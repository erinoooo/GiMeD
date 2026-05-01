"""
GiMeD XRDP installation and configuration
"""

import os
import subprocess
import textwrap

from gimed.system import apt_install, run, systemctl, command_exists
from gimed.desktop import get_session_cmd
from gimed.ui import print_step, print_success, print_warning, spinner

XRDP_CONF = "/etc/xrdp/xrdp.ini"
STARTWM   = "/etc/xrdp/startwm.sh"
CERT_PATH = "/etc/xrdp/cert.pem"
KEY_PATH  = "/etc/xrdp/key.pem"


def install_xrdp(distro):
    with spinner("Installing xrdp"):
        apt_install("xrdp", "xorgxrdp")

    with spinner("Enabling xrdp service"):
        systemctl("enable", "xrdp")

    # Add xrdp user to ssl-cert group (needed on Ubuntu/Debian)
    try:
        run(["usermod", "-aG", "ssl-cert", "xrdp"], check=False)
    except Exception:
        pass

    print_success("xrdp installed")


def configure_xrdp(de_key):
    session_cmd = get_session_cmd(de_key)

    # Write ~/.xsession for root and any existing human users
    _write_xsession(session_cmd, "/root/.xsession")

    # Also patch startwm.sh so it works for all users connecting via xrdp
    _patch_startwm(session_cmd)

    with spinner("Restarting xrdp"):
        systemctl("restart", "xrdp")

    print_success(f"xrdp configured to launch {de_key.upper()}")


def _write_xsession(session_cmd, path):
    content = f"#!/bin/sh\nexec {session_cmd}\n"
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o755)


def _patch_startwm(session_cmd):
    """
    Replace the exec lines at the end of startwm.sh with our DE's session command.
    Keeps the environment setup at the top intact.
    """
    if not os.path.exists(STARTWM):
        content = f"#!/bin/sh\nexec {session_cmd}\n"
        with open(STARTWM, "w") as f:
            f.write(content)
        os.chmod(STARTWM, 0o755)
        return

    with open(STARTWM) as f:
        lines = f.readlines()

    # Strip any existing exec lines and append ours
    filtered = [l for l in lines if not l.strip().startswith("exec ")]
    filtered.append(f"\nexec {session_cmd}\n")

    with open(STARTWM, "w") as f:
        f.writelines(filtered)
    os.chmod(STARTWM, 0o755)


def generate_ssl_cert():
    import socket
    hostname = socket.gethostname()

    with spinner("Generating self-signed SSL certificate"):
        run([
            "openssl", "req", "-x509", "-nodes",
            "-newkey", "rsa:2048",
            "-keyout", KEY_PATH,
            "-out",    CERT_PATH,
            "-days",   "3650",
            "-subj",   f"/CN={hostname}",
        ])

    # Fix ownership
    try:
        run(["chown", "xrdp:xrdp", CERT_PATH, KEY_PATH], check=False)
    except Exception:
        pass
    os.chmod(KEY_PATH, 0o600)

    # Point xrdp.ini at the new certs
    _patch_xrdp_ini_certs()

    with spinner("Restarting xrdp after cert update"):
        systemctl("restart", "xrdp")

    print_success(f"SSL cert generated (valid 10 years): {CERT_PATH}")


def _patch_xrdp_ini_certs():
    if not os.path.exists(XRDP_CONF):
        return

    with open(XRDP_CONF) as f:
        content = f.read()

    import re
    content = re.sub(r"^certificate=.*$", f"certificate={CERT_PATH}", content, flags=re.MULTILINE)
    content = re.sub(r"^key_file=.*$",    f"key_file={KEY_PATH}",      content, flags=re.MULTILINE)

    with open(XRDP_CONF, "w") as f:
        f.write(content)
