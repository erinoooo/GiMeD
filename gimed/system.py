"""
GiMeD system detection utilities
"""

import os
import subprocess
import shutil


SUPPORTED = {
    "ubuntu": ["20.04", "22.04", "24.04"],
    "debian": ["10", "11", "12"],
}

# Map distro codenames to versions for robustness
CODENAME_MAP = {
    "focal":   ("ubuntu", "20.04"),
    "jammy":   ("ubuntu", "22.04"),
    "noble":   ("ubuntu", "24.04"),
    "buster":  ("debian", "10"),
    "bullseye":("debian", "11"),
    "bookworm":("debian", "12"),
}


def check_root():
    return os.geteuid() == 0


def detect_distro():
    """
    Parse /etc/os-release and return a dict with keys:
    id, version, version_id, pretty_name, codename
    """
    info = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    info[k.lower()] = v.strip('"')
    except FileNotFoundError:
        pass

    return {
        "id":           info.get("id", "unknown").lower(),
        "version":      info.get("version_id", ""),
        "pretty_name":  info.get("pretty_name", "Unknown"),
        "codename":     info.get("version_codename", ""),
        "id_like":      info.get("id_like", ""),
    }


def check_supported_distro(distro):
    did = distro["id"]
    ver = distro["version"]
    codename = distro["codename"].lower()

    # Direct match
    if did in SUPPORTED:
        # Accept any version — we'll warn but not block on minor versions
        return True

    # Codename match (some Ubuntu variants report differently)
    if codename in CODENAME_MAP:
        return True

    # Ubuntu-based (Mint, Pop!_OS, etc.) — allow with warning
    if "ubuntu" in distro.get("id_like", ""):
        return True

    return False


def run(cmd, check=True, capture=False):
    """
    Run a shell command. cmd can be a list or string.
    Returns CompletedProcess.
    """
    kwargs = dict(
        shell=isinstance(cmd, str),
        check=check,
    )
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
        kwargs["text"] = True

    return subprocess.run(cmd, **kwargs)


def apt_install(*packages):
    """Install packages via apt-get non-interactively."""
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    subprocess.run(
        ["apt-get", "install", "-y", "--no-install-recommends"] + list(packages),
        check=True,
        env=env,
    )


def apt_update():
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    subprocess.run(["apt-get", "update", "-y"], check=True, env=env)


def systemctl(action, service):
    subprocess.run(["systemctl", action, service], check=True)


def command_exists(cmd):
    return shutil.which(cmd) is not None
