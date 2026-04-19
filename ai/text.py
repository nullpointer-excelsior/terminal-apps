import click
import pyperclip
from .libs.cli import copy_option, userinput_argument
from .libs.llm import invoke_llm_stream

grammar_prompt = """
Correct the following text grammatically, enclosed in triple backticks. ```{userinput}```. Do not return the text with the triple backticks.
"""

translate_prompt = """
Translate the following text: "{text}"
- If the text is in English, translate it to Spanish.
- If the text is in Spanish, translate it to English.
- If the text to be translated into English contains numbers, write them in words followed by the number in parentheses.
- Always reply with the translated text.
"""

question_prompt = """
You are a helpful assistant. Respond directly and without explanations unless instructed otherwise.
"""


@click.command(help='Correct the grammar of a text')
@click.pass_context
@userinput_argument()
@copy_option()
def grammar(ctx, userinput, copy):
    context = ctx.obj['context']
    prompt = grammar_prompt.format(userinput=userinput)
    
    stream = invoke_llm_stream(prompt, model=context.model)
    response = context.strategy.display_stream(stream)
    
    if copy:
        pyperclip.copy(response)


@click.command(help='English - Spanish Translator')
@click.pass_context
@userinput_argument()
@copy_option()
def translate(ctx, userinput, copy):
    context = ctx.obj['context']
    prompt = translate_prompt.format(text=userinput)
    
    stream = invoke_llm_stream(prompt, model=context.model)
    response = context.strategy.display_stream(stream)
    
    if copy:
        pyperclip.copy(response)


@click.command(help='Ask ChatGPT/LLM a question')
@click.pass_context
@userinput_argument()
def question(ctx, userinput):
    context = ctx.obj['context']
    stream = invoke_llm_stream(userinput, model=context.model, system_message=question_prompt)
    context.strategy.display_stream(stream)


def get_instructions(words, sentences, tone, audience, style, markdown, translate):
    instructions = []
    if words:
        instructions.append(f' - The summary should not exceed {words} words.')
    if sentences:
        instructions.append(f' - The summary should not exceed {sentences} sentences.')
    if style:
        instructions.append(f' - The summary should have a {style} style.')
    if audience:
        instructions.append(f' - The summary should target a {audience} audience.')
    if tone:
        instructions.append(f' - The summary should have a {tone} tone.')
    if markdown:
        instructions.append(' - The summary must be in markdown format.')
    if translate:
        instructions.append(' - The summary must be translated to Spanish if necessary.')
    return instructions


def get_prompt(text, instructions):
    if len(instructions) > 0:
        instructions_list = '\n'.join(instructions)
        instructions_text = f'The summary must follow these instructions:\n{instructions_list}'
    else:
        instructions_text = ''
    return f"""Summarize the following text enclosed in triple backticks.\n{instructions_text}\n```{text}```."""


@click.command(help='Summarize a text')
@click.pass_context
@userinput_argument()
@click.option('--words', '-w', type=int, help='Approximate number of words', default=None)
@click.option('--sentences', '-s', type=int, help='Approximate number of sentences', default=None)
@click.option('--tone', '-t', type=str, help='Tone of the summary', default=None)
@click.option('--audience', '-a', type=str, help='Target audience of the summary', default=None)
@click.option('--style', '-st', type=str, help='Style of the summary', default=None)
@click.option('--markdown', '-md', is_flag=True, help='Markdown output format')
@click.option('--translate', '-tr', is_flag=True, help='Translate if necessary')
def summarize(ctx, userinput, words, sentences, tone, audience, style, markdown, translate):
    context = ctx.obj['context']
    instructions = get_instructions(words, sentences, tone, audience, style, markdown, translate)
    prompt = get_prompt(userinput, instructions)
    
    system_message = "You are an expert at synthesizing information."
    if markdown:
        system_message += " Output in Markdown format."

    stream = invoke_llm_stream(prompt, model=context.model, system_message=system_message)
    context.strategy.display_stream(stream)


@click.command(help='Transcribe an audio file to text')
@click.pass_context
@userinput_argument()
@copy_option()
@click.option('--language', '-l', type=str, help='Default language (e.g., "en", "es")', default='en')
def transcribe(ctx, userinput, copy, language):
    context = ctx.obj['context']
    context.info(f"🎙️ Transcribing {userinput}...", fg="cyan")
    
    from openai import OpenAI
    client = OpenAI()
    try:
        with open(userinput, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        response = transcript.text
        context.display(response)
        if copy:
            pyperclip.copy(response)
    except Exception as e:
        context.info(f"❌ Error during transcription: {e}", fg="red")

