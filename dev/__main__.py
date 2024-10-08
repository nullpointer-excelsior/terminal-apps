import click
from code_scanner import code_scanner

@click.group(help='Herramientas terminal bash')
def cli():
    pass

cli.add_command(code_scanner)

cli()