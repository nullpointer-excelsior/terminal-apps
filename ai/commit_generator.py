from libs.chatgpt import ask_simple_question_to_chatgpt
from libs.cli import get_context_options
import subprocess
import click


prompt="""
Crea un commit semantico corto en ingles en base al siguiente diff: {diff}
"""

def get_diff():
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
    return subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True)

@click.command(help='Generador de commit')
@click.pass_context
def commit_generator(ctx):
    model, temperature = get_context_options(ctx)
    try:
        diff = get_diff()
        prompt_diff = prompt.format(diff=diff)
        ask_simple_question_to_chatgpt(prompt_diff, model=model, temperature=temperature)
    except subprocess.CalledProcessError:
        pass
