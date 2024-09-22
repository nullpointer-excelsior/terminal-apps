import click
from project_scanner import proyect_scanner

@click.group(help='Herramientas terminal bash')
def cli():
    pass

cli.add_command(proyect_scanner)

cli()