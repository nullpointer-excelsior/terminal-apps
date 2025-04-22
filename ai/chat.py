from libs.chatgpt import chat_with_chatgpt, get_stream_completion
from libs.cli import get_context_options, markdown_option
from libs.display import display_markdown, process_markdown, display_highlighted_code
from libs.system import FzfCommand, SystemCommandException
from libs.config import config
import click
import pyperclip
import re
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import os
import tempfile


default_system_prompt = """Eres un útil asistente que resolverá todas las dudas del usuario y responderás de forma directa y sin explicaciones, a menos que el usuario te lo indique."""


def create_prompt():
    template_path = default_system_prompt

    try:
        fzf = FzfCommand([
            "--preview-window=right:70%:wrap", 
            "--preview", "bat --style=numbers --color=always {}"
        ])
        templates_dir = f"{config.ai_prompt_resources}/templates/"
        selected = fzf.select_file(templates_dir)

        if selected is not None:
            template_path = selected

    except SystemCommandException:
        click.echo(click.style("Fzf not installed", fg="red"))
        click.echo(click.style(f"\t* Using default prompt: {default_system_prompt}", fg="yellow"))
        return template_path

    content = Path(template_path).read_text()
    variables = set(re.findall(r"\{([^}]+)\}", content))

    for var in variables:
        value = input(
            f"\nEnter template param for {click.style(f'${var}', fg='yellow')}: "
        ).strip()
        content = content.replace(f"{{{var}}}", value if value else '')

    return content


def get_last_assistant_response(messages):
    return messages[-1].get('content') if len(messages) > 1 else ''


@dataclass
class ChatCommand:
    EXIT = ['--exit', 'exit']
    MARKDOWN = ['--markdown', '-md']
    COPY = ['--copy', '-c']
    CODE = ['--code', '-cd']


@dataclass
class PromptCommand:
    FILES = '@files'


@dataclass
class UserPrompt:
    prompt: str

    def is_exit_command(self):
        return self.prompt in ChatCommand.EXIT
    
    def is_markdown_command(self):
        return any(cmd in self.prompt for cmd in ChatCommand.MARKDOWN)
    
    def is_copy_command(self):
        return self.prompt.strip() in ChatCommand.COPY
    
    def is_code_command(self):
        return self.prompt in ChatCommand.CODE
    
    def is_files_present(self):
        return PromptCommand.FILES in self.prompt
    
    def content(self):
        content = self.prompt
        for cmd in ChatCommand.MARKDOWN:
            content = content.replace(cmd, '')
        return content.strip()
    

def copy_last_assistant_message(messages):
    last_message_content = get_last_assistant_response(messages)
    if last_message_content == '':
        print(click.style("🤖 > ", fg="green"), end="", flush=True)
        print("Nada que copiar!!")
    else:
        pyperclip.copy(last_message_content)


def copy_code(messages):

    def extract_code_snippets(markdown_text):
        pattern = r"```(\w+)?\n(.*?)```"
        return re.findall(pattern, markdown_text, re.DOTALL)
    
    def get_snippet_code(filename):
        markdown = Path(filename).read_text()
        match = re.search(r"```(?:[\w+]*\n)?(.*?)```", markdown, re.DOTALL)
        return match.group(1) if match else ''
    
    def write_snippet_file(snippet, index, directory):
        filename = f"snippet_{index + 1}.md"
        path = os.path.join(directory, filename)
        with open(path, "w") as f:
            f.write(f"# Snippet {index + 1}\n\n")
            f.write(f"```{snippet[0].strip()}\n{snippet[1]}\n```")
        return filename.replace(".md", "")
    
    last_message = get_last_assistant_response(messages)
    snippets = extract_code_snippets(last_message)
    temp_dir = tempfile.mkdtemp()
    snippet_list = [write_snippet_file(snippet, i, temp_dir) for i, snippet in enumerate(snippets)]

    fzf = FzfCommand([
        '--preview',
        "bat --style=numbers --color=always " + temp_dir + "/{}.md",
    ])
    file_selected = fzf.input_values(snippet_list)
    
    if file_selected != '':
        selected_code = get_snippet_code(f"{temp_dir}/{file_selected}.md")
        pyperclip.copy(selected_code)



@click.command(help="Chatgpt session in terminal")
@click.pass_context
@click.option("-p", "--prompt", is_flag=True, help="Select a prompt from resources")
@markdown_option()
def chat(ctx, prompt, markdown):
    model, temperature = get_context_options(ctx)
    
    print_command = lambda cmd, desc: click.echo(f"{click.style(cmd, fg='cyan')}: {desc}")
    click.echo(click.style("\nTerminal AI assistant\n", fg="cyan"))
    click.echo(click.style("Chat commands:", fg="yellow"))
    print_command(",".join(ChatCommand.EXIT), "exit from chat")
    print_command(",".join(ChatCommand.MARKDOWN), "show response in markdown")
    print_command(",".join(ChatCommand.COPY), "copy the AI response")
    print_command(",".join(ChatCommand.CODE), "select and copy code snippet from last assistant response")
    print()
    
    messages = [
        {
            "role": "system",
            "content": create_prompt() if prompt else default_system_prompt,
        },
    ]

    def stream_chat():
        response = display_highlighted_code(lambda: get_stream_completion(messages, model=model, temperature=temperature))
        messages.append({"role": "system", "content": response})

    def markdown_chat():
        response = chat_with_chatgpt(messages, model, temperature, stream=False)
        messages.append({"role": "system", "content": response})
        return response

    while True:
        try:
            raw_input = input(click.style("🦁 > ", fg="green"))
            chat_user_prompt = UserPrompt(raw_input)
            
            if chat_user_prompt.is_exit_command():
                break

            if chat_user_prompt.is_copy_command():
                copy_last_assistant_message(messages)
                continue

            if chat_user_prompt.is_code_command():
                copy_code(messages)
                continue

            if chat_user_prompt.is_files_present():
                
                continue

            print(click.style("🤖 > ", fg="green"), end="", flush=True)

            messages.append({"role": "user", "content": chat_user_prompt.content()})
            
            if chat_user_prompt.is_markdown_command():
                display_markdown(markdown_chat())
                continue
            else:
                process_markdown(
                    markdown,
                    lambda: markdown_chat(),
                    lambda: stream_chat()
                )

        except Exception as e:
            print(f"Unhandled chat error: {e}")
        
