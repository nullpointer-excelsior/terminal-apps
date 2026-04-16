from typing import Generator, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

# Model Aliases for backward compatibility and convenience
MODEL_ALIASES = {
    "gpt4o": "openai:gpt-4o",
    "gpt4om": "openai:gpt-4o-mini",
    "o1": "openai:o1-preview",
    "o1m": "openai:o1-mini",
    "gemini": "google:gemini-1.5-pro",
    "geminim": "google:gemini-1.5-flash",
}

DEFAULT_MODEL = "openai:gpt-4o-mini"


def resolve_model(model_str: str) -> str:
    """Expands aliases to provider:model format."""
    if model_str in MODEL_ALIASES:
        return MODEL_ALIASES[model_str]
    return model_str


def get_llm(model: str, streaming: bool = False) -> Any:
    """Instantiates ChatOpenAI or ChatGoogleGenerativeAI based on model string."""
    resolved_model = resolve_model(model)
    
    if ":" not in resolved_model:
        # Default to openai if no provider specified
        provider, model_name = "openai", resolved_model
    else:
        provider, model_name = resolved_model.split(":", 1)

    if provider == "openai":
        return ChatOpenAI(model=model_name, streaming=streaming)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model_name, streaming=streaming)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def invoke_llm_stream(
    prompt: Any,
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant."
) -> Generator[str, None, None]:
    """Yields text chunks from the selected provider.
    
    Args:
        prompt: Can be a simple string or a list of content blocks (for vision support).
    """
    llm = get_llm(model, streaming=True)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=prompt),
    ]
    
    for chunk in llm.stream(messages):
        # LangChain chunks have a .content attribute
        if hasattr(chunk, "content"):
            yield str(chunk.content)
        else:
            yield str(chunk)


def invoke_llm_structured(
    prompt: str,
    output_schema: type[BaseModel],
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant."
) -> BaseModel:
    """Returns a parsed Pydantic model."""
    llm = get_llm(model)
    structured_llm = llm.with_structured_output(output_schema)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=prompt),
    ]
    return structured_llm.invoke(messages)


def invoke_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant."
) -> str:
    """Non-streaming invocation that returns the full response string."""
    llm = get_llm(model)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    return str(response.content)
