"""
GiMeD CLI - Interactive TUI for setup
"""

import sys
import os
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

    # ── Desktop environment ────────────────────────────────────────────────
    print_section("Desktop Environment")
    de_label, de_key = ask_select(
        "Which desktop environment would you like?",
        DESKTOP_CHOICES,
    )
    print_info(f"Selected: {de_label.strip()}")

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
    print_info(f"  Desktop : {de_label.strip()}")
    print_info(f"  xrdp    : port 3389, SSL={'yes' if want_ssl else 'no'}")
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

    # ── Done ───────────────────────────────────────────────────────────────
    print_section("All Done!")
    print_success("GiMeD setup complete.")
    print_info("")
    print_info("Next steps:")
    print_info("  1. Import the WireGuard client config on your device")
    print_info("  2. Connect to the VPN")
    print_info(f"  3. RDP to  {wg_server_vpn_ip}:3389")
    print_info("")
    print_warning("Port 3389 is NOT exposed to the internet — only WireGuard UDP port is open.")
