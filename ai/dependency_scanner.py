"""
Dependency scanner using LangGraph.

Analyzes a source file and recursively discovers all internal file
dependencies by delegating to an LLM that reads the project tree.
"""

import fnmatch
import os
import click
from pathlib import Path
from operator import add, or_
from typing import Annotated, FrozenSet, List, Optional, Set, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph


# ---------------------------------------------------------------------------
# State schemas
# ---------------------------------------------------------------------------

class InputState(TypedDict):
    filename: str


class OutputState(TypedDict):
    file_dependencies: List[str]


class DependencyState(TypedDict):
    """Internal graph state threaded through every node."""

    # Files still waiting to be analysed (treated as a FIFO queue).
    file_queue: List[str]
    # Files that have already been processed (reducer: union of sets).
    processed_files: Annotated[Set[str], or_]
    # Every dependency discovered so far (reducer: list concatenation).
    all_dependencies: Annotated[List[str], add]
    project_root: str
    tree_view: str


# ---------------------------------------------------------------------------
# LLM output schema
# ---------------------------------------------------------------------------

class FileDependencies(TypedDict):
    file_dependencies: List[str]


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def read_file(file_path: str) -> Optional[str]:
    """Return the UTF-8 text of *file_path*, or ``None`` on any error."""
    path = Path(file_path)
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, UnicodeDecodeError):
        return None


def parse_gitignore(directory: str) -> FrozenSet[str]:
    """
    Parse ``<directory>/.gitignore`` and return its patterns as a frozenset.

    Lines that are empty or start with ``#`` are skipped.
    Trailing whitespace and leading ``/`` anchors are stripped so that
    ``fnmatch`` can match plain file/directory names without path prefixes.
    """
    gitignore_path = Path(directory) / ".gitignore"
    if not gitignore_path.is_file():
        return frozenset()

    patterns: Set[str] = set()
    for raw_line in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # Skip blank lines and comments.
        if not line or line.startswith("#"):
            continue
        # Strip a leading slash so patterns like "/dist" match "dist" too.
        patterns.add(line.lstrip("/"))

    return frozenset(patterns)


def _is_ignored(name: str, rel_path: str, patterns: FrozenSet[str]) -> bool:
    """
    Return ``True`` if *name* or its relative path matches any gitignore pattern.

    Checks both the bare name (e.g. ``node_modules``) and the path relative to
    the project root (e.g. ``src/generated/foo.py``) so that directory globs
    and path-specific patterns both work correctly.
    """
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def generate_tree(directory: str) -> str:
    """
    Return an ASCII directory tree rooted at *directory*.

    Entries that match patterns declared in ``<directory>/.gitignore`` are
    silently excluded, keeping the tree relevant for source-code analysis.
    The ``.git`` folder is always excluded regardless of gitignore contents.
    """
    if not os.path.isdir(directory):
        return "Directory not found."

    ignored_patterns = parse_gitignore(directory)
    # Always hide the VCS metadata folder.
    always_ignore: FrozenSet[str] = frozenset({".git"})
    all_patterns = ignored_patterns | always_ignore

    root_abs = os.path.abspath(directory)
    lines: List[str] = [os.path.basename(root_abs) or directory]

    def _recurse(current_abs: str, prefix: str = "") -> None:
        try:
            raw_items = sorted(os.listdir(current_abs))
        except PermissionError:
            return

        # Filter out ignored entries before deciding which is "last".
        visible_items = [
            item for item in raw_items
            if not _is_ignored(
                item,
                os.path.relpath(os.path.join(current_abs, item), root_abs),
                all_patterns,
            )
        ]

        for idx, item in enumerate(visible_items):
            abs_path = os.path.join(current_abs, item)
            is_last = idx == len(visible_items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{item}")
            if os.path.isdir(abs_path):
                extension = "    " if is_last else "│   "
                _recurse(abs_path, prefix + extension)

    _recurse(root_abs)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM chain factory
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a technical assistant specialised in code analysis. "
    "Identify internal file dependencies from the provided source code. "
    "Use the directory tree to resolve paths. "
    "Return only files that actually exist in the tree."
)

