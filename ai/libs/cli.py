import sys
import click
from libs.llm import DEFAULT_MODEL, MODEL_ALIASES


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


def model_option(model=DEFAULT_MODEL):
    help_text = (
        f"AI model to use. Format: 'provider:model' or use an alias. "
        f"Aliases: {', '.join(MODEL_ALIASES.keys())}. "
        f"Default: {DEFAULT_MODEL}"
    )
    def decorator(wrapped_function):
        return click.option(
            '--model', '-m',
            type=str,
            default=model,
            help=help_text
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
    return model
