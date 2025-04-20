import click
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

console = Console()

@click.command(help="Muestra archivos markdown con colores")
@click.argument("src_files", nargs=-1)
def mdcat(src_files):
    for src in src_files:
        content = Path(src).read_text()
        console.print(Markdown(content))
