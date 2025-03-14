import os
from dataclasses import dataclass


@dataclass
class Config:
    ai_prompt_resources: str


config = Config(ai_prompt_resources=os.getenv("AI_PROMPT_RESOURCES"))
