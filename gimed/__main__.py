"""
GiMeD - Give Me a Desktop
Automatically sets up a desktop environment, XRDP, and WireGuard on headless Linux systems.
"""

import sys
import os

# When launched via curl|bash or sudo, fd 0 may be a pipe rather than the
# terminal. Reopen stdin from /dev/tty before prompt_toolkit initialises so
# questionary gets a real tty to work with.
if not sys.stdin.isatty():
    try:
        sys.stdin = open("/dev/tty", "r")
    except OSError:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gimed.cli import main

if __name__ == "__main__":
    main()