_HUMAN_TEMPLATE = (
    "Project Tree:\n{tree}\n\n"
    "Current File Path: {filename}\n\n"
    "Content:\n{content}"
)


def build_dependency_chain(model: str):
    """Return a runnable chain: dict → FileDependencies."""
    llm = init_chat_model(model)
    prompt = ChatPromptTemplate.from_messages(
        [("system", _SYSTEM_PROMPT), ("human", _HUMAN_TEMPLATE)]
    )
    return prompt | llm.with_structured_output(FileDependencies)


# ---------------------------------------------------------------------------
# Graph node factories
# ---------------------------------------------------------------------------

def make_init_node(project_root: str = "."):
    """Return the initialisation node (InputState → DependencyState)."""

    def init_node(state: InputState) -> DependencyState:
        return {
            "file_queue": [state["filename"]],
            "processed_files": set(),
            "all_dependencies": [],
            "project_root": project_root,
            "tree_view": generate_tree(project_root),
        }

    return init_node


def make_analyze_node(dependency_chain):
    """Return the analysis node that pops one file from the queue."""

    def analyze_node(state: DependencyState) -> DependencyState:
        queue = list(state["file_queue"])
        if not queue:
            return {}

        current_file = queue.pop(0)

        # Skip files we have already visited.
        if current_file in state["processed_files"]:
            return {"file_queue": queue}

        content = read_file(current_file)
        if content is None:
            return {
                "processed_files": {current_file},
                "file_queue": queue,
            }

        result: FileDependencies = dependency_chain.invoke(
            {
                "tree": state["tree_view"],
                "filename": current_file,
                "content": content,
            }
        )

        found_deps: List[str] = result.get("file_dependencies", [])
        already_seen = state["processed_files"] | set(queue)
        new_files = [dep for dep in found_deps if dep not in already_seen]

        return {
            "file_queue": queue + new_files,
            "processed_files": {current_file},
            "all_dependencies": found_deps,
        }

    return analyze_node


def output_node(state: DependencyState) -> OutputState:
    """Deduplicate and sort all discovered dependencies."""
    return {"file_dependencies": sorted(set(state["all_dependencies"]))}


def has_pending_files(state: DependencyState) -> str:
    """Routing function: keep analysing while the queue is non-empty."""
    return "analyze" if state["file_queue"] else "output"


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_agent(model: str):
    """Compile and return the LangGraph dependency-scanning agent."""
    dependency_chain = build_dependency_chain(model)

    workflow = StateGraph(
        state_schema=DependencyState,
        input_schema=InputState,
        output_schema=OutputState,
    )

    workflow.add_node("init", make_init_node())
    workflow.add_node("analyze", make_analyze_node(dependency_chain))
    workflow.add_node("output", output_node)

    workflow.add_edge(START, "init")
    workflow.add_edge("init", "analyze")
    # After each analysis step, decide whether to loop or finish.
    workflow.add_conditional_edges("analyze", has_pending_files, ["analyze", "output"])
    workflow.add_edge("output", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command("scan-deps")
@click.argument("filename", type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format.")
@click.option(
    "--plain/--no-plain",
    default=True,
    help="Output results as a plain list (default) or formatted.",
)
@click.pass_context
def scan_deps(ctx: click.Context, filename: str, output_json: bool, plain: bool) -> None:
    """Scan a file for internal dependencies using LangGraph."""
    context = ctx.obj["context"]

    agent = build_agent(context.model)
    result: OutputState = agent.invoke({"filename": filename})
    dependencies = result.get("file_dependencies", [])

    if output_json:
        import json as json_lib

        click.echo(json_lib.dumps({"root": filename, "file_dependencies": dependencies}))
    elif plain:
        click.echo(filename)
        for dep in dependencies:
            click.echo(dep)
            
    else:
        context.display({"file_dependencies": dependencies})
