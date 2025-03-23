import click
from recorder import record


@click.group(help='Herramientas de audio para terminal bash')
def cli():
    pass

cli.add_command(record)

cli()