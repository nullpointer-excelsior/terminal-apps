from abc import ABC, abstractmethod
from typing import Any, Optional


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


class CLIContext:
    def __init__(self, model: str, strategy: DisplayStrategy, verbose: bool):
        self.model = model
        self.strategy = strategy
        self.verbose = verbose

    def display(self, data: Any):
        """Main entry point for outputting command results."""
        if isinstance(data, str):
            self.strategy.display_text(data)
        else:
            self.strategy.display_data(data)

    def log(self, message: str):
        """Logs diagnostic messages to stderr if verbose is True."""
        if self.verbose:
            import click
            click.echo(click.style(f"DEBUG: {message}", fg="white", dim=True), err=True)

    def info(self, message: str, **kwargs):
        """Always logs informative messages to stderr."""
        import click
        click.echo(click.style(message, **kwargs), err=True)
