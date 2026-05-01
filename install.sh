#!/usr/bin/env bash
# GiMeD installer
# Usage:
#   sudo bash install.sh
#
# What this does:
#   1. Checks you're on a supported distro
#   2. Downloads the latest GiMeD binary from GitHub Releases
#   3. Installs it to /usr/local/bin/gimed
#   4. Runs it

set -euo pipefail

REPO="erinoooo/gimed"
INSTALL_PATH="/usr/local/bin/gimed"

ARCH="$(uname -m)"
case "$ARCH" in
    x86_64)  ARCH_TAG="x86_64" ;;
    aarch64) ARCH_TAG="aarch64" ;;
    armv7l)  ARCH_TAG="armv7l" ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
    ;;
esac

BINARY_NAME="gimed-linux-${ARCH_TAG}"
BINARY_URL="https://github.com/${REPO}/releases/latest/download/${BINARY_NAME}"

RESET="\033[0m"; BOLD="\033[1m"; GREEN="\033[32m"; CYAN="\033[36m"; RED="\033[31m"; YELLOW="\033[33m"

info()    { echo -e "  ${CYAN}→${RESET} $*"; }
success() { echo -e "  ${GREEN}✓${RESET} $*"; }
error()   { echo -e "  ${RED}✗${RESET} $*" >&2; }
warn()    { echo -e "  ${YELLOW}⚠${RESET} $*"; }

echo -e "${CYAN}"
cat << 'BANNER'
  ██████╗ ██╗███╗   ███╗███████╗██████╗
 ██╔════╝ ██║████╗ ████║██╔════╝██╔══██╗
 ██║  ███╗██║██╔████╔██║█████╗  ██║  ██║
 ██║   ██║██║██║╚██╔╝██║██╔══╝  ██║  ██║
 ╚██████╔╝██║██║ ╚═╝ ██║███████╗██████╔╝
  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝
BANNER
echo -e "${RESET}"
echo -e "${BOLD}  Give Me a Desktop — Installer${RESET}"
echo -e "  https://github.com/${REPO}"
echo ""

if [[ "$EUID" -ne 0 ]]; then
    error "Must be run as root: sudo bash install.sh"
    exit 1
fi

if [[ ! -f /etc/os-release ]]; then
    error "Cannot detect distro."
    exit 1
fi

source /etc/os-release
id_lower="${ID,,}"
id_like_lower="${ID_LIKE:-}"
if [[ "$id_lower" != "ubuntu" && "$id_lower" != "debian" && \
      "$id_like_lower" != *"ubuntu"* && "$id_like_lower" != *"debian"* ]]; then
    error "Unsupported distro: $PRETTY_NAME"
    warn "GiMeD supports Ubuntu and Debian."
    exit 1
fi
success "Detected: $PRETTY_NAME"

command -v curl &>/dev/null || apt-get install -y curl -qq

info "Downloading GiMeD binary ($BINARY_NAME)..."
tmp="$(mktemp)"
curl -fsSL --progress-bar "$BINARY_URL" -o "$tmp"
chmod +x "$tmp"
mv "$tmp" "$INSTALL_PATH"
success "Installed to $INSTALL_PATH"

echo ""
echo -e "  ${GREEN}${BOLD}GiMeD installed!${RESET}"
echo ""
echo -e "  Run it with: ${BOLD}sudo gimed${RESET}"
echo ""
