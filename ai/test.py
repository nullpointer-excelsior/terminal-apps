from libs.chatgpt import ask_to_chatgpt
from libs.cli import get_context_options, userinput_argument
import click


prompt="""
Eres un útil asistente. Responderás de forma directa y sin explicaciones a menos que te indique lo contrario.
"""
def cb(ctx, param, value):
    print(f"{param}: value:{value}")
    import sys
    if not value and not sys.stdin.isatty():
        value = click.get_text_stream("stdin").read()
    return value

@click.command(help='Testing command')
@click.pass_context
@click.argument('userinput', callback=cb, required=False)
def test(ctx, userinput):
    print(f'useripunt:{userinput}')
    model, temperature = get_context_options(ctx)
    print(f"m:{model}, t:{temperature}")

    # o = click.get_text_stream('stdout').read()
    # print(f"o:{o}")
    
