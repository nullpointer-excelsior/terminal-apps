from .developer import dev, commit_generator
from .dependency_scanner import scan_deps
from .english import english
from .libs.cli import model_option
from .screenshot import screenshot
from .text import grammar, translate, question, summarize, transcribe
from .libs.context import CLIContext
from .libs.display import RichDisplayStrategy, PlainDisplayStrategy, JSONDisplayStrategy
import click


@click.group(help='AI tools for terminal')
@model_option()
@click.option('--plain', is_flag=True, help='Plain text output')
@click.option('--json', 'json_output', is_flag=True, help='JSON output')
@click.option('--verbose', is_flag=True, help='Verbose output (diagnostics on stderr)')
@click.pass_context
def cli(ctx, model, plain, json_output, verbose):
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    
    if json_output:
        strategy = JSONDisplayStrategy()
    elif plain:
        strategy = PlainDisplayStrategy()
    else:
        strategy = RichDisplayStrategy()
        
    ctx.obj['context'] = CLIContext(model=model, strategy=strategy, verbose=verbose)

cli.add_command(question)
cli.add_command(grammar)
cli.add_command(translate)
cli.add_command(dev)
cli.add_command(english)
cli.add_command(summarize)
cli.add_command(screenshot)
cli.add_command(commit_generator)
cli.add_command(transcribe)
cli.add_command(scan_deps)

if __name__ == "__main__":
    cli()

