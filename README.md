# GiMeD — Give Me a Desktop

> Headless Linux → full remote desktop in minutes.

GiMeD automatically installs and configures a desktop environment, XRDP, and WireGuard VPN on any headless Ubuntu or Debian system. Answer a few questions and GiMeD does the rest.

---

## How to install

**1. Download the installer**

```bash
curl -fsSL https://raw.githubusercontent.com/erinoooo/gimed/main/install.sh -o install.sh
```

**2. Run it**

```bash
sudo bash install.sh
```

**3. Launch GiMeD**

```bash
sudo gimed
```

That's it. GiMeD will walk you through the rest interactively.

---

## What GiMeD sets up

```
Your device
    │
    │  WireGuard VPN (UDP 51820)
    ▼
Headless server
    │
    │  RDP to 10.x.x.1:3389  (never exposed to the internet)
    ▼
Desktop session (XFCE / MATE / LXDE / LXQt)
```

- **Desktop environment** — your choice of XFCE, MATE, LXDE, or LXQt
- **XRDP** — RDP server on port 3389, Xorg-based
- **Self-signed SSL cert** — optional, for encrypted RDP
- **WireGuard VPN** — only UDP 51820 is exposed; port 3389 stays firewalled
- **Client config** — delivered as terminal output, saved file, and/or QR code

---

## Supported systems

| Distro  | Versions              |
|---------|-----------------------|
| Ubuntu  | 20.04, 22.04, 24.04   |
| Debian  | 10, 11, 12            |

Ubuntu-based distros (Mint, Pop!_OS, etc.) should work too.

---

## Desktop environment compatibility

| DE    | xrdp | Weight      | Notes                      |
|-------|------|-------------|----------------------------|
| XFCE  | ✅   | Light       | Recommended — most stable  |
| MATE  | ✅   | Medium      | Windows-like feel          |
| LXDE  | ✅   | Very light  | Best for low-RAM servers   |
| LXQt  | ✅   | Light       | Modern LXDE successor      |

> GNOME and KDE are excluded due to Wayland/xrdp compatibility issues.

---

## After setup

1. Import the WireGuard client config (or scan the QR code) into the WireGuard app on your device
2. Connect to the VPN
3. Open your RDP client and connect to `10.99.0.1:3389` (or whatever VPN IP you chose)
4. Log in with your Linux credentials

**Recommended RDP clients:**
- Windows — built-in Remote Desktop Connection
- macOS — Microsoft Remote Desktop (App Store)
- Linux — Remmina

---

## Security notes

- Port 3389 is **never opened** to the internet — RDP is only reachable over WireGuard
- WireGuard keys are generated fresh on every run
- WireGuard config is saved to `/root/gimed-client.conf` with `600` permissions
- The SSL cert is self-signed; you'll see a warning on first RDP connect — click through once

---

## Building from source

```bash
git clone https://github.com/erinoooo/gimed
cd gimed
bash build.sh
# binary → dist/gimed-linux-x86_64
```

Upload `dist/gimed-linux-<arch>` as a GitHub Release asset with that exact filename.

---

## Project layout

```
gimed/
├── install.sh          ← downloads and installs the binary
├── build.sh            ← PyInstaller build script
├── gimed.spec          ← PyInstaller spec
├── setup.py
├── README.md
└── gimed/
    ├── __main__.py     ← entry point
    ├── cli.py          ← interactive setup flow
    ├── ui.py           ← TUI (simple-term-menu + rich)
    ├── system.py       ← OS detection, shell utils
    ├── desktop.py      ← DE installer
    ├── xrdp.py         ← xrdp installer + configurator
    └── wireguard.py    ← WireGuard installer + configurator
```

---

## License

MIT
