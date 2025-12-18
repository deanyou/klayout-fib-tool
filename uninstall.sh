#!/bin/bash

# FIB Tool - Uninstallation Script
# Removes FIB Tool from KLayout SALT directory

echo "=========================================="
echo "FIB Tool - Uninstaller"
echo "=========================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

# Set KLayout SALT directory
if [ "$MACHINE" = "Mac" ]; then
    KLAYOUT_SALT_DIR="$HOME/.klayout/salt"
elif [ "$MACHINE" = "Linux" ]; then
    KLAYOUT_SALT_DIR="$HOME/.klayout/salt"
else
    echo "Error: Unsupported OS"
    exit 1
fi

TARGET_DIR="$KLAYOUT_SALT_DIR/fib-tool"

echo "Target: $TARGET_DIR"
echo ""

# Check if installed
if [ ! -e "$TARGET_DIR" ]; then
    echo "FIB Tool is not installed."
    echo "Nothing to uninstall."
    exit 0
fi

# Show what will be removed
if [ -L "$TARGET_DIR" ]; then
    LINK_TARGET=$(readlink "$TARGET_DIR")
    echo "Found: Symbolic link to $LINK_TARGET"
else
    echo "Found: Installed files"
fi

echo ""
read -p "Remove FIB Tool from KLayout? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Removing FIB Tool..."

rm -rf "$TARGET_DIR"

if [ $? -eq 0 ]; then
    echo "✓ FIB Tool removed successfully"
    echo ""
    echo "To reinstall, run: ./install.sh"
else
    echo "✗ Error removing FIB Tool"
    exit 1
fi
