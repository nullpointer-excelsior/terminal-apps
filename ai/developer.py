from .libs.cli import userinput_argument, get_context_options, copy_option, markdown_option
from .libs.display import HighlightedCodeDisplayStrategy, MarkdownDisplayStrategy
from .libs.llm import invoke_llm, invoke_llm_stream
from .libs.config import config
import click
import subprocess
import pyperclip
import os

dev_prompt = """
You are a helpful assistant and expert software developer/architect. Respond directly and without unnecessary explanations.
"""

userinput_with_files = """
I have the following files:
{content}
Respond to the following:
{input}
"""


def create_context_files(file_paths):
    markdown_content = "## Content files\n"
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        markdown_content += f"**{file_name}**\n"
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                extension = os.path.splitext(file_name)[1][1:]
                markdown_content += f"```{extension}\n{content}\n```\n"
        except Exception as e:
            markdown_content += f"Error reading file {file_name}: {e}\n"
    return markdown_content


def userinput_factory(userinput, files):
    if files:
        content = create_context_files(files)
        return userinput_with_files.format(content=content, input=userinput)
    return userinput


@click.command(help='Expert developer')
@click.pass_context
@userinput_argument()
@markdown_option()
@click.option('-f', '--file', multiple=True, help="File as context")
def dev(ctx, userinput, markdown, file):
    context = ctx.obj['context']
    userinput_prompt = userinput_factory(userinput, file)
    
    system_message = dev_prompt
    if markdown:
        system_message += " Output in Markdown format."

    stream = invoke_llm_stream(userinput_prompt, model=context.model, system_message=system_message)
    context.strategy.display_stream(stream)


def execute_git_diff():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
        return subprocess.run(["git", "diff", "--cached"], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return None


def execute_git_commit(message: str):
    try:
        return subprocess.run(["git", "commit", "-m", message.strip()], check=True, text=True, capture_output=True).stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


@click.command(help='Commit message generator')
@click.pass_context
@copy_option()
def commit_generator(ctx, copy):
    context = ctx.obj['context']
    diff = execute_git_diff()
    if not diff:
        context.info("No staged changes found or not a git repository.", fg="yellow")
        return
    
    system_message = "Create a short semantic commit message in English based on the details of the `git diff --cached` output provided by the user. I want only the text of the message, do not add characters like '```'"
    prompt = f"Generate the commit message for the following diff: {diff}"

    context.info("🤔 Generating commit message...", fg="yellow")
    
    # We'll use a local loop for the confirmation interactively as it was before,
    # but use context.info for logging.
    
    def generate_and_get_response(p):
        res = ""
        # Use simple color for interactive part if Rich is not used
        click.echo(click.style("", fg="yellow"), nl=False)
        for chunk in invoke_llm_stream(p, model=context.model, system_message=system_message):
            click.echo(chunk, nl=False)
            res += chunk
        click.echo(click.style("", reset=True))
        return res

    response = generate_and_get_response(prompt)

    while not click.confirm(click.style('Do you want to confirm this commit message?', fg='green')):
        feedback = click.prompt("What should be changed?", default="Change it please")
        prompt = f"This message didn't convince me: {response}. Feedback: {feedback}. Generate a new one for this diff: {diff}"
        context.info("🤔 Regenerating commit message...", fg="yellow")
        response = generate_and_get_response(prompt)

    stdout = execute_git_commit(response)
    if stdout:
        context.display(stdout)
    if copy:
        pyperclip.copy(response)

