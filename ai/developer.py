from libs.session import WithSessionStrategy, WithoutSessionStrategy
from libs.chatgpt import ask_simple_question_to_chatgpt, chat_with_chatgpt
from libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from libs.display import HighlightedCodeDisplayStrategy, MarkdowDisplayStrategy
import click
import subprocess
import pyperclip
import os

dev_prompt="""
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""

userinput_with_files="""
Tengo los siguientes archivos:
{content}
Responde lo siguiente:
{input}
"""

commit_generator_prompt="""
Crea un mensaje de commit semántico corto en inglés basado en los detalles de la salida de `git diff --cached` dado por el usuario
"""


def create_context_files(file_paths):
    markdown_content = "## Content files\n"
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        markdown_content += f"**{file_name}**\n"
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                extension = os.path.splitext(file_name)[1][1:]
                markdown_content += f"```{extension}\n{content}\n```\n"
        except Exception as e:
            markdown_content += f"Error reading file: {e}\n"
    return markdown_content


def userinput_factory(userinput, files):
    if files:
        content = create_context_files(files)
        return userinput_with_files.format(content=content, input=userinput)
    return userinput


def display_strategy(markdown):
    return MarkdowDisplayStrategy() if markdown else HighlightedCodeDisplayStrategy()


@click.command(help='Desarrollador experto')
@click.pass_context
@userinput_argument()
@markdown_option()
@click.option('-ns', '--no-session', is_flag=True, help="Consulta sin sesión.")
@click.option('-f', '--file', multiple=True, help="Archivo como contexto")
def dev(ctx, userinput, markdown, no_session, file):

    model, temperature = get_context_options(ctx)
    userinput_prompt = userinput_factory(userinput, file)
    llmcall = display_strategy(markdown)

    if no_session:
        session_strategy = WithoutSessionStrategy(
            userinput=userinput_prompt,
            systemprompt=dev_prompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall
        )
    else: 
        session_strategy = WithSessionStrategy(
            userinput=userinput_prompt,
            systemprompt=dev_prompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall,
            assistant='dev'
        ) 

    session_strategy.request()


def execute_git_diff():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
        return subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        pass

def execute_git_commit(message:str):
    try:
        return subprocess.run(["git", "commit","-m", message.strip()], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError as e:
        print(str(e))
        pass

@click.command(help='Generador de commit')
@click.pass_context
@copy_option()
def commit_generator(ctx, copy):
    model, temperature = get_context_options(ctx)
    diff = execute_git_diff()
    messages = [
        {"role": "system", "content": "Crea un mensaje de commit semántico corto en inglés basado en los detalles de la salida de `git diff --cached` dado por el usuario. Quiero solo el mensaje en texto, No agregues caracteres como '```'"},
        {"role": "user", "content": f"Genera el commit message para el siguiente diff: {diff}"}
    ]

    print("\033[33m")
    response = chat_with_chatgpt(messages, model=model, temperature=temperature)
    print("\033[0m")

    while not click.confirm(click.style('Do you want to confirm this message commit?', fg='green')):
        messages.append({"role": "user", "content": f"Este mensaje no me convence: {response} Cambialo porfavor"})
        print("\033[33m")
        response = chat_with_chatgpt(messages, model=model, temperature=temperature)
        print("\033[0m")

    stdout = execute_git_commit(response)
    print(f"\n{stdout}")
