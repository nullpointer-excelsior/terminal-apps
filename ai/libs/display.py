from rich.markdown import Markdown
from rich.console import Console
from contextlib import nullcontext
import click
from abc import ABC, abstractmethod
from libs.chatgpt import chat_with_chatgpt, get_stream_completion


console = Console()


def display_markdown(content):
    print('')
    console.print(Markdown(content))
    print('')


def display_highlighted_code(llm_stream):
    complete_response = ''
    code_buffer = ''
    waiting_for_code = False
    extract_lastline = lambda x: x.strip().split('\n')[-1]
    status_ctx = nullcontext() 

    for stream in llm_stream():
        stream = stream.content if stream.content is not None else ''
        complete_response += stream

        if complete_response != '' and complete_response[-1] == '\n' and not waiting_for_code:
            last_line = extract_lastline(complete_response)
            if "```" in last_line and "```markdown" not in last_line:
                waiting_for_code = True
                code_buffer += last_line
                print('')
                status_ctx = console.status("[cyan]🧰 Building code snippet...\n", spinner="dots")
                status_ctx.__enter__()
                
        if waiting_for_code:
            code_buffer += stream
            if code_buffer != '' and code_buffer[-1] == '\n':
                last_line = extract_lastline(code_buffer)
                if "```" == last_line.strip():
                    status_ctx.__exit__(None, None, None)
                    console.log("[green]✅ Code snippet ready!")
                    display_markdown(code_buffer)
                    waiting_for_code = False
                    code_buffer = ''
                    
        if not waiting_for_code and "``" not in extract_lastline(complete_response):
            print(stream, end="", flush=True)

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
    def request(self, messages, model, temperature) -> str:
        pass


class SessionStrategy(ABC):

    @abstractmethod
    def request(self) -> str:
        pass


class HighlightedCodeDisplayStrategy(LLMCallStrategy):

    def request(self, messages, model, temperature):
        return display_highlighted_code(lambda: get_stream_completion(messages, model=model, temperature=temperature))


class MarkdowDisplayStrategy(LLMCallStrategy):

    def request(self, messages, model, temperature):
        click.echo(click.style('\n🔄 Waiting for the complete answer from OpenAI...', fg='cyan', bold=True, underline=True))
        response = chat_with_chatgpt(messages, model=model, temperature=temperature, stream=False)
        display_markdown(response)
        return response
