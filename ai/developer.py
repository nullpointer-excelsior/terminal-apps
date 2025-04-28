from libs.database import ChatSessionRepository, Message, create_orm_session, Session
from libs.chatgpt import ask_simple_question_to_chatgpt, chat_with_chatgpt, get_stream_completion
from libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from libs.display import process_markdown, display_highlighted_code, display_markdown
from libs.config import config
import click
import subprocess
import pyperclip
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Callable

dev_prompt="""
Eres un útil asistente y experto desarrollador y arquitecto de software. Responderás de forma directa y sin explicaciones.
"""

commit_generator_prompt="""
Crea un mensaje de commit semántico corto en inglés basado en el siguiente diff:
{diff}
"""


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


@dataclass
class WithSessionStrategy(SessionStrategy):

    userinput: str
    systemprompt: str
    model: str
    temperature: float
    llmcall: LLMCallStrategy
    assistant: str

    def request(self):
        messages = [
            {"role": "system", "content": self.systemprompt},
            {"role": "user", "content": self.userinput}
        ]
        chatsession_repository = ChatSessionRepository(create_orm_session(config.ai_sqlite_database))
        workspace = os.getcwd()
        
        session_found = chatsession_repository.find_by_workspace_and_assistant(workspace, self.assistant)

        if session_found:
            session_found.messages.append(Message(session_id=session_found.id, content=self.userinput, role='user'))
            chatsession_repository.update(session_found)
            messages = [{ 'role': m.role, 'content': m.content } for m in session_found.messages]
        else:
            session_found = chatsession_repository.create(workspace, self.assistant, messages)

        response = self.llmcall.request(messages, model=self.model, temperature=self.temperature)

        session_found.messages.append(Message(session_id=session_found.id, content=response, role='assistant'))
        chatsession_repository.update(session_found)

        return response


@dataclass
class WithoutSessionStrategy(SessionStrategy):

    userinput: str
    systemprompt: str
    model: str
    temperature: float
    llmcall: LLMCallStrategy

    def request(self):
        messages = [
            {"role": "system", "content": self.systemprompt},
            {"role": "user", "content": self.userinput}
        ]
        return self.llmcall.request(messages, model=self.model, temperature=self.temperature)


@click.command(help='Desarrollador experto')
@click.pass_context
@userinput_argument()
@markdown_option()
@click.option('-s', '--session', is_flag=True, help="Crea u obtiene una sesión.")
def dev(ctx, userinput, markdown, session):
    model, temperature = get_context_options(ctx)

    llmcall = MarkdowDisplayStrategy() if markdown else HighlightedCodeDisplayStrategy()

    if session:
        session_strategy = WithSessionStrategy(
            userinput=userinput,
            systemprompt=dev_prompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall,
            assistant='dev'
        ) 
    else: 
        session_strategy = WithoutSessionStrategy(
            userinput=userinput,
            systemprompt=dev_prompt,
            model=model,
            temperature=temperature,
            llmcall=llmcall
        )

    session_strategy.request()




@click.command(help='Generador de commit')
@click.pass_context
@copy_option()
def commit_generator(ctx, copy):
    model, temperature = get_context_options(ctx)
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
        diff = subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True)
        prompt_diff = commit_generator_prompt.format(diff=diff)
        response = ask_simple_question_to_chatgpt(prompt_diff, model=model, temperature=temperature)
        if copy:
            pyperclip.copy(response)
    except subprocess.CalledProcessError:
        pass