from libs.llm import invoke_llm_structured
from libs.cli import copy_option, userinput_argument, get_context_options
import click
from pydantic import BaseModel, Field
from typing import List
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


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


class EnglishTutorResponse(BaseModel):
    corrected_text: str = Field(description="The full corrected text or translation.")
    corrections: List[str] = Field(description="List of specific corrections made.")
    errors: List[str] = Field(description="List of grammatical or vocabulary errors found.")
    suggestions: List[str] = Field(description="Suggestions to improve the flow or sound more natural.")


@click.command(help='Profesor de inglés')
@click.pass_context
@userinput_argument()
@copy_option()
def english(ctx, userinput, copy):
    model, _ = get_context_options(ctx)
    console = Console()

    with console.status("[bold green]Pensando..."):
        response: EnglishTutorResponse = invoke_llm_structured(
            prompt=userinput,
            output_schema=EnglishTutorResponse,
            model=model,
            system_message=prompt_base
        )

    # Render corrected text prominently
    console.print(Panel(
        Text(response.corrected_text, style="bold green"),
        title="[bold green]Corrected Text",
        border_style="green"
    ))

    if response.corrections:
        console.print("\n[bold blue]Corrections:")
        for c in response.corrections:
            console.print(f" [blue]•[/blue] {c}")

    if response.errors:
        console.print("\n[bold red]Errors:")
        for e in response.errors:
            console.print(f" [red]•[/red] {e}")

    if response.suggestions:
        console.print("\n[bold yellow]Suggestions:")
        for s in response.suggestions:
            console.print(f" [yellow]•[/yellow] {s}")
    
    console.print()

    if copy:
        pyperclip.copy(response.corrected_text)
