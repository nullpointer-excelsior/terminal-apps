import subprocess
from typing import List


def command_exists(command: str) -> bool:
    """Checks if a bash command exists."""
    try:
        subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    

class SystemCommandException(Exception): pass


class FzfCommand:
    options: List[str]

    def __init__(self, options):
        self.options = options
        if not command_exists('fzf'):
            raise SystemCommandException("fzf command not installed")

    def select_file(self, directory= '.'):
        commands = ['fzf']
        commands += self.options
        process = subprocess.Popen(
            commands, 
            cwd=directory, 
            stdout=subprocess.PIPE, 
            text=True
        )
        selected_file, _ = process.communicate()
        if not selected_file:
            return None
        return f"{directory}/{selected_file.strip()}" if not directory.endswith('/') else f"{directory}{selected_file.strip()}"

    def input_content(self, content):
        commands = ['fzf']
        commands += self.options
        result = subprocess.run(
            commands,
            input=content,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    
    def input_values(self, values):
        return self.input_content('\n'.join(values))