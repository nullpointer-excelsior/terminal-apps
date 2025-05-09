import os
import click
import base64
import pyperclip
from openai import OpenAI
from pathlib import Path
from libs.cli import copy_option
import tempfile
from datetime import datetime


client = OpenAI()


def openai_vision_request(model, user_input, base64_image):
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": user_input
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
            }
        ],
        max_tokens=1000,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        answer = delta.content if delta.content is not None else ''
        yield answer


def capture_screen(filename):
    os.system(f"screencapture -i {filename}")


def png_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data)
        return base64_encoded.decode('utf-8')
    

def generate_temp_capture():
    temp_dir = tempfile.gettempdir()
    filename = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + "capture.png"
    return os.path.join(temp_dir, filename)


def translate_image(model, base64_image):
    response = ''
    for stream in openai_vision_request(model, "Traduce el siguiente texto al español si el contenido está en inglés, y si el contenido está en español, tradúcelo al inglés.", base64_image):
        print(stream, end="", flush=True)
        response += stream
    return response


def explain_image(model, base64_image):
    response = ''
    for stream in openai_vision_request(model, "Explicame que hay en la imagen", base64_image):
        print(stream, end="", flush=True)
        response += stream
    return response


def transcribe_image(model, base64_image):
    response = ''
    for stream in openai_vision_request(model, "Transcribe el texto de la imagen proporcinada en texto plano.", base64_image):
        print(stream, end="", flush=True)
        response += stream
    return response


def prompt_image(model, prompt, base64_image):
    response = ''
    for stream in openai_vision_request(model, prompt, base64_image):
        print(stream, end="", flush=True)
        response += stream
    return response


@click.command(help='Captura de pantalla con integración AI')
@click.option('-tr', '--translate', is_flag=True, help="Habilita la opción de traducción")
@click.option('-e', '--explain', is_flag=True, help="Habilita la opción de explicación")
@click.option('-p', '--prompt', type=str, help="Proporciona un prompt de texto")
@copy_option()
def screenshot(translate, explain, prompt, copy):
    
    filename = generate_temp_capture()
    capture_screen(filename)
    
    if not Path(filename).exists():
        click.echo(click.style("Capture aborted", fg='yellow'))
        return
    
    b64 = png_to_base64(filename)
    
    if translate:
        response = translate_image('gpt-4o-mini', b64)
    elif explain:
        response = explain_image('gpt-4o-mini', b64)
    elif prompt:
        response = prompt_image('gpt-4o-mini', prompt, b64)
    else:
        response = transcribe_image('gpt-4o-mini', b64)
    
    if copy:
        pyperclip.copy(response)
    