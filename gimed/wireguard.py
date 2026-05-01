"""
GiMeD WireGuard installation and configuration
"""

import os
import subprocess

from gimed.system import apt_install, run, systemctl, command_exists
from gimed.ui import print_step, print_success, print_warning, print_info, spinner

WG_DIR      = "/etc/wireguard"
WG_CONF     = "/etc/wireguard/wg0.conf"
CLIENT_CONF = "/root/gimed-client.conf"


def install_wireguard(distro):
    with spinner("Installing WireGuard"):
        apt_install("wireguard", "wireguard-tools", "iptables")

    # On Ubuntu 24.04 / EC2, ensure iptables-legacy is used so wg-quick
    # PostUp/PostDown rules work. nftables is the default but wg-quick
    # uses iptables syntax.
    _fix_iptables()
    _enable_ip_forwarding()

    print_success("WireGuard installed")


def _fix_iptables():
    """Switch to iptables-legacy if nftables is the current default."""
    try:
        # Check if update-alternatives knows about iptables
        result = subprocess.run(
            ["update-alternatives", "--query", "iptables"],
            capture_output=True, text=True
        )
        if "iptables-legacy" in result.stdout:
            run(["update-alternatives", "--set", "iptables",
                 "/usr/sbin/iptables-legacy"], check=False)
            run(["update-alternatives", "--set", "ip6tables",
                 "/usr/sbin/ip6tables-legacy"], check=False)
    except Exception:
        pass


def _enable_ip_forwarding():
    sysctl_conf = "/etc/sysctl.d/99-gimed-wireguard.conf"
    with open(sysctl_conf, "w") as f:
        f.write("net.ipv4.ip_forward=1\nnet.ipv6.conf.all.forwarding=1\n")
    run(["sysctl", "--system"], check=False)


def _gen_keypair():
    priv = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub  = subprocess.check_output(["wg", "pubkey"], input=priv.encode()).decode().strip()
    return priv, pub


def _detect_default_interface():
    try:
        result = subprocess.check_output(
            ["ip", "route", "show", "default"], text=True
        )
        parts = result.split()
        idx = parts.index("dev")
        return parts[idx + 1]
    except Exception:
        return "eth0"


def configure_wireguard(server_vpn_ip, client_vpn_ip, listen_port=51820):
    os.makedirs(WG_DIR, mode=0o700, exist_ok=True)

    with spinner("Generating WireGuard keypairs"):
        server_priv, server_pub = _gen_keypair()
        client_priv, client_pub = _gen_keypair()

    iface = _detect_default_interface()

    # Use single-line PostUp/PostDown — wg-quick handles them line by line
    server_conf = f"""\
[Interface]
Address = {server_vpn_ip}/24
ListenPort = {listen_port}
PrivateKey = {server_priv}
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o {iface} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o {iface} -j MASQUERADE

[Peer]
# GiMeD client
PublicKey  = {client_pub}
AllowedIPs = {client_vpn_ip}/32
"""

    with open(WG_CONF, "w") as f:
        f.write(server_conf)
    os.chmod(WG_CONF, 0o600)

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
        _start_wireguard()

    return {
        "text":       client_conf_text,
        "client_ip":  client_vpn_ip,
        "server_ip":  server_vpn_ip,
        "public_ip":  public_ip,
        "port":       listen_port,
    }


def _start_wireguard():
    """Start WireGuard, with a helpful error message if it fails."""
    try:
        systemctl("start", "wg-quick@wg0")
        print_success("WireGuard started successfully")
    except subprocess.CalledProcessError:
        # Capture journal output for diagnosis
        journal = subprocess.run(
            ["journalctl", "-u", "wg-quick@wg0", "-n", "20", "--no-pager"],
            capture_output=True, text=True
        ).stdout.strip()

        print_warning("WireGuard failed to start. Checking logs...")
        print_info("")

        # Common cause on EC2/Ubuntu 24.04: iptables nat table missing
        if "Table does not exist" in journal or "iptables" in journal.lower():
            print_warning("iptables NAT module not available. Trying nftables fallback...")
            _patch_conf_to_nftables()
            try:
                systemctl("start", "wg-quick@wg0")
                print_success("WireGuard started with nftables")
                return
            except subprocess.CalledProcessError:
                pass

        # Print last journal lines so user can see what went wrong
        print_warning("WireGuard service log:")
        for line in journal.splitlines()[-10:]:
            print_info(f"  {line}")
        print_warning("WireGuard did not start. The config is saved — you can start it manually:")
        print_info("  sudo systemctl start wg-quick@wg0")
        print_info("  sudo journalctl -u wg-quick@wg0 -n 30")


def _patch_conf_to_nftables():
    """Replace iptables PostUp/PostDown with nftables equivalents."""
    with open(WG_CONF) as f:
        content = f.read()

    iface = _detect_default_interface()

    # Replace PostUp/PostDown with nftables syntax
    import re
    content = re.sub(r"PostUp = .*", (
        f"PostUp = nft add table ip nat; "
        f"nft add chain ip nat postrouting {{ type nat hook postrouting priority 100 \\; }}; "
        f"nft add rule ip nat postrouting oifname \"{iface}\" masquerade; "
        f"nft add table ip filter; "
        f"nft add chain ip filter forward {{ type filter hook forward priority 0 \\; }}; "
        f"nft add rule ip filter forward iifname \"wg0\" accept; "
        f"nft add rule ip filter forward oifname \"wg0\" accept"
    ), content)
    content = re.sub(r"PostDown = .*", (
        "PostDown = nft flush table ip nat; nft delete table ip nat; "
        "nft flush chain ip filter forward"
    ), content)

    with open(WG_CONF, "w") as f:
        f.write(content)
    os.chmod(WG_CONF, 0o600)

    # Also install nftables if missing
    try:
        apt_install("nftables")
        run(["systemctl", "enable", "nftables"], check=False)
        run(["systemctl", "start", "nftables"], check=False)
    except Exception:
        pass


def _get_public_ip():
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
    if command_exists("qrencode"):
        try:
            subprocess.run(["qrencode", "-t", "ansiutf8"], input=text.encode(), check=True)
            return
        except Exception:
            pass
    try:
        apt_install("qrencode")
        subprocess.run(["qrencode", "-t", "ansiutf8"], input=text.encode(), check=True)
    except Exception:
        print_warning("Could not generate QR code. Falling back to file output.")
        _save_client_config(text)
