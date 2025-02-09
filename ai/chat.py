from libs.chatgpt import chat_with_chatgpt
from libs.cli import get_context_options
import click

chat_system_prompt = """Eres un útil asistente que resolverá todas las dudas del usuario y responderás de forma directa y sin explicaciones, a menos que el usuario te lo indique."""

@click.command(help='Chatgpt session in terminal')
@click.pass_context
def chat(ctx):
    model, temperature = get_context_options(ctx)
    messages = [
        {"role": "system", "content": chat_system_prompt},
    ]
    click.echo(click.style('\nStarting chat...\n', fg='green'))
    while True:
        chat_user_prompt = input(click.style("🦁 > ", fg='green'))
        if chat_user_prompt == "exit":
            break
        messages.append({"role": "user", "content": chat_user_prompt })
        print(click.style("🤖 > ", fg='green'), end="", flush=True)
        response = chat_with_chatgpt(messages, model, temperature)
        messages.append({"role": "system", "content": response })
        