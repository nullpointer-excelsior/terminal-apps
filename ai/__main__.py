import click
from text import grammar, translate, question, summarize, transcribe
from developer import dev, commit_generator
from english import english
from screenshot import screenshot
from chat import chat
from libs.cli import model_option, temperature_option


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
cli.add_command(dev)
cli.add_command(english)
cli.add_command(summarize)
cli.add_command(screenshot)
cli.add_command(commit_generator)
cli.add_command(chat)
cli.add_command(transcribe)

cli()