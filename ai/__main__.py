import click
from grammar import grammar
from developer import developer
from question import question
from translate import translate
from summarize import summarize
from english import english
from libs.cli import model_option, temperature_option
from test import test
from screenshot import screenshot


@click.group(help='Herramientas de AI para terminal bash')
@model_option()
@temperature_option()
@click.pass_context
def cli(ctx, model, temperature):
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['temperature'] = temperature

cli.add_command(question)
cli.add_command(grammar)
cli.add_command(translate)
cli.add_command(developer)
cli.add_command(english)
cli.add_command(summarize)
cli.add_command(screenshot)
cli.add_command(test)

cli()