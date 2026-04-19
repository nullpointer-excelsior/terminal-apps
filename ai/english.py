from .libs.llm import invoke_llm_structured
from .libs.cli import copy_option, userinput_argument, get_context_options
import click
from pydantic import BaseModel, Field
from typing import List
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


prompt_base="""
You are an expert English tutor. Help the user learn English following these instructions:

# Instructions:
- Respond directly and as concisely as possible.
- Any English text the user provides may have errors; you must correct it and provide a list of corrections.
- Important: the corrected text MUST BE AT THE BEGINNING OF THE RESPONSE.
- If the user provides text in Spanish, you must translate it.
- Provide suggestions to improve phrases if they are in English but don't sound natural.
- Give all your responses with a summary of errors and suggestions, and finally the text the user needs or asked you to correct.
- Explain grammar, phrasal verbs, or verb tenses.
- If a phrase contains numbers, provide the written number; for example: I'm 30: I'm thirty (30).
- The user may provide English text with Spanish words enclosed in "<>", which means they don't know how to say that word in English; provide the translation in the corrected text. Example: 
    - I want to <ser libre>: "I want to break free"
    - He <tenía que ir a trabajar> on Sunday: "He had to go to work on Sunday" 
- Provide the English lesson with a short, appropriate English name to help the user learn from their mistakes.
"""


class EnglishTutorResponse(BaseModel):
    corrected_text: str = Field(description="The full corrected text or translation.")
    corrections: List[str] = Field(description="List of specific corrections made.")
    errors: List[str] = Field(description="List of grammatical or vocabulary errors found.")
    suggestions: List[str] = Field(description="Suggestions to improve the flow or sound more natural.")


@click.command(help='English Teacher')
@click.pass_context
@userinput_argument()
@copy_option()
def english(ctx, userinput, copy):
    context = ctx.obj['context']

    context.info(f"🤔 Thinking with {context.model}...", fg="green", bold=True)
    
    response: EnglishTutorResponse = invoke_llm_structured(
        prompt=userinput,
        output_schema=EnglishTutorResponse,
        model=context.model,
        system_message=prompt_base
    )

    # Use strategies for display where possible or use context.display/info for specialized formatting
    # Since EnglishTutorResponse is structured, we can pass it to display_data or handle it here.
    # To keep the rich experience for standard TTY, we can use context.info/log.
    
    # We'll use a dictionary to leverage strategy.display_data if needed, 
    # but for standard output we want the nice panels.
    
    if hasattr(context.strategy, 'console'): # RichDisplayStrategy uses console
        from rich.panel import Panel
        from rich.text import Text
        context.strategy.console.print(Panel(
            Text(response.corrected_text, style="bold green"),
            title="[bold green]Corrected Text",
            border_style="green"
        ))

        if response.corrections:
            context.strategy.console.print("\n[bold blue]Corrections:")
            for c in response.corrections:
                context.strategy.console.print(f" [blue]•[/blue] {c}")

        if response.errors:
            context.strategy.console.print("\n[bold red]Errors:")
            for e in response.errors:
                context.strategy.console.print(f" [red]•[/red] {e}")

        if response.suggestions:
            context.strategy.console.print("\n[bold yellow]Suggestions:")
            for s in response.suggestions:
                context.strategy.console.print(f" [yellow]•[/yellow] {s}")
        
        context.strategy.console.print()
    else:
        # For Plain or JSON strategy
        context.display(response.model_dump())

    if copy:
        pyperclip.copy(response.corrected_text)
