import os
import click
from pathlib import Path

IGNORE_DIRECTORIES = ["node_modules", "venv", ".venv", "__pycache__"]


def get_file_type(file_name):
    return os.path.splitext(file_name)[1][1:] or "txt"


def source_code_list(src_files):
    content = []
    for src in src_files:
        content.append(f"- {src}")
    return "\n".join(content)


def source_code_content(src_files):
    content = []
    for src in src_files:
        file_ext = get_file_type(src)
        content_code = Path(src).read_text()
        content.append(f"**{src}**\n\n```{file_ext}\n{content_code}\n```")
    return "\n".join(content)


def filter_source_code_files(src_files):
    filtered = []
    for file in src_files:
        if not os.path.isfile(file):
            continue
        if any(directory in file for directory in IGNORE_DIRECTORIES):
            continue
        filtered.append(file)
    return filtered


def summary_source_code(src_files):
    summary = []
    source_list = source_code_list(src_files)
    source_content = source_code_content(src_files)
    summary.append("# Code Summary\n")
    summary.append("## File list\n")
    summary.append(source_list)
    summary.append("\n ## File content")
    summary.append(source_content)
    return "\n".join(summary)


def get_directory_files(directory):
    src_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            src_files.append(os.path.join(root, file))
    return src_files


@click.command(help="Resume codigo fuente en formato markdown")
@click.option("-o", "--output", default=None, help="Output file in markdown format")
@click.argument("src_files", nargs=-1)
def summarize_sources(output, src_files):
    src_files_filtered = filter_source_code_files(src_files)
    summary = summary_source_code(src_files_filtered)
    if output:
        Path(f"{output}.md").write_text(summary)
    else:
        print(summary)


@click.command(help="Resume codigo fuente de un directorio en formato markdown")
@click.option("-o", "--output", default=None, help="Output file in markdown format")
@click.argument("directory")
def summarize_dir(output, directory):
    src_files = get_directory_files(directory)
    src_files_filtered = filter_source_code_files(src_files)
    summary = summary_source_code(src_files_filtered)
    if output:
        Path(f"{output}.md").write_text(summary)
    else:
        print(summary)