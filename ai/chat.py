from libs.chatgpt import chat_with_chatgpt
from libs.cli import get_context_options, markdown_option, process_markdown, print_markdown
from libs.system import command_exists
from libs.config import config
import click
import re
import subprocess
from pathlib import Path

default_system_prompt = """Eres un útil asistente que resolverá todas las dudas del usuario y responderás de forma directa y sin explicaciones, a menos que el usuario te lo indique."""


def select_template() -> str:
    template_directory = f"{config.ai_prompt_resources}/templates"
    process = subprocess.Popen(
        ['fzf'], cwd=template_directory, stdout=subprocess.PIPE, text=True
    )
    selected_file, _ = process.communicate()
    if not selected_file:
        return None
    return f"{template_directory}/{selected_file.strip()}"


def create_prompt():
    # verify commands required
    command = 'fzf'
    if not command_exists(command):
        click.echo(click.style(f"\n\tx Command ${command} doesn't exits", fg="red"))
        click.echo(click.style("\t* Using default prompt"))
        return default_system_prompt
    # select template 
    template = select_template()
    if template is None:
        return default_system_prompt
    # read template content and generate prompt
    content = Path(template).read_text()
    variables = set(re.findall(r"\{([^}]+)\}", content))
    for var in variables:
        value = input(
            f"\nEnter template param for {click.style(f'${var}', fg='yellow')}: "
        ).strip()
        if value:
            content = content.replace(f"{{{var}}}", value)
    return content


@click.command(help="Chatgpt session in terminal")
@click.pass_context
@click.option("-p", "--prompt", is_flag=True, help="Select a prompt from resources")
@markdown_option()
def chat(ctx, prompt, markdown):
    model, temperature = get_context_options(ctx)

    messages = [
        {
            "role": "system",
            "content": create_prompt() if prompt else default_system_prompt,
        },
    ]

    def stream_chat():
        response = chat_with_chatgpt(messages, model, temperature)
        messages.append({"role": "system", "content": response})

    def markdown_chat():
        response = chat_with_chatgpt(messages, model, temperature, stream=False)
        messages.append({"role": "system", "content": response})
        return response
    
    click.echo(click.style("\nStarting chat...\n", fg="green"))

    while True:
        chat_user_prompt = input(click.style("🦁 > ", fg="green"))

        if chat_user_prompt == "exit":
            break
        
        print(click.style("🤖 > ", fg="green"), end="", flush=True)

        if chat_user_prompt.startswith('-md'):
            messages.append({"role": "user", "content": chat_user_prompt.split('-md')[1]})
            print_markdown(markdown_chat())
            continue
        
        messages.append({"role": "user", "content": chat_user_prompt})

        process_markdown(
            markdown,
            lambda: markdown_chat(),
            lambda: stream_chat()
        )
        
