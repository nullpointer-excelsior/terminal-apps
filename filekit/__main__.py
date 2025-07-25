import click
from markdown import mdcat, mdcode_file, mdcode_sources, mdcode_directory, mdcode_select


@click.group(help='Herramientas de manipulacion de archivos para terminal bash')
def cli():
    pass

cli.add_command(mdcat)
cli.add_command(mdcode_file)
cli.add_command(mdcode_sources)
cli.add_command(mdcode_directory)
cli.add_command(mdcode_select)

cli()