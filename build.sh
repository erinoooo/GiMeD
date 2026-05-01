#!/usr/bin/env bash
# build.sh — builds the GiMeD binary using PyInstaller
# Output binary is named: gimed-linux-<arch>  (e.g. gimed-linux-x86_64)
set -e

DIST_DIR="./dist"
OS="linux"
ARCH="$(uname -m)"          # x86_64 | aarch64 | armv7l
BINARY_NAME="gimed-${OS}-${ARCH}"
BINARY="$DIST_DIR/$BINARY_NAME"

echo "==> Installing build deps..."
pip install pyinstaller --quiet

echo "==> Building binary: $BINARY_NAME ..."
pyinstaller gimed.spec --distpath "$DIST_DIR" --workpath ./build --clean -y

# PyInstaller outputs the name from the spec ('gimed'); rename to arch-tagged name
mv "$DIST_DIR/gimed" "$BINARY"

echo ""
echo "✓ Binary ready: $BINARY"
echo "  Name: $BINARY_NAME"
echo "  Size: $(du -sh $BINARY | cut -f1)"
echo ""
echo "Upload this file as a GitHub Release asset with exactly this name:"
echo "  $BINARY_NAME"
echo ""
echo "Then the one-liner works:"
echo "  curl -fsSL https://raw.githubusercontent.com/erinoooo/gimed/main/install.sh | sudo bash"
echo ""
echo "To test locally:"
echo "  sudo $BINARY"