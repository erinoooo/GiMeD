"""
GiMeD WireGuard installation and configuration
"""

import os
import subprocess
import ipaddress

from gimed.system import apt_install, run, systemctl, command_exists
from gimed.ui import print_step, print_success, print_warning, print_info, spinner

WG_DIR      = "/etc/wireguard"
WG_CONF     = "/etc/wireguard/wg0.conf"
CLIENT_CONF = "/root/gimed-client.conf"


def install_wireguard(distro):
    with spinner("Installing WireGuard"):
        apt_install("wireguard", "wireguard-tools")

    # Enable IP forwarding persistently
    _enable_ip_forwarding()

    print_success("WireGuard installed")


def _enable_ip_forwarding():
    sysctl_conf = "/etc/sysctl.d/99-gimed-wireguard.conf"
    with open(sysctl_conf, "w") as f:
        f.write("net.ipv4.ip_forward=1\nnet.ipv6.conf.all.forwarding=1\n")
    run(["sysctl", "--system"], check=False)


def _gen_keypair():
    """Generate a WireGuard private/public keypair. Returns (private, public)."""
    priv = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub  = subprocess.check_output(["wg", "pubkey"], input=priv.encode()).decode().strip()
    return priv, pub


def _detect_default_interface():
    """Detect the default network interface (eth0, ens3, etc.)."""
    try:
        result = subprocess.check_output(
            ["ip", "route", "show", "default"], text=True
        )
        # "default via x.x.x.x dev eth0 ..."
        parts = result.split()
        idx = parts.index("dev")
        return parts[idx + 1]
    except Exception:
        return "eth0"


def configure_wireguard(server_vpn_ip, client_vpn_ip, listen_port=51820):
    """
    Generate keypairs, write server wg0.conf, return client config dict.
    """
    os.makedirs(WG_DIR, mode=0o700, exist_ok=True)

    with spinner("Generating WireGuard keypairs"):
        server_priv, server_pub = _gen_keypair()
        client_priv, client_pub = _gen_keypair()

    iface = _detect_default_interface()

    server_conf = f"""\
[Interface]
Address = {server_vpn_ip}/24
ListenPort = {listen_port}
PrivateKey = {server_priv}

# NAT masquerading so VPN clients can reach the server
PostUp   = iptables -A FORWARD -i wg0 -j ACCEPT; \\
           iptables -A FORWARD -o wg0 -j ACCEPT; \\
           iptables -t nat -A POSTROUTING -o {iface} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; \\
           iptables -D FORWARD -o wg0 -j ACCEPT; \\
           iptables -t nat -D POSTROUTING -o {iface} -j MASQUERADE

[Peer]
# GiMeD client
PublicKey  = {client_pub}
AllowedIPs = {client_vpn_ip}/32
"""

    with open(WG_CONF, "w") as f:
        f.write(server_conf)
    os.chmod(WG_CONF, 0o600)

    # Get public IP for client config endpoint
    public_ip = _get_public_ip()

    client_conf_text = f"""\
[Interface]
Address    = {client_vpn_ip}/24
PrivateKey = {client_priv}
DNS        = 1.1.1.1

[Peer]
PublicKey           = {server_pub}
Endpoint            = {public_ip}:{listen_port}
AllowedIPs          = {server_vpn_ip}/32
PersistentKeepalive = 25
"""

    with spinner("Starting WireGuard"):
        systemctl("enable", "wg-quick@wg0")
        systemctl("start",  "wg-quick@wg0")

    print_success(f"WireGuard running — server VPN IP: {server_vpn_ip}")

    return {
        "text":       client_conf_text,
        "client_ip":  client_vpn_ip,
        "server_ip":  server_vpn_ip,
        "public_ip":  public_ip,
        "port":       listen_port,
    }


def _get_public_ip():
    """Try to detect the server's public IP."""
    methods = [
        ["curl", "-s", "--max-time", "5", "https://api.ipify.org"],
        ["curl", "-s", "--max-time", "5", "https://ifconfig.me"],
    ]
    for cmd in methods:
        try:
            ip = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
            if ip:
                return ip
        except Exception:
            pass
    return "YOUR_SERVER_PUBLIC_IP"


def output_client_config(wg_config, mode):
    """Output client config as terminal print, file, QR, or all."""
    text  = wg_config["text"]
    modes = ["terminal", "file", "qr"] if mode == "all" else [mode]

    if "terminal" in modes:
        _print_client_config(text)

    if "file" in modes:
        _save_client_config(text)

    if "qr" in modes:
        _print_qr(text)


def _print_client_config(text):
    print()
    print_info("─" * 52)
    print_info("  WireGuard Client Config (copy to your device)  ")
    print_info("─" * 52)
    for line in text.splitlines():
        print_info(line)
    print_info("─" * 52)


def _save_client_config(text):
    with open(CLIENT_CONF, "w") as f:
        f.write(text)
    os.chmod(CLIENT_CONF, 0o600)
    print_success(f"Client config saved to: {CLIENT_CONF}")


def _print_qr(text):
    # Try qrencode
    if command_exists("qrencode"):
        try:
            subprocess.run(
                ["qrencode", "-t", "ansiutf8"],
                input=text.encode(),
                check=True,
            )
            return
        except Exception:
            pass

    # Try to install it
    try:
        from gimed.system import apt_install
        apt_install("qrencode")
        subprocess.run(
            ["qrencode", "-t", "ansiutf8"],
            input=text.encode(),
            check=True,
        )
    except Exception:
        print_warning("Could not generate QR code (qrencode unavailable). Falling back to file output.")
        _save_client_config(text)
