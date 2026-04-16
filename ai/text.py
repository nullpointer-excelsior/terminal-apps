import click
import pyperclip
from libs.display import HighlightedCodeDisplayStrategy, MarkdownDisplayStrategy
from libs.cli import copy_option, userinput_argument, get_context_options
from libs.llm import invoke_llm, invoke_llm_stream

grammar_prompt = """
Corrije gramaticalmente el texto encerrado en triple acento grave. ```{userinput}```, no debes devolver el texto con el triple acento grave.
"""

translate_prompt = """
Traduce el siguiente texto: "{text}"
- Si el texto esta en inglés traducelo al español
- Si el texto esta en español traducelo al inglés.
- Si el texto que debe ser traducido al inglés contiene números, deberás escribirlos con palabras seguidos del número encerrado entre paréntesis.
"""

question_prompt = """
Eres un útil asistente. Responderás de forma directa y sin explicaciones a menos que te indique lo contrario.
"""


@click.command(help='Corrije la gramatica de un texto')
@click.pass_context
@userinput_argument()
@copy_option()
def grammar(ctx, userinput, copy):
    model = get_context_options(ctx)
    prompt = grammar_prompt.format(userinput=userinput)
    response = ""
    for chunk in invoke_llm_stream(prompt, model=model):
        print(chunk, end="", flush=True)
        response += chunk
    print()  # New line after streaming
    if copy:
        pyperclip.copy(response)


@click.command(help='Traductor de Inglés - Español')
@click.pass_context
@userinput_argument()
@copy_option()
def translate(ctx, userinput, copy):
    prompt = translate_prompt.format(text=userinput)
    model = get_context_options(ctx)
    response = ""
    for chunk in invoke_llm_stream(prompt, model=model):
        print(chunk, end="", flush=True)
        response += chunk
    print()  # New line after streaming
    if copy:
        pyperclip.copy(response)


@click.command(help='Pregunta a ChatGPT')
@click.pass_context
@userinput_argument()
def question(ctx, userinput):
    model = get_context_options(ctx)
    llmcall = HighlightedCodeDisplayStrategy()
    llmcall.request(userinput, model=model, system_message=question_prompt)


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
@click.option('--markdown', '-md', is_flag=True, help='Formato de salida mardown')
@click.option('--translate', '-tr', is_flag=True, help='Traduce si es necesario')
def summarize(ctx, userinput, words, sentences, tone, audience, style, markdown, translate):
    instructions = get_instructions(words, sentences, tone, audience, style, markdown, translate)
    prompt = get_prompt(userinput, instructions)
    model = get_context_options(ctx)

    if markdown:
        llmcall = MarkdownDisplayStrategy()
    else:
        llmcall = HighlightedCodeDisplayStrategy()

    llmcall.request(prompt, model=model, system_message="Eres un experto sintetizando información.")


@click.command(help='Transcribe un archivo de audio a texto')
@userinput_argument()
@copy_option()
@click.option('--language', '-l', type=str, help='Lenguaje default(es)', default='es')
def transcribe(userinput, copy, language):
    # This remains using OpenAI SDK via a simplified helper or we can move it to a dedicated audio lib if needed.
    # For now, following instructions to migrate core commands.
    # Note: transcribe was using transcribe_audio from chatgpt.py which is being deleted.
    # However, Phase 5 says audio module continues to work.
    # Let's check if we should keep a minimal version of transcribe_audio or if it's out of scope for this task.
    # The prompt says: "Migrate text.py commands... Update transcribe()".
    from openai import OpenAI
    client = OpenAI()
    with open(userinput, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )
    response = transcript.text
    click.echo(response)
    if copy:
        pyperclip.copy(response)

