import click
import pyperclip
from libs.cli import copy_option, userinput_argument, get_context_options
from libs.chatgpt import ask_to_chatgpt, transcribe_audio

grammar_prompt = """
Corrije gramaticalmente el texto encerrado en triple acento grave. ```{userinput}```, no debes devolver el texto con el triple acento grave.
"""

translate_prompt = """
Traduce el siguiente texto: "{text}"
- Si el texto esta en inglés traducelo al español
- Si el texto esta en español traducelo al inglés.
- Si el texto que debe ser traducido al inglés contiene números, deberás escribirlos con palabras seguidos del número encerrado entre paréntesis.
"""

question_prompt="""
Eres un útil asistente. Responderás de forma directa y sin explicaciones a menos que te indique lo contrario.
"""


@click.command(help='Corrije la gramatica de un texto')
@click.pass_context
@userinput_argument()
@copy_option()
def grammar(ctx, userinput, copy):
    model, temperature = get_context_options(ctx)
    prompt = grammar_prompt.format(userinput=userinput)
    response = ask_to_chatgpt(userinput, prompt=prompt, model=model, temperature=temperature)
    if copy:
        pyperclip.copy(response)


@click.command(help='Traductor de Inglés - Español')
@click.pass_context
@userinput_argument()
@copy_option()
def translate(ctx, userinput, copy):
    prompt = translate_prompt.format(text=userinput)
    model, temperature = get_context_options(ctx)
    response = ask_to_chatgpt(userinput, prompt=prompt, model=model, temperature=temperature)
    if copy:
        pyperclip.copy(response) 


@click.command(help='Pregunta a ChatGPT')
@click.pass_context
@userinput_argument()
def question(ctx, userinput):
    model, temperature = get_context_options(ctx)
    ask_to_chatgpt(userinput, prompt=question_prompt, model=model, temperature=temperature)


def get_instructions(words, sentences, tone, audience, style, markdown, translate):
    instructions = []
    if words:
        instructions.append(f' - El resumen no debe tener más de {words} palabras.')
    if sentences:
        instructions.append(f' - El resumen no debe tener más de {sentences} oraciones.')
    if style:
        instructions.append(f' - El resumen debe tener un estilo {style}.')
    if audience:
        instructions.append(f' - El resumen debe apuntar a una audiencia {audience}.')
    if tone:
        instructions.append(f' - El resumen debe tener un tono {tone}.')
    if markdown:
        instructions.append(' - El resumen debe estar en formato markdown.')
    if translate:
        instructions.append(' - El resumen debe ser traducido al español si es necesario.')
    return instructions


def get_prompt(text, instructions):
    if len(instructions) > 0:
        instructions_list = '\n'.join(instructions)
        instructions_text = f'El resumen debe seguir las siguientes instrucciones:\n{instructions_list}'
    else:
        instructions_text = ''
    return f"""Resume el siguiente texto encerrado en triple acento grave.\n{instructions_text}\n```{text}```."""


@click.command(help='Resume un texto')
@click.pass_context
@userinput_argument()
@click.option('--words', '-w', type=int, help='Número de palabras aproximadas', default=None)
@click.option('--sentences', '-s', type=int, help='Número de oraciones aproximadas', default=None)
@click.option('--tone', '-t', type=str, help='Tono del resumen', default=None)
@click.option('--audience', '-a', type=str, help='Público objetivo del resumen', default=None)
@click.option('--style', '-st', type=str, help='Estilo del resumen', default=None)
@click.option('--markdown', '-md', type=str, is_flag=True, help='Formato de salida mardown')
@click.option('--translate', '-tr', is_flag=True, help='Traduce si es necesario')
def summarize(ctx, userinput,words, sentences, tone, audience, style, markdown, translate):
    instructions = get_instructions(words, sentences, tone, audience, style, markdown, translate)
    prompt = get_prompt(userinput, instructions)
    model, temperature = get_context_options(ctx)
    ask_to_chatgpt(userinput, prompt=prompt, model=model, temperature=temperature)


@click.command(help='Transcribe un archivo de audio a texto')
@userinput_argument()
@copy_option()
@click.option(
    '--transcription-model', 
    '-tm', 
    type=click.Choice(['gpt-4o-mini-transcribe', 'gpt-4o-transcribe', 'whisper-1']), 
    default='gpt-4o-mini-transcribe',
    help='Modelo para transcripción default (gpt-4o-mini-transcribe)', 
)
@click.option('--language', '-l', type=str, help='Lenguaje default(es)', default='es')
def transcribe(userinput, copy, transcription_model, language):
    response = transcribe_audio(userinput, transcription_model, language)
    if copy:
        pyperclip.copy(response)
