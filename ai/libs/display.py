from rich.markdown import Markdown
from rich.console import Console
from contextlib import nullcontext
import click
import json
from typing import Any
from abc import ABC, abstractmethod
from .llm import invoke_llm, invoke_llm_stream


console = Console()
error_console = Console(stderr=True)


class DisplayStrategy(ABC):
    @abstractmethod
    def display_text(self, text: str):
        """Displays raw text result."""
        pass

    @abstractmethod
    def display_data(self, data: Any):
        """Displays structured data."""
        pass

    @abstractmethod
    def display_stream(self, stream_generator):
        """Handles streaming LLM responses."""
        pass


class RichDisplayStrategy(DisplayStrategy):
    def __init__(self):
        self.console = console

    def display_text(self, text: str):
        print('')
        self.console.print(Markdown(text))
        print('')

    def display_data(self, data: Any):
        self.console.print(data)

    def display_stream(self, stream_generator):
        return display_highlighted_code(stream_generator)


class PlainDisplayStrategy(DisplayStrategy):
    def display_text(self, text: str):
        click.echo(text)

    def display_data(self, data: Any):
        click.echo(str(data))

    def display_stream(self, stream_generator):
        complete_response = ''
        for chunk in stream_generator:
            complete_response += chunk
            click.echo(chunk, nl=False)
        click.echo('')
        return complete_response


class JSONDisplayStrategy(DisplayStrategy):
    def display_text(self, text: str):
        self.display_data({"result": text})

    def display_data(self, data: Any):
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))

    def display_stream(self, stream_generator):
        complete_response = ''
        for chunk in stream_generator:
            complete_response += chunk
        self.display_data({"result": complete_response})
        return complete_response


def display_markdown(content):
    print('')
    console.print(Markdown(content))
    print('')


def display_highlighted_code(llm_stream_generator):
    complete_response = ''
    code_buffer = ''
    waiting_for_code = False
    extract_lastline = lambda x: x.strip().split('\n')[-1]
    status_ctx = nullcontext() 

    for chunk in llm_stream_generator:
        complete_response += chunk

        if complete_response != '' and complete_response[-1] == '\n' and not waiting_for_code:
            last_line = extract_lastline(complete_response)
            if "```" in last_line and "```markdown" not in last_line:
                waiting_for_code = True
                code_buffer += last_line
                print('')
                status_ctx = console.status("[cyan]🧰 Building code snippet...\n", spinner="dots")
                status_ctx.__enter__()
                
        if waiting_for_code:
            code_buffer += chunk
            if code_buffer != '' and code_buffer[-1] == '\n':
                last_line = extract_lastline(code_buffer)
                if "```" == last_line.strip():
                    status_ctx.__exit__(None, None, None)
                    console.log("[green]✅ Code snippet ready!")
                    display_markdown(code_buffer)
                    waiting_for_code = False
                    code_buffer = ''
                    
        if not waiting_for_code and "``" not in extract_lastline(complete_response):
            print(chunk, end="", flush=True)

    if len(code_buffer) > 1:
        status_ctx.__exit__(None, None, None)
        console.log("[green]✅ Code snippet ready!")
        display_markdown(code_buffer)
    
    print('\n')
    return complete_response


def process_markdown(markdown: bool, with_markdown, no_markdown):
    if markdown:
        click.echo(click.style('\n🔄 Waiting for the complete answer from OpenAI...', fg='cyan', bold=True, underline=True))
        response = with_markdown()
        display_markdown(response)
        return response
    else:
        return no_markdown()
    

class LLMCallStrategy(ABC):

    @abstractmethod
    def request(self, prompt, model, system_message) -> str:
        pass


class SessionStrategy(ABC):

    @abstractmethod
    def request(self) -> str:
        pass


class HighlightedCodeDisplayStrategy(LLMCallStrategy):

    def request(self, prompt, model, system_message):
        return display_highlighted_code(invoke_llm_stream(prompt, model=model, system_message=system_message))


class MarkdownDisplayStrategy(LLMCallStrategy):

    def request(self, prompt, model, system_message):
        click.echo(click.style('\n🔄 Streaming answer...', fg='cyan', bold=True, underline=True))
        response = ""
        for chunk in invoke_llm_stream(prompt, model=model, system_message=system_message):
            response += chunk
        display_markdown(response)
        return response
