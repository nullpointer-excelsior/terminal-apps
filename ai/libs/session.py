from libs.database import ChatSessionRepository, Message, create_orm_session
from libs.display import LLMCallStrategy
from libs.config import config
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


class SessionStrategy(ABC):

    @abstractmethod
    def request(self) -> str:
        pass


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

