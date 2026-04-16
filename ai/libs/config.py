import os
from dataclasses import dataclass


@dataclass
class Config:
    ai_prompt_resources: str
    google_api_key: str


config = Config(
    ai_prompt_resources=os.getenv("AI_PROMPT_RESOURCES"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
