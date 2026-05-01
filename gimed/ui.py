"""
GiMeD UI - Terminal UI using InquirerPy + rich
InquirerPy handles piped stdin, sudo, SSH, and non-tty environments correctly.
"""

import sys
from contextlib import contextmanager

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

BANNER = r"""
  ██████╗ ██╗███╗   ███╗███████╗██████╗
 ██╔════╝ ██║████╗ ████║██╔════╝██╔══██╗
 ██║  ███╗██║██╔████╔██║█████╗  ██║  ██║
 ██║   ██║██║██║╚██╔╝██║██╔══╝  ██║  ██║
 ╚██████╔╝██║██║ ╚═╝ ██║███████╗██████╔╝
  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝
"""


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
    result = inquirer.select(
        message=prompt,
        choices=[Choice(value=value, name=label) for label, value in choices],
        mandatory=True,
    ).execute()

    if result is None:
        print_warning("Interrupted.")
        sys.exit(1)

    label = next(label for label, value in choices if value == result)
    print_success(f"Selected: {label.split('—')[0].strip()}")
    return label, result


def ask_input(prompt, default=None, validator=None, error_msg="Invalid input"):
    def _validate(val):
        if not val and default is None:
            return False
        if val and validator and not validator(val):
            return False
        return True

    result = inquirer.text(
        message=prompt,
        default=default or "",
        validate=_validate,
        invalid_message=error_msg,
        mandatory=True,
    ).execute()

    if result is None:
        print_warning("Interrupted.")
        sys.exit(1)

    return result if result else default


def ask_confirm(prompt, default=True):
    result = inquirer.confirm(
        message=prompt,
        default=default,
        mandatory=True,
    ).execute()

    if result is None:
        sys.exit(1)

    return result
