from libs.chatgpt import ask_to_chatgpt, get_model
from libs.cli import copy_option, userinput_argument, get_context_options
import click
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import pyperclip


prompt_base="""
Eres un experto tutor de inglés y ayudarás al usuario a aprender inglés siguiendo las siguientes instrucciones:

# Instrucciones:
- Responderás de forma directa y de la forma más concisa posible.
- Todo texto en inglés que el usuario te proporcione puede que tenga errores y deberás corregirlo, entregando una lista de correcciones.
- Importante: el texto corregido DEBE IR AL PRINCIPIO DE LA RESPUESTA.
- Si el usuario te entrega un texto en español, deberás traducirlo.
- Deberás dar sugerencias para mejorar las frases que el usuario te dé si estas están en inglés y no suenan bien.
- Deberás dar todas tus respuestas con un resumen de errores y sugerencias, y al final el texto que el usuario necesita o te pidió que corrijas.
- Explicarás gramática, phrasal verbs o tiempos verbales.
- Si una frase contiene números, deberás dar el número escrito; por ejemplo: I'm 30: I'm thirty (30).
- El usuario puede que te entregue un texto en inglés con palabras en español encerradas entre "<>" lo que significa que él no sabe cómo se dice esa palabra en inglés; deberás dar la traducción en el texto corregido, ejemplo: 
    - I want to <ser libre>: "I want to break free"
    - He <tenía que ir a trabajar> on Sunday: "he had to go to work on Sunday" 
- Deberás dar la lección de inglés con un nombre corto y en inglés más adecuado para aprender de la falencia del usuario.
"""


client = OpenAI()


class EnglishTutorResponse(BaseModel):
    corrected_text: str
    corrections: List[str]
    errors: List[str]
    suggestions: List[str]


def structured_output(input, model, temperature):
    completion = client.beta.chat.completions.parse(
        model=get_model(model),
        messages=[
            {"role": "system", "content": prompt_base},
            {
                "role": "user",
                "content": input,
            },
        ],
        response_format=EnglishTutorResponse,
        temperature=temperature
    )
    return completion.choices[0].message


@click.command(help='Profesor de inglés')
@click.pass_context
@userinput_argument()
@copy_option()
def english(ctx, userinput, copy):
    model, temperature = get_context_options(ctx)

    response = structured_output(userinput, model, temperature)

    if (response.refusal):
        click.secho("Response refused", fg='red', bold=True)
        click.secho(response.refusal, fg='red')
    else:
        click.secho(f"\n{response.parsed.corrected_text}\n", fg='green')
        click.secho("Corrections:", fg='blue', bold=True)
        for c in response.parsed.corrections:
            click.secho(f"- {c}", fg='blue')
        
        click.secho("Errors:", fg='red', bold=True)
        for e in response.parsed.errors:
            click.secho(f"- {e}", fg='red')
        
        click.secho("Suggestions:", fg='yellow', bold=True)
        for s in response.parsed.suggestions:
            click.secho(f"- {s}", fg='yellow')
        print()
        if copy:
            pyperclip.copy(response.parsed.corrected_text)            
