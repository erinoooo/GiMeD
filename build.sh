#!/usr/bin/env bash
# build.sh — builds the GiMeD binary using PyInstaller
set -e

DIST_DIR="./dist"
OS="linux"
ARCH="$(uname -m)"
BINARY_NAME="gimed-${OS}-${ARCH}"
BINARY="$DIST_DIR/$BINARY_NAME"

echo "==> Installing build deps..."
pip install pyinstaller InquirerPy rich --quiet

echo "==> Building binary: $BINARY_NAME ..."
pyinstaller gimed.spec --distpath "$DIST_DIR" --workpath ./build --clean -y

# PyInstaller names it 'gimed' from the spec; rename to arch-tagged name
mv "$DIST_DIR/gimed" "$BINARY"

echo ""
echo "✓ Binary ready: $BINARY"
echo "  Name: $BINARY_NAME"
echo "  Size: $(du -sh $BINARY | cut -f1)"
echo ""
echo "Upload as a GitHub Release asset named exactly: $BINARY_NAME"
echo ""
echo "One-liner will then work:"
echo "  curl -fsSL https://raw.githubusercontent.com/erinoooo/gimed/main/install.sh | sudo bash"
echo ""
echo "To test locally: sudo $BINARY"
