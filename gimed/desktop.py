"""
GiMeD desktop environment installation
"""

from gimed.system import apt_update, apt_install, run
from gimed.ui import print_step, print_success, print_warning, spinner

# Packages to install per DE
DE_PACKAGES = {
    "xfce": [
        "xfce4",
        "xfce4-goodies",
        "lightdm",
    ],
    "mate": [
        "mate-desktop-environment",
        "mate-desktop-environment-extras",
        "lightdm",
    ],
    "lxde": [
        "lxde",
        "lightdm",
    ],
    "lxqt": [
        "lxqt",
        "lightdm",
    ],
}

# The session command written to ~/.xsession / startwm.sh
DE_SESSION_CMD = {
    "xfce": "startxfce4",
    "mate": "mate-session",
    "lxde": "startlxde",
    "lxqt": "startlxqt",
}

# Display manager to configure
DE_DISPLAY_MANAGER = {
    "xfce": "lightdm",
    "mate": "lightdm",
    "lxde": "lightdm",
    "lxqt": "lightdm",
}


def install_desktop(de_key, distro):
    packages = DE_PACKAGES.get(de_key)
    if not packages:
        raise ValueError(f"Unknown desktop: {de_key}")

    with spinner("Updating package lists"):
        apt_update()

    with spinner(f"Installing {de_key.upper()} desktop environment"):
        apt_install(*packages)

    # Prevent lightdm from starting on boot (we're headless, xrdp manages sessions)
    try:
        run(["systemctl", "disable", "lightdm"], check=False)
    except Exception:
        pass

    print_success(f"{de_key.upper()} installed")


def get_session_cmd(de_key):
    return DE_SESSION_CMD.get(de_key, "startxfce4")
