import sys
import click
from libs.chatgpt import chatgpt_models
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def get_argument_or_stdin(ctx, param, value):
    if value is not None:
        return value
    if not sys.stdin.isatty():
        return click.get_text_stream("stdin").read()
    raise click.BadArgumentUsage("Text can't be empty.")


def userinput_argument():
    def decorator(wrapped_fn):
        return click.argument('userinput', callback=get_argument_or_stdin, required=False)(wrapped_fn)
    return decorator


def model_option(model='gpt4om'):
    model_choices= list(chatgpt_models.keys())
    def decorator(wrapped_function):
        return click.option(
            '--model', '-m',
            type=click.Choice(model_choices, case_sensitive=False),
            default=model,
            help='Indica el modelo AI a usar'
        )(wrapped_function)
    return decorator


def temperature_option(temperature=0):
    def decorator(wrapped_function):
        return click.option(
            '--temperature', '-t',
            type=float, 
            help='Temperatura del modelo. Entre 0 y 2. Los valores más altos como 0.8 harán que la salida sea más aleatoria, mientras que los valores más bajos como 0.2 la harán más enfocada y determinista.', 
            default=temperature
        )(wrapped_function)
    return decorator


def copy_option():
    def decorator(wrapper_fn):
        return click.option('-c', '--copy', is_flag=True, help='Copia la respuesta al portapapeles')(wrapper_fn)
    return decorator


def markdown_option():
    def decorator(wrapper_fn):
        return click.option('-md', '--markdown', is_flag=True, help='Respuesta en Markdown')(wrapper_fn)
    return decorator


def get_context_options(ctx):
    model = ctx.obj["model"]
    temperature = ctx.obj["temperature"]
    return model, temperature


def print_markdown(content):
    console.print(Markdown(content))


def process_markdown(markdown: bool, with_markdown, no_markdown):
    if markdown:
        click.echo(click.style('🔄 Waiting for the complete answer from OpenAI...', fg='cyan', bold=True, underline=True))
        print_markdown(with_markdown())
    else:
        no_markdown()
