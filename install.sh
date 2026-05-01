#!/usr/bin/env bash
# GiMeD installer
# Usage (single liner):
#   curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/gimed/main/install.sh | sudo bash
#   OR
#   wget -qO- https://raw.githubusercontent.com/YOUR_ORG/gimed/main/install.sh | sudo bash
#
# What this does:
#   1. Checks you're on a supported distro
#   2. Downloads the latest GiMeD binary from GitHub Releases
#   3. Installs it to /usr/local/bin/gimed
#   4. Runs it immediately

set -euo pipefail

#─────────────────────────────────────────────
# Config — update these when you publish releases
REPO="YOUR_ORG/gimed"
BINARY_URL="https://github.com/${REPO}/releases/latest/download/gimed-linux-x86_64"
INSTALL_PATH="/usr/local/bin/gimed"
#─────────────────────────────────────────────

RESET="\033[0m"
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
RED="\033[31m"
YELLOW="\033[33m"

info()    { echo -e "  ${CYAN}→${RESET} $*"; }
success() { echo -e "  ${GREEN}✓${RESET} $*"; }
error()   { echo -e "  ${RED}✗${RESET} $*" >&2; }
warn()    { echo -e "  ${YELLOW}⚠${RESET} $*"; }

banner() {
echo -e "${CYAN}"
cat << 'EOF'
  ██████╗ ██╗███╗   ███╗███████╗██████╗
 ██╔════╝ ██║████╗ ████║██╔════╝██╔══██╗
 ██║  ███╗██║██╔████╔██║█████╗  ██║  ██║
 ██║   ██║██║██║╚██╔╝██║██╔══╝  ██║  ██║
 ╚██████╔╝██║██║ ╚═╝ ██║███████╗██████╔╝
  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═════╝
EOF
echo -e "${RESET}"
echo -e "${BOLD}  Give Me a Desktop — Installer${RESET}"
echo -e "  https://github.com/${REPO}"
echo ""
}

check_root() {
    if [[ "$EUID" -ne 0 ]]; then
        error "This installer must be run as root."
        echo ""
        echo "  Run with sudo:"
        echo "    curl -fsSL https://raw.githubusercontent.com/${REPO}/main/install.sh | sudo bash"
        exit 1
    fi
}

check_distro() {
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot detect distro (/etc/os-release not found)."
        exit 1
    fi

    source /etc/os-release
    local id="${ID,,}"
    local id_like="${ID_LIKE:-}"

    if [[ "$id" != "ubuntu" && "$id" != "debian" && "$id_like" != *"ubuntu"* && "$id_like" != *"debian"* ]]; then
        error "Unsupported distro: $PRETTY_NAME"
        warn "GiMeD currently supports Ubuntu and Debian."
        exit 1
    fi

    success "Detected: $PRETTY_NAME"
}

check_deps() {
    local missing=()
    for cmd in curl wget; do
        command -v "$cmd" &>/dev/null && return 0
    done
    # Neither curl nor wget — try to install curl
    warn "curl/wget not found, installing curl..."
    apt-get install -y curl -qq
}

download_binary() {
    info "Downloading GiMeD binary..."

    local tmp
    tmp="$(mktemp)"

    if command -v curl &>/dev/null; then
        curl -fsSL --progress-bar "$BINARY_URL" -o "$tmp"
    elif command -v wget &>/dev/null; then
        wget -q --show-progress "$BINARY_URL" -O "$tmp"
    else
        error "Neither curl nor wget available."
        exit 1
    fi

    chmod +x "$tmp"
    mv "$tmp" "$INSTALL_PATH"
    success "Installed to $INSTALL_PATH"
}

main() {
    banner
    check_root
    check_distro
    check_deps
    download_binary

    echo ""
    echo -e "  ${GREEN}${BOLD}GiMeD installed! Starting setup...${RESET}"
    echo ""
    sleep 1

    exec "$INSTALL_PATH"
}

main "$@"
