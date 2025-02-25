from libs.chatgpt import ask_to_chatgpt
from libs.cli import userinput_argument, get_context_options
import click


prompt_base="""
Actua como un experto profesor en ingles y corrige el siguiente texto encerrado en triple acento grave ```{text}```. este texto puede estar en ingles o español deberas corregir si existe algun error
y tambien puedes dar sugeriencias para mejorarlo.
Devolveras un resumen con los errores y sugerencias.
"""


@click.command(help='Profesor de inglés')
@click.pass_context
@userinput_argument()
def english(ctx, userinput):
    model, temperature = get_context_options(ctx)
    prompt = prompt_base.format(text=userinput)
    ask_to_chatgpt(userinput, prompt=prompt, model=model, temperature=temperature)
