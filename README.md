# GiMeD — Give Me a Desktop

> Headless Linux → full remote desktop in minutes.

GiMeD automatically installs and configures a desktop environment, XRDP, and WireGuard VPN on any headless Ubuntu or Debian system. You answer a few questions; GiMeD does the rest.

---

## Single-liner install

```bash
curl -fsSL https://raw.githubusercontent.com/erinoooo/gimed/main/install.sh | sudo bash
```

or with `wget`:

```bash
wget -qO- https://raw.githubusercontent.com/erinoooo/gimed/main/install.sh | sudo bash
```

That's it. The script will:
1. Check you're on a supported distro
2. Download the latest `gimed` binary to `/usr/local/bin/gimed`
3. Launch GiMeD immediately

---

## What GiMeD sets up

```
Your device
    │
    │  WireGuard VPN (UDP 51820)
    ▼
Headless server
    │
    │  RDP to 10.x.x.1:3389  (never exposed to internet)
    ▼
Desktop session (XFCE / MATE / LXDE / LXQt)
```

- **Desktop environment** — your choice of XFCE, MATE, LXDE, or LXQt
- **XRDP** — RDP server on port 3389, Xorg-based (no Wayland headaches)
- **Self-signed SSL cert** — optional, for encrypted RDP
- **WireGuard VPN** — only port 51820/UDP is exposed; 3389 stays firewalled
- **Client config** — delivered as terminal output, saved file, and/or QR code

---

## Supported systems

| Distro  | Versions          |
|---------|-------------------|
| Ubuntu  | 20.04, 22.04, 24.04 |
| Debian  | 10, 11, 12        |

Ubuntu-based distros (Mint, Pop!_OS, etc.) should work too.

---

## Desktop environment compatibility

| DE    | xrdp | Weight   | Notes                        |
|-------|------|----------|------------------------------|
| XFCE  | ✅    | Light    | Recommended — most stable    |
| MATE  | ✅    | Medium   | Windows-like feel            |
| LXDE  | ✅    | Very light | Best for low-RAM servers   |
| LXQt  | ✅    | Light    | Modern LXDE successor        |

> GNOME and KDE are excluded due to Wayland/xrdp compatibility issues.

---

## After setup

1. Import `gimed-client.conf` (or scan the QR code) into the WireGuard app on your device
2. Connect to the VPN
3. Open your RDP client and connect to `10.99.0.1:3389` (or whatever VPN IP you chose)
4. Log in with your Linux credentials

---

## Building from source

```bash
git clone https://github.com/erinoooo/gimed
cd gimed
pip install pyinstaller
bash build.sh
# binary → dist/gimed
```

---

## Project layout

```
gimed/
├── install.sh          # single-liner bootstrap
├── build.sh            # PyInstaller build script
├── gimed.spec          # PyInstaller spec
├── setup.py
└── gimed/
    ├── __main__.py     # entry point
    ├── cli.py          # interactive setup flow
    ├── ui.py           # TUI helpers
    ├── system.py       # OS detection, shell utils
    ├── desktop.py      # DE installer
    ├── xrdp.py         # xrdp installer + configurator
    └── wireguard.py    # WireGuard installer + configurator
```

---

## Security notes

- Port 3389 is **never opened** to the internet — RDP is only reachable over WireGuard
- WireGuard keys are generated fresh on every run
- The SSL cert is self-signed; you'll see a warning on first RDP connect (click through once)
- WireGuard config is saved to `/root/gimed-client.conf` with `600` permissions

---

## License

MIT
