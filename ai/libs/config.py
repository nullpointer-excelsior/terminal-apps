import os
from dataclasses import dataclass


@dataclass
class Config:
    ai_prompt_resources: str
    ai_sqlite_database: str


config = Config(
    ai_prompt_resources=os.getenv("AI_PROMPT_RESOURCES"),
    ai_sqlite_database=os.getenv("AI_SQLITE_DATABASE")
)
