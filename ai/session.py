from libs.database import ChatSessionRepository, Message, create_orm_session, Session
from libs.display import display_markdown
from libs.config import config
import click
from datetime import datetime
import pyperclip
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


chatsession_repository = ChatSessionRepository(create_orm_session(config.ai_sqlite_database))


def display_sessions(sessions):
    console = Console()

    if not sessions:
        console.print("[bold red]Sessions not found.[/bold red]")
        return

    panel = Panel.fit(
        "[bold bright_white]Sessions List[/bold bright_white]",
        title="",
        border_style="bright_blue",
        box=box.DOUBLE
    )
    console.print(panel)

    table = Table(
        show_header=True,
        header_style="bold green",
        box=box.SQUARE,
        show_lines=True
    )

    table.add_column("SessionID", style="bold magenta", justify="center")
    table.add_column("Assistant", style="bold cyan", justify="center")
    table.add_column("Workspace", style="bold yellow", justify="left")
    table.add_column("Messages", style="bold blue", justify="center")

    for session in sessions:
        table.add_row(
            str(session.id),
            str(session.assistant),
            str(session.workspace),
            str(len(session.messages))
        )

    console.print(table)


def format_timestamp_message(dt: datetime) -> str:
    return dt.strftime("[%Y-%m-%d %H:%M:%S]")


@click.command(help='Administrador de sesiones')
@click.argument('operation', type=click.Choice(['list', 'current', 'read', 'clean'], case_sensitive=False))
@click.argument('session_id', type=int, required=False)
def sessions(operation, session_id):
    if operation == 'list':
        sessions = chatsession_repository.find_all()
        display_sessions(sessions)
    elif operation == 'current':
        workspace = os.getcwd()
        sessions = chatsession_repository.find_by_workspace(workspace)
        display_sessions(sessions)
    elif operation == 'read' and session_id is not None:
        session = chatsession_repository.get_session_by_id(session_id)
        if session:
            click.echo(f"SessionID: {session.id}, Assistant: {session.assistant}, Workspace: {session.workspace}, Messages: {len(session.messages)}")
            for message in session.messages:
                role = click.style("🦁 > ", fg="green") if message.role == 'user' else click.style("🤖 > ", fg="green")
                timestamp = click.style(format_timestamp_message(message.timestamp), fg='cyan')
                click.echo(f"{timestamp} {role}")
                display_markdown(message.content)
        else:
            click.echo(f"No se encontró la sesión con ID: {session_id}.")
    elif operation == 'clean' and session_id is not None:
        result = chatsession_repository.delete_session_by_id(session_id)
        if result:
            click.echo(f"Sesión con ID: {session_id} ha sido eliminada.")
        else:
            click.echo(f"No se encontró la sesión con ID: {session_id}.")
