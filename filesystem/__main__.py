import click
from filesystem import mdcat

@click.group(help='Herramientas de filesystem para terminal bash')
def cli():
    pass

cli.add_command(mdcat)

cli()