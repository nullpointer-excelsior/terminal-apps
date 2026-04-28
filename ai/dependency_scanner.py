import os
import click
from typing import Annotated, List, Set, TypedDict, Optional
from pathlib import Path
from operator import add, or_
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START


class OutputDependencies(TypedDict):
    file_dependencies: List[str]


class InputState(TypedDict):
    filename: str


class OutputState(TypedDict):
    file_dependencies: List[str]


class DependencyState(TypedDict):
    # Queue of files to be analyzed
    file_queue: List[str]
    # Set of files already visited to prevent circular dependency loops
    processed_files: Annotated[Set[str], or_]
    # Aggregated list of all discovered dependencies
    all_dependencies: Annotated[List[str], add]
    project_root: str
    tree_view: str


def read_file_content(file_path: str) -> Optional[str]:
    path = Path(file_path)
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, UnicodeDecodeError):
        return None


def generate_tree(directory: str) -> str:
    output = []
    def build_tree(current_path: str, prefix: str = ""):
        try:
            items = sorted(os.listdir(current_path))
        except PermissionError:
            return
        for index, item in enumerate(items):
            path = os.path.join(current_path, item)
            is_last = (index == len(items) - 1)
            connector = "└── " if is_last else "├── "
            output.append(f"{prefix}{connector}{item}")
            if os.path.isdir(path):
                build_tree(path, prefix + ("    " if is_last else "│   "))
    
    if os.path.isdir(directory):
        output.append(os.path.basename(os.path.abspath(directory)) or directory)
        build_tree(directory)
        return "\n".join(output)
    return "Directory not found."


# Initialize LLM with structured output
def build_agent(model: str):
    llm = init_chat_model(model)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical assistant specialized in code analysis. "
                   "Identify internal file dependencies from the provided source code. "
                   "Use the directory tree to resolve paths. Return only existing files from the tree."),
        ("human", "Project Tree:\n{tree}\n\nCurrent File Path: {filename}\n\nContent:\n{content}")
    ])
    dependency_analyzer = prompt | llm.with_structured_output(OutputDependencies)

    def init_analyzer_node(state: InputState) -> DependencyState:
        return {
            "file_queue": [state["filename"]],
            "processed_files": set(),
            "all_dependencies": [],
            "project_root": ".",
            "tree_view": generate_tree(".")
        }

    def analyze_file_node(state: DependencyState) -> DependencyState:
        queue = list(state["file_queue"])
        if not queue:
            return {}

        current_file = queue.pop(0)
        
        # Skip if already processed
        if current_file in state["processed_files"]:
            return {"file_queue": queue}

        content = read_file_content(current_file)
        if not content:
            return {
                "processed_files": {current_file},
                "file_queue": queue
            }

        result = dependency_analyzer.invoke({
            "tree": state["tree_view"],
            "filename": current_file,
            "content": content
        })

        found_deps = result.get("file_dependencies", [])
        
        # Identify new files for the queue
        new_to_queue = [
            dep for dep in found_deps 
            if dep not in state["processed_files"] and dep not in queue
        ]

        return {
            "file_queue": queue + new_to_queue,
            "processed_files": {current_file},
            "all_dependencies": found_deps
        }

    def output_node(state: DependencyState) -> OutputState:
        return {"file_dependencies": sorted(list(set(state["all_dependencies"])))}

    def router_logic(state: DependencyState):
        return "analyze" if state["file_queue"] else END

    workflow = StateGraph(state_schema=DependencyState, input_schema=InputState, output_schema=OutputState)
    workflow.add_node("init", init_analyzer_node)
    workflow.add_node("analyze", analyze_file_node)
    workflow.add_node("output", output_node)
    workflow.add_edge(START, "init")
    workflow.add_edge("init", "analyze")
    workflow.add_edge("analyze", "output")
    workflow.add_conditional_edges("analyze", router_logic)
    workflow.add_edge("output", END)
    return workflow.compile()


@click.command("scan-deps")
@click.argument("filename", type=click.Path(exists=True))
@click.pass_context
def scan_deps(ctx, filename):
    """Scan a file for dependencies using LangGraph."""
    context = ctx.obj["context"]
    model = context.model
    agent = build_agent(model)
    result = agent.invoke({"filename": filename})
    # Extract file_dependencies from the OutputState dict
    deps_list = result.get("file_dependencies", [])
    context.display({"file_dependencies": deps_list})
