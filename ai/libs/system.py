import subprocess


def command_exists(command: str) -> bool:
    """Checks if a bash command exists."""
    try:
        subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False