from typing import Generator, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

# Model Aliases for backward compatibility and convenience
MODEL_ALIASES = {
    "gpt4.1n": "openai:gpt-4.1-nano",
    "gpt4.1m": "openai:gpt-4.1-mini",
    "gpt4.1": "openai:gpt-4.1",
    "gpt5m": "openai:gpt-5-mini",
    "gemini": "google-genai:gemini-3.1-pro-preview",
    "gemini-flash": "google-genai:gemini-3-flash-preview",
}

DEFAULT_MODEL = "openai:gpt-5-mini"


class AIInfrastructureError(Exception):
    """Raised when LLM initialization or invocation fails.
    
    This wraps provider-specific exceptions (authentication errors,
    invalid model names, rate limits, etc.) into a unified error
    that can be handled gracefully by CLI commands.
    """
    pass


def resolve_model(model_str: str) -> str:
    """Expands aliases to provider:model format."""
    if model_str in MODEL_ALIASES:
        return MODEL_ALIASES[model_str]
    return model_str


def get_llm(model: str, streaming: bool = False) -> Any:
    """Instantiates a chat model using LangChain's unified factory.
    
    This function uses init_chat_model to create a provider-agnostic
    chat model instance. Provider-specific imports are handled by
    LangChain internally.
    
    Args:
        model: Model string in format 'provider:model-name' or an alias
        streaming: Whether to enable streaming mode
        
    Returns:
        A LangChain chat model instance
        
    Raises:
        AIInfrastructureError: When model instantiation fails
    """
    resolved_model = resolve_model(model)
    
    try:
        # Use LangChain's unified factory for provider-agnostic instantiation
        # The factory automatically handles provider-specific configuration
        llm = init_chat_model(
            model=resolved_model,
            temperature=0.7,
        )
        
        # Configure streaming if requested
        if streaming:
            llm.streaming = True
            
        return llm
        
    except Exception as e:
        # Wrap provider-specific errors into user-friendly messages
        raise AIInfrastructureError(
            f"Failed to initialize model '{resolved_model}': {str(e)}\n"
            f"Please check your API keys and model name."
        ) from e


def invoke_llm_stream(
    prompt: Any,
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant.",
    context: Any = None
) -> Generator[str, None, None]:
    """Yields text chunks from the selected provider.
    
    Args:
        prompt: Can be a simple string or a list of content blocks (for vision support).
        model: Model identifier (alias or full provider:model string)
        system_message: System prompt to set context
        context: Optional CLIContext for verbose logging
        
    Yields:
        Text chunks as strings
        
    Raises:
        AIInfrastructureError: When streaming fails
    """
    if context:
        context.log(f"Calling LLM with model: {model}")
        context.log(f"System Message: {system_message}")
        context.log(f"Prompt type: {type(prompt)}")

    try:
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
                
    except AIInfrastructureError:
        # Re-raise infrastructure errors as-is
        raise
    except Exception as e:
        raise AIInfrastructureError(
            f"Streaming failed: {str(e)}"
        ) from e


def invoke_llm_structured(
    prompt: str,
    output_schema: type[BaseModel],
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant."
) -> BaseModel:
    """Returns a parsed Pydantic model.
    
    Args:
        prompt: User prompt text
        output_schema: Pydantic model class defining the expected output structure
        model: Model identifier (alias or full provider:model string)
        system_message: System prompt to set context
        
    Returns:
        Instance of the output_schema with parsed data
        
    Raises:
        AIInfrastructureError: When structured output generation fails
    """
    try:
        llm = get_llm(model)
        structured_llm = llm.with_structured_output(output_schema)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=prompt),
        ]
        return structured_llm.invoke(messages)
        
    except AIInfrastructureError:
        # Re-raise infrastructure errors as-is
        raise
    except Exception as e:
        raise AIInfrastructureError(
            f"Structured output generation failed: {str(e)}"
        ) from e


def invoke_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_message: str = "You are a helpful assistant."
) -> str:
    """Non-streaming invocation that returns the full response string.
    
    Args:
        prompt: User prompt text
        model: Model identifier (alias or full provider:model string)
        system_message: System prompt to set context
        
    Returns:
        Complete response text as a string
        
    Raises:
        AIInfrastructureError: When invocation fails
    """
    try:
        llm = get_llm(model)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        return str(response.content)
        
    except AIInfrastructureError:
        # Re-raise infrastructure errors as-is
        raise
    except Exception as e:
        raise AIInfrastructureError(
            f"LLM invocation failed: {str(e)}"
        ) from e
