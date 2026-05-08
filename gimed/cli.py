"""
GiMeD CLI - Interactive TUI for setup
"""

import sys
import os
import subprocess
import time

from gimed.ui import (
    print_banner,
    print_step,
    print_success,
    print_error,
    print_warning,
    print_info,
    ask_select,
    ask_input,
    ask_confirm,
    print_section,
    spinner,
)
from gimed.system import (
    check_root,
    detect_distro,
    check_supported_distro,
    run,
)
from gimed.desktop import install_desktop
from gimed.xrdp import install_xrdp, configure_xrdp, generate_ssl_cert
from gimed.wireguard import install_wireguard, configure_wireguard, output_client_config


DESKTOP_CHOICES = [
    ("XFCE   — Lightweight, fast, excellent xrdp compatibility  [Recommended]", "xfce"),
    ("MATE   — Classic desktop, Windows-like feel, very stable", "mate"),
    ("LXDE   — Ultra-lightweight, great for low-RAM servers", "lxde"),
    ("LXQt   — Modern LXDE successor, Qt-based", "lxqt"),
]

CLIENT_OUTPUT_CHOICES = [
    ("Print to terminal", "terminal"),
    ("Save to file",      "file"),
    ("QR code (scan with WireGuard mobile app)", "qr"),
    ("All of the above", "all"),
]

# State file written before reboot, checked on next run
STATE_FILE = "/var/lib/gimed/state"


def _read_state():
    """Return dict of saved state, or empty dict."""
    if not os.path.exists(STATE_FILE):
        return {}
    state = {}
    try:
        with open(STATE_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    state[k.strip()] = v.strip()
    except Exception:
        pass
    return state


def _write_state(**kwargs):
    """Persist key=value pairs to state file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    existing = _read_state()
    existing.update(kwargs)
    with open(STATE_FILE, "w") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")


def _clear_state():
    try:
        os.remove(STATE_FILE)
    except Exception:
        pass


def _do_upgrade_and_reboot(distro):
    """Run apt update + upgrade, save state, then reboot."""
    print_section("System Update")
    print_warning("GiMeD will now update and upgrade the system.")
    print_warning("The server will reboot automatically when done.")
    print_warning("Run  sudo gimed  again after the reboot to continue setup.")
    print_info("")

    if not ask_confirm("Proceed with update + reboot?", default=True):
        print_warning("Skipping update. Packages may be outdated.")
        _write_state(upgrade_done="skipped")
        return

    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"

    with spinner("Running apt update"):
        subprocess.run(["apt", "update", "-y"], check=True, env=env)

    with spinner("Running apt upgrade"):
        subprocess.run(
            ["apt", "upgrade", "-y",
             "-o", "Dpkg::Options::=--force-confdef",
             "-o", "Dpkg::Options::=--force-confold"],
            check=True, env=env,
        )

    _write_state(upgrade_done="yes")

    print_success("System upgraded. Rebooting in 5 seconds...")
    print_info("Run  sudo gimed  after the reboot to continue.")
    time.sleep(5)
    os.execv("/sbin/reboot", ["reboot"])


def main():
    print_banner()

    # ── Preflight ──────────────────────────────────────────────────────────
    print_section("Preflight Checks")

    if not check_root():
        print_error("GiMeD must be run as root (use sudo).")
        sys.exit(1)
    print_success("Running as root")

    distro = detect_distro()
    if not check_supported_distro(distro):
        print_error(f"Unsupported distro: {distro['id']} {distro['version']}")
        print_info("GiMeD currently supports Ubuntu and Debian.")
        sys.exit(1)
    print_success(f"Detected: {distro['pretty_name']}")

    # ── Upgrade check ──────────────────────────────────────────────────────
    state = _read_state()
    upgrade_done = state.get("upgrade_done", "no")

    if upgrade_done == "no":
        # First run — warn user and offer upgrade + reboot
        print_section("System Update")
        print_warning("For the most up-to-date packages, GiMeD recommends")
        print_warning("running a full system upgrade before installing.")
        print_info("The system will reboot once, then you run  sudo gimed  again.")
        print_info("")
        _do_upgrade_and_reboot(distro)
        # If user skipped, fall through to setup immediately
    elif upgrade_done == "yes":
        print_success("System already upgraded — continuing setup")
    elif upgrade_done == "skipped":
        print_warning("Upgrade was skipped — packages may not be latest")

    # ── Desktop environment ────────────────────────────────────────────────
    print_section("Desktop Environment")
    de_label, de_key = ask_select(
        "Which desktop environment would you like?",
        DESKTOP_CHOICES,
    )

    # ── WireGuard config ───────────────────────────────────────────────────
    print_section("WireGuard VPN")

    wg_port = ask_input(
        "WireGuard listen port",
        default="51820",
        validator=lambda v: v.isdigit() and 1 <= int(v) <= 65535,
        error_msg="Must be a valid port number (1-65535)",
    )

    wg_server_ip = ask_input(
        "VPN subnet (server will be .1)",
        default="10.99.0",
        validator=lambda v: len(v.split(".")) == 3,
        error_msg="Enter the first 3 octets, e.g. 10.99.0",
    )

    wg_client_ip = f"{wg_server_ip}.2"
    wg_server_vpn_ip = f"{wg_server_ip}.1"

    client_output_label, client_output = ask_select(
        "How should GiMeD deliver the WireGuard client config?",
        CLIENT_OUTPUT_CHOICES,
    )

    # ── SSL cert ───────────────────────────────────────────────────────────
    print_section("SSL Certificate")
    want_ssl = ask_confirm("Generate a self-signed SSL certificate for XRDP?", default=True)

    # ── Confirm ────────────────────────────────────────────────────────────
    print_section("Ready to Install")
    print_info(f"  Desktop  : {de_label.strip()}")
    print_info(f"  xrdp     : port 3389, SSL={'yes' if want_ssl else 'no'}")
    print_info(f"  WireGuard: UDP {wg_port}, server {wg_server_vpn_ip}, client {wg_client_ip}")

    if not ask_confirm("Proceed with installation?", default=True):
        print_warning("Aborted.")
        sys.exit(0)

    # ── Install ────────────────────────────────────────────────────────────
    print_section("Installing Desktop Environment")
    install_desktop(de_key, distro)

    print_section("Installing & Configuring XRDP")
    install_xrdp(distro)
    configure_xrdp(de_key)
    if want_ssl:
        generate_ssl_cert()

    print_section("Installing & Configuring WireGuard")
    install_wireguard(distro)
    wg_config = configure_wireguard(
        server_vpn_ip=wg_server_vpn_ip,
        client_vpn_ip=wg_client_ip,
        listen_port=int(wg_port),
    )

    # ── Client config output ───────────────────────────────────────────────
    print_section("WireGuard Client Configuration")
    output_client_config(wg_config, client_output)

    # ── Done — clear state so a fresh run works correctly ─────────────────
    _clear_state()

    print_section("All Done!")
    print_success("GiMeD setup complete.")
    print_info("")
    print_info("Next steps:")
    print_info("  1. Import the WireGuard client config on your device")
    print_info("  2. Connect to the VPN")
    print_info(f"  3. RDP to  {wg_server_vpn_ip}:3389")
    print_info("")
    print_warning("Port 3389 is NOT exposed to the internet — only WireGuard UDP port is open.")
