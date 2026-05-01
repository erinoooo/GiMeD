"""
GiMeD - Give Me a Desktop
Automatically sets up a desktop environment, XRDP, and WireGuard on headless Linux systems.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gimed.cli import main

if __name__ == "__main__":
    main()
