"""
GiMeD UI - Terminal UI helpers using only stdlib + optional rich
"""

import sys
import os
import time
import threading
import itertools

# Try rich for prettier output, fall back to plain ANSI
try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich import print as rprint
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None

# ANSI codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"
WHITE  = "\033[97m"

BANNER = r"""
  ██████╗ ██╗███╗   ███╗███████╗██████╗
 ██╔════╝ ██║████╗ ████║██╔════╝██╔══██╗
 ██║  ███╗██║██╔████╔██║█████╗  ██║  ██║
 ██║   ██║██║██║╚██╔╝██║██╔══╝  ██║  ██║
 ╚██████╔╝██║██║ ╚═╝ ██║███████╗██████╔╝
  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝
"""

def _c(color, text):
    """Wrap text in ANSI color if stdout is a tty."""
    if sys.stdout.isatty():
        return f"{color}{text}{RESET}"
    return text

def print_banner():
    print(_c(CYAN, BANNER))
    print(_c(BOLD + WHITE, "  Give Me a Desktop".center(46)))
    print(_c(DIM,           "  Headless Linux → Desktop in minutes\n".center(46)))
    print()

def print_section(title):
    width = 50
    line = "─" * width
    print()
    print(_c(CYAN, f"┌{line}┐"))
    print(_c(CYAN, "│") + _c(BOLD + WHITE, f"  {title}".ljust(width)) + _c(CYAN, "│"))
    print(_c(CYAN, f"└{line}┘"))

def print_step(msg):
    print(_c(BLUE, "  →") + f" {msg}")

def print_success(msg):
    print(_c(GREEN, "  ✓") + f" {msg}")

def print_error(msg):
    print(_c(RED, "  ✗") + f" {msg}", file=sys.stderr)

def print_warning(msg):
    print(_c(YELLOW, "  ⚠") + f" {msg}")

def print_info(msg):
    print(_c(DIM, "   ") + f"{msg}")


class spinner:
    """Context manager that shows a spinner while work happens."""
    FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

    def __init__(self, label):
        self.label = label
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        for frame in itertools.cycle(self.FRAMES):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r  {_c(CYAN, frame)} {self.label} ")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.label) + 8) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        # Only spin when output is NOT a tty (e.g. piped/logged).
        # When interactive, a spinner conflicts with input() — just print a step line.
        if not sys.stdout.isatty():
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        else:
            print_step(self.label)
        return self

    def __exit__(self, *_):
        self._stop.set()
        if self._thread:
            self._thread.join()


def ask_select(prompt, choices):
    """
    choices: list of (label, value) tuples
    Returns (label, value) of selected item.
    """
    print()
    print(_c(BOLD, f"  {prompt}"))
    print()
    for i, (label, _) in enumerate(choices, 1):
        print(f"    {_c(CYAN, str(i) + ')')} {label}")
    print()

    while True:
        try:
            raw = input(_c(DIM, "  Enter number: ")).strip()
            if not raw:
                continue  # ignore empty lines silently
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                label, value = choices[idx]
                print_success(f"Selected: {label.split('—')[0].strip()}")
                return label, value
            else:
                print_warning(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print_warning("Please enter a number.")
        except EOFError:
            continue  # ignore stray EOF bytes
        except KeyboardInterrupt:
            print()
            print_warning("Interrupted.")
            sys.exit(1)


def ask_input(prompt, default=None, validator=None, error_msg="Invalid input"):
    """Prompt for a string value with optional default and validator."""
    hint = f" [{default}]" if default else ""
    print()
    while True:
        try:
            raw = input(_c(BOLD, f"  {prompt}{hint}: ")).strip()
            if not raw and default is not None:
                raw = default
            if not raw:
                continue  # no default, empty input — silently retry
            if validator and not validator(raw):
                print_warning(error_msg)
                continue
            return raw
        except EOFError:
            continue
        except KeyboardInterrupt:
            print()
            print_warning("Interrupted.")
            sys.exit(1)


def ask_confirm(prompt, default=True):
    """Yes/no prompt. Returns bool."""
    hint = "[Y/n]" if default else "[y/N]"
    print()
    while True:
        try:
            raw = input(_c(BOLD, f"  {prompt} {_c(DIM, hint)}: ")).strip().lower()
            if not raw:
                return default
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            print_warning("Please enter y or n.")
        except EOFError:
            continue
        except KeyboardInterrupt:
            print()
            sys.exit(1)