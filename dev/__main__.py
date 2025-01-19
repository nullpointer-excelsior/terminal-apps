import click
from sumarize_source_code import summarize_sources, summarize_dir

@click.group(help='Herramientas terminal bash')
def cli():
    pass

cli.add_command(summarize_sources)
cli.add_command(summarize_dir)

cli()