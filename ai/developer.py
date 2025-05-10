from libs.session import WithSessionStrategy, WithoutSessionStrategy
from libs.chatgpt import ask_simple_question_to_chatgpt
from libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from libs.display import HighlightedCodeDisplayStrategy, MarkdowDisplayStrategy
import click
import subprocess
import pyperclip
import os

dev_prompt="""
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""

dev_prompt_with_context_files="""
Eres un útil asistente y experto desarrollador y arquitecto de software. 

## INSTRUCIONES
- Responderás de forma directa y sin explicaciones.
- Considera los siguientes archivos: {files} los cuales tienen el siguiente contenido:
{content}
"""

commit_generator_prompt="""
Crea un mensaje de commit semántico corto en inglés basado en el siguiente diff:
{diff}
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


def system_prompt_factory(files):
    if files:
        content = create_context_files(files)
        return dev_prompt_with_context_files.format(files=', '.join(files), content=content)
    return dev_prompt


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
    systemprompt = system_prompt_factory(file)
    llmcall = display_strategy(markdown)

    if no_session:
        session_strategy = WithoutSessionStrategy(
            userinput=userinput,
            systemprompt=systemprompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall
        )
    else: 
        session_strategy = WithSessionStrategy(
            userinput=userinput,
            systemprompt=systemprompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall,
            assistant='dev'
        ) 

    session_strategy.request()


@click.command(help='Generador de commit')
@click.pass_context
@copy_option()
def commit_generator(ctx, copy):
    model, temperature = get_context_options(ctx)
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
        diff = subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True)
        prompt_diff = commit_generator_prompt.format(diff=diff)
        response = ask_simple_question_to_chatgpt(prompt_diff, model=model, temperature=temperature)
        if copy:
            pyperclip.copy(response)
    except subprocess.CalledProcessError:
        pass
