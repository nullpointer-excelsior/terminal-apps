from .developer import dev, commit_generator
from .english import english
from .libs.cli import model_option
from .screenshot import screenshot
from .text import grammar, translate, question, summarize, transcribe
import click


@click.group(help='Herramientas de AI para terminal bash')
@model_option()
@click.pass_context
def cli(ctx, model):
    ctx.ensure_object(dict)
    ctx.obj['model'] = model

cli.add_command(question)
cli.add_command(grammar)
cli.add_command(translate)
cli.add_command(dev)
cli.add_command(english)
cli.add_command(summarize)
cli.add_command(screenshot)
cli.add_command(commit_generator)
cli.add_command(transcribe)

if __name__ == "__main__":
    cli()

