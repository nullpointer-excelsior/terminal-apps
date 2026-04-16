import os
import click
import base64
import pyperclip
from pathlib import Path
from libs.cli import copy_option, get_context_options
from libs.llm import invoke_llm_stream
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


def process_image_query(model, prompt, base64_image):
    """Processes an image query using LangChain vision support."""
    content = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        },
    ]
    
    response = ""
    for chunk in invoke_llm_stream(prompt=content, model=model):
        print(chunk, end="", flush=True)
        response += chunk
    print()
    return response


@click.command(help='Captura de pantalla con integración AI')
@click.pass_context
@click.option('-tr', '--translate', is_flag=True, help="Habilita la opción de traducción")
@click.option('-e', '--explain', is_flag=True, help="Habilita la opción de explicación")
@click.option('-p', '--prompt', type=str, help="Proporciona un prompt de texto")
@copy_option()
def screenshot(ctx, translate, explain, prompt, copy):
    model, _ = get_context_options(ctx)
    
    filename = generate_temp_capture()
    capture_screen(filename)
    
    if not Path(filename).exists():
        click.echo(click.style("Capture aborted", fg='yellow'))
        return
    
    b64 = png_to_base64(filename)
    
    if translate:
        query = "Traduce el siguiente texto al español si el contenido está en inglés, y si el contenido está en español, tradúcelo al inglés."
    elif explain:
        query = "Explicame que hay en la imagen"
    elif prompt:
        query = prompt
    else:
        query = "Transcribe el texto de la imagen proporcinada en texto plano."
    
    response = process_image_query(model, query, b64)
    
    if copy:
        pyperclip.copy(response)
    