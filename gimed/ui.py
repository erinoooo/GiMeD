"""
GiMeD UI - Terminal UI using questionary + rich
"""

import sys
import os

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from contextlib import contextmanager

console = Console()

BANNER = r"""
  ██████╗ ██╗███╗   ███╗███████╗██████╗
 ██╔════╝ ██║████╗ ████║██╔════╝██╔══██╗
 ██║  ███╗██║██╔████╔██║█████╗  ██║  ██║
 ██║   ██║██║██║╚██╔╝██║██╔══╝  ██║  ██║
 ╚██████╔╝██║██║ ╚═╝ ██║███████╗██████╔╝
  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝
"""

Q_STYLE = Style([
    ("qmark",        "fg:#00d7ff bold"),
    ("question",     "bold"),
    ("answer",       "fg:#00ff99 bold"),
    ("pointer",      "fg:#00d7ff bold"),
    ("highlighted",  "fg:#00d7ff bold"),
    ("selected",     "fg:#00ff99"),
    ("instruction",  "fg:#888888"),
])


def print_banner():
    console.print(BANNER, style="cyan", highlight=False)
    console.print("  Give Me a Desktop".center(46), style="bold white")
    console.print("  Headless Linux → Desktop in minutes\n".center(46), style="dim")
    console.print()


def print_section(title):
    console.print()
    console.print(Panel(f"[bold white]{title}[/]", border_style="cyan", padding=(0, 1)))


def print_step(msg):
    console.print(f"  [blue]→[/] {msg}")


def print_success(msg):
    console.print(f"  [green]✓[/] {msg}")


def print_error(msg):
    console.print(f"  [red]✗[/] {msg}", stderr=True)


def print_warning(msg):
    console.print(f"  [yellow]⚠[/] {msg}")


def print_info(msg):
    console.print(f"   [dim]{msg}[/]")


@contextmanager
def spinner(label):
    """Context manager that shows a rich spinner while work runs."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(label, total=None)
        yield
    print_step(label)


def ask_select(prompt, choices):
    """
    choices: list of (label, value) tuples
    Returns (label, value) of selected item.
    """
    labels = [label for label, _ in choices]
    result = questionary.select(
        prompt,
        choices=labels,
        style=Q_STYLE,
    ).ask()

    if result is None:
        print_warning("Interrupted.")
        sys.exit(1)

    value = dict(choices)[result]
    return result, value


def ask_input(prompt, default=None, validator=None, error_msg="Invalid input"):
    """Prompt for a string value with optional default and validator."""
    def _validate(val):
        if not val and default is None:
            return "Please enter a value."
        if val and validator and not validator(val):
            return error_msg
        return True

    result = questionary.text(
        prompt,
        default=default or "",
        validate=_validate,
        style=Q_STYLE,
    ).ask()

    if result is None:
        print_warning("Interrupted.")
        sys.exit(1)

    return result if result else default


def ask_confirm(prompt, default=True):
    """Yes/no prompt. Returns bool."""
    result = questionary.confirm(
        prompt,
        default=default,
        style=Q_STYLE,
    ).ask()

    if result is None:
        sys.exit(1)

    return result