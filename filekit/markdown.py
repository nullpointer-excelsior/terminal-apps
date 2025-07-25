import click
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
import os
from libs.commands import FzfCommand


IGNORE_DIRECTORIES = ["node_modules", "venv", ".venv", "__pycache__"]


console = Console()


def get_file_type(file_name):
    return os.path.splitext(file_name)[1][1:] or "txt"


def source_code_list(src_files):
    content = []
    for src in src_files:
        content.append(f"- {src}")
    return "\n".join(content)


def build_codeblock(path, content, ext):
    ext = get_file_type(path)
    content = Path(path).read_text()
    return f"**{path}:**\n```{ext}\n{content}\n```\n"


def source_code_content(src_files):
    content = []
    for src in src_files:
        file_ext = get_file_type(src)
        content_code = Path(src).read_text()
        content.append(f"**{src}:**\n```{file_ext}\n{content_code}\n```\n")
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


def get_directory_files(directory):
    src_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            src_files.append(os.path.join(root, file))
    return src_files


@click.command(help="Muestra archivos markdown con colores")
@click.argument('input_file', type=click.File('r'), required=False)
def mdcat(input_file):
    if input_file is None:
        input_file = click.get_text_stream('stdin')
    console.print(Markdown(input_file.read()))


@click.command(help="Resume codigo fuente en formato markdown")
@click.argument("src_filess", nargs=-1)
def mdcode_sources(src_files):
    src_files_filtered = filter_source_code_files(src_files)
    summary = source_code_content(src_files_filtered)
    print(summary)


@click.command(help="Resume codigo fuente de un directorio en formato markdown")
@click.argument("directory")
def mdcode_directory(directory):
    src_files = get_directory_files(directory)
    src_files_filtered = filter_source_code_files(src_files)
    summary = source_code_content(src_files_filtered)
    print(summary)


@click.command(help="Muestra archivos markdown")
@click.argument('pathfile', type=click.Path(exists=True), required=False)
def mdcode_file(pathfile):
    file = Path(pathfile)
    ext = file.suffix.lstrip('.')
    content = file.read_text()
    codeblock = f"**{pathfile}:**\n```{ext}\n{content}\n```\n"
    print(codeblock)


@click.command(help="Muestra archivos markdown con fzf")
def mdcode_select():
    fzf = FzfCommand([
        "--preview-window=right:70%:wrap", 
        "--preview", "bat --style=numbers --color=always {}"
    ])
    pathfile = fzf.select_file('.')
    if pathfile is None:
        return
    file = Path(pathfile)
    ext = file.suffix.lstrip('.')
    content = file.read_text()
    codeblock = f"**{pathfile}:**\n```{ext}\n{content}\n```\n"
    print(codeblock)