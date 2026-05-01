#!/usr/bin/env bash
# build.sh — builds the GiMeD binary using PyInstaller
set -e

DIST_DIR="./dist"
OS="linux"
ARCH="$(uname -m)"
BINARY_NAME="gimed-${OS}-${ARCH}"
BINARY="$DIST_DIR/$BINARY_NAME"

echo "==> Installing build deps..."
pip install pyinstaller simple-term-menu rich --quiet

echo "==> Building binary: $BINARY_NAME ..."
pyinstaller gimed.spec --distpath "$DIST_DIR" --workpath ./build --clean -y

mv "$DIST_DIR/gimed" "$BINARY"

echo ""
echo "✓ Binary ready: $BINARY"
echo "  Name: $BINARY_NAME"
echo "  Size: $(du -sh $BINARY | cut -f1)"
echo ""
echo "Run directly with: sudo $BINARY"
