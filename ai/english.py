from libs.chatgpt import ask_to_chatgpt
from libs.cli import userinput_argument, get_context_options
import click


prompt_base="""
Actúa como un experto profesor de inglés y corrige el siguiente texto encerrado en triple acento grave ```{text}```. Este texto puede estar en inglés o español; deberás corregir si existe algún error 
y también puedes dar sugerencias para mejorarlo.
devolverás un resumen con los errores y sugerencias.
"""


@click.command(help='Profesor de inglés')
@click.pass_context
@userinput_argument()
def english(ctx, userinput):
    model, temperature = get_context_options(ctx)
    prompt = prompt_base.format(text=userinput)
    ask_to_chatgpt(userinput, prompt=prompt, model=model, temperature=temperature)
