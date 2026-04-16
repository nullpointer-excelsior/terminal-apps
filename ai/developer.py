from libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from libs.display import HighlightedCodeDisplayStrategy, MarkdownDisplayStrategy
from libs.llm import invoke_llm, invoke_llm_stream
from libs.config import config
import click
import subprocess
import pyperclip
import os

dev_prompt = """
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""

userinput_with_files = """
Tengo los siguientes archivos:
{content}
Responde lo siguiente:
{input}
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
    return MarkdownDisplayStrategy() if markdown else HighlightedCodeDisplayStrategy()


@click.command(help='Desarrollador experto')
@click.pass_context
@userinput_argument()
@markdown_option()
@click.option('-f', '--file', multiple=True, help="Archivo como contexto")
def dev(ctx, userinput, markdown, file):
    model = get_context_options(ctx)
    userinput_prompt = userinput_factory(userinput, file)
    llmcall = display_strategy(markdown)
    llmcall.request(userinput_prompt, model=model, system_message=dev_prompt)


def execute_git_diff():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
        return subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return None


def execute_git_commit(message: str):
    try:
        return subprocess.run(["git", "commit", "-m", message.strip()], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError as e:
        print(str(e))
        return None


@click.command(help='Generador de commit')
@click.pass_context
@copy_option()
def commit_generator(ctx, copy):
    model = get_context_options(ctx)
    diff = execute_git_diff()
    if not diff:
        click.echo("No staged changes found or not a git repository.")
        return
    
    system_message = "Crea un mensaje de commit semántico corto en inglés basado en los detalles de la salida de `git diff --cached` dado por el usuario. Quiero solo el mensaje en texto, No agregues caracteres como '```'"
    prompt = f"Genera el commit message para el siguiente diff: {diff}"

    print("\033[33m", end="", flush=True)
    response = ""
    for chunk in invoke_llm_stream(prompt, model=model, system_message=system_message):
        print(chunk, end="", flush=True)
        response += chunk
    print("\033[0m")

    while not click.confirm(click.style('Do you want to confirm this message commit?', fg='green')):
        feedback = click.prompt("What should be changed?", default="Change it please")
        prompt = f"Este mensaje no me convence: {response}. Feedback: {feedback}. Genera uno nuevo para este diff: {diff}"
        print("\033[33m", end="", flush=True)
        response = ""
        for chunk in invoke_llm_stream(prompt, model=model, system_message=system_message):
            print(chunk, end="", flush=True)
            response += chunk
        print("\033[0m")

    stdout = execute_git_commit(response)
    if stdout:
        print(f"\n{stdout}")
    if copy:
        pyperclip.copy(response)

