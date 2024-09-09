import os
import base64
import argparse
from openai import OpenAI

client = OpenAI()


def openai_vision_request(model, user_input, base64_image):
    response = client.chat.completions.create(
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
    )
    return response.choices[0]


def capture_screen(filename):
    os.system(f"screencapture -i {filename}")


def png_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data)
        return base64_encoded.decode('utf-8')
    

def translate_image(model, base64_image):
    res = openai_vision_request(model, "Traduce el siguiente texto al español si el contenido esta en ingles y si el contenido esta en español traducelo al ingles", base64_image)
    print(res)


def explain_image(model, base64_image):
    res = openai_vision_request(model, "Explicame que hay en la imagen", base64_image)
    print(res)

def prompt_image(model, prompt, base64_image):
    res = openai_vision_request(model, prompt, base64_image)
    print(res)



def main():
    parser = argparse.ArgumentParser(description="Un script que maneja opciones de traducción, explicación y solicitud.")
    
    # Opciones y sus versiones cortas
    parser.add_argument('-t', '--translate', action='store_true', help="Habilita la opción de traducción")
    parser.add_argument('-e', '--explain', action='store_true', help="Habilita la opción de explicación")
    parser.add_argument('-p', '--prompt', type=str, help="Proporciona un prompt de texto")
    
    args = parser.parse_args()
    filename = "capture.png"

    capture_screen(filename)
    b64 = png_to_base64(filename)
    
    if args.translate:
        translate_image('gpt-4o-mini', b64)
    if args.explain:
        explain_image('gpt-4o-mini', b64)
    if args.prompt:
        prompt_image('gpt-4o-mini', args.prompt, b64)
    
    os.system(f"rm -f {filename}")
    
if __name__ == '__main__':
    main()