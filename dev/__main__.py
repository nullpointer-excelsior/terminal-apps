import click
from sumarize_source_code import summarize_sources

@click.group(help='Herramientas terminal bash')
def cli():
    pass

cli.add_command(summarize_sources)

cli()