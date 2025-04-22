from libs.chatgpt import ask_simple_question_to_chatgpt, ask_to_chatgpt_no_stream, get_stream_completion
from libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from libs.display import display_markdown, process_markdown, display_highlighted_code
import click
import subprocess
import pyperclip


dev_prompt="""
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""

commit_generator_prompt="""
Crea un mensaje de commit semántico corto en inglés basado en el siguiente diff:
{diff}
"""


@click.command(help='Desarrollador experto')
@click.pass_context
@userinput_argument()
@markdown_option()
def dev(ctx, userinput, markdown):
    model, temperature = get_context_options(ctx)
    messages = [
        {"role": "system", "content": dev_prompt},
        {"role": "user", "content": userinput}
    ]
    process_markdown(
        markdown, 
        lambda: ask_to_chatgpt_no_stream(userinput, prompt=dev_prompt, model=model, temperature=temperature),
        lambda: display_highlighted_code(lambda : get_stream_completion(messages, model=model, temperature=temperature))
    )


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