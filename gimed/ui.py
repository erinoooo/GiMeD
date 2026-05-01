"""
GiMeD UI - Terminal UI using simple-term-menu + rich
simple-term-menu works reliably over SSH and sudo with no stdin/tty issues.
"""

import sys
from contextlib import contextmanager

from simple_term_menu import TerminalMenu
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
    console.print(f"\n  [bold]{prompt}[/]\n")
    labels = [label for label, _ in choices]

    menu = TerminalMenu(
        labels,
        title=None,
        menu_cursor="► ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
        cycle_cursor=True,
        clear_screen=False,
    )
    idx = menu.show()

    if idx is None:
        print_warning("Interrupted.")
        sys.exit(1)

    label, value = choices[idx]
    print_success(f"Selected: {label.split('—')[0].strip()}")
    return label, value


def ask_input(prompt, default=None, validator=None, error_msg="Invalid input"):
    hint = f" [{default}]" if default else ""
    console.print(f"\n  [bold]{prompt}{hint}:[/] ", end="")

    while True:
        try:
            raw = input().strip()
            if not raw and default is not None:
                return default
            if not raw:
                console.print(f"  [yellow]Please enter a value:[/] ", end="")
                continue
            if validator and not validator(raw):
                console.print(f"  [yellow]{error_msg}:[/] ", end="")
                continue
            return raw
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(1)


def ask_confirm(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    console.print(f"\n  [bold]{prompt} [{hint}]:[/] ", end="")

    while True:
        try:
            raw = input().strip().lower()
            if not raw:
                return default
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            console.print(f"  [yellow]Please enter y or n:[/] ", end="")
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(1)
