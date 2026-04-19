import os
import click
import base64
import pyperclip
from pathlib import Path
from .libs.cli import copy_option, get_context_options
from .libs.llm import invoke_llm_stream
import tempfile
from datetime import datetime


def capture_screen(filename):
    os.system(f"screencapture -i {filename}")


def png_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data)
        return base64_encoded.decode('utf-8')
    

def generate_temp_capture():
    temp_dir = tempfile.gettempdir()
    filename = datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_capture.png"
    return os.path.join(temp_dir, filename)


def process_image_query(context, prompt, base64_image):
    """Processes an image query using LangChain vision support."""
    content = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        },
    ]
    
    stream = invoke_llm_stream(prompt=content, model=context.model)
    return context.strategy.display_stream(stream)


@click.command(help='AI-integrated screen capture')
@click.pass_context
@click.option('-tr', '--translate', is_flag=True, help="Enable translation")
@click.option('-e', '--explain', is_flag=True, help="Enable explanation")
@click.option('-p', '--prompt', type=str, help="Provide a custom text prompt")
@copy_option()
def screenshot(ctx, translate, explain, prompt, copy):
    context = ctx.obj['context']
    
    filename = generate_temp_capture()
    capture_screen(filename)
    
    if not Path(filename).exists():
        context.info("Capture aborted", fg='yellow')
        return
    
    b64 = png_to_base64(filename)
    
    if translate:
        query = "Translate the following text to Spanish if the content is in English, and if it is in Spanish, translate it to English."
    elif explain:
        query = "Explain what is in the image"
    elif prompt:
        query = prompt
    else:
        query = "Transcribe the text from the provided image in plain text."
    
    context.info(f"📸 Processing image with {context.model}...", fg="cyan")
    
    content = [
        {"type": "text", "text": query},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        },
    ]
    
    stream = invoke_llm_stream(prompt=content, model=context.model)
    response = context.strategy.display_stream(stream)
    
    if copy:
        pyperclip.copy(response)
    