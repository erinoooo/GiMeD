#!/usr/bin/env bash
# build.sh — builds the GiMeD binary using PyInstaller
set -e

DIST_DIR="./dist"
BINARY="$DIST_DIR/gimed"

echo "==> Installing build deps..."
pip install pyinstaller --quiet

echo "==> Building binary..."
pyinstaller gimed.spec --distpath "$DIST_DIR" --workpath ./build --clean -y

echo ""
echo "✓ Binary ready: $BINARY"
echo "  Size: $(du -sh $BINARY | cut -f1)"
echo ""
echo "To test locally:"
echo "  sudo $BINARY"
