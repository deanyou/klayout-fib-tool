#!/bin/bash

# FIB Tool - Installation Script for macOS/Linux
# Installs FIB Tool as a KLayout SALT package

set -e  # Exit on error

echo "=========================================="
echo "FIB Tool - SALT Package Installer"
echo "=========================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: $MACHINE"
echo ""

# Set KLayout SALT directory based on OS
if [ "$MACHINE" = "Mac" ]; then
    KLAYOUT_SALT_DIR="$HOME/.klayout/salt"
elif [ "$MACHINE" = "Linux" ]; then
    KLAYOUT_SALT_DIR="$HOME/.klayout/salt"
else
    echo "Error: Unsupported operating system: $MACHINE"
    exit 1
fi

echo "KLayout SALT directory: $KLAYOUT_SALT_DIR"
echo ""

# Check if source directories exist
if [ ! -d "python/fib_tool" ]; then
    echo "Error: python/fib_tool/ directory not found"
    echo ""
    echo "It looks like the project hasn't been migrated to SALT structure yet."
    echo "Please run: ./refactor.sh first"
    exit 1
fi

if [ ! -d "pymacros" ]; then
    echo "Error: pymacros/ directory not found"
    echo ""
    echo "It looks like the project hasn't been migrated to SALT structure yet."
    echo "Please run: ./refactor.sh first"
    exit 1
fi

# Create SALT directory if it doesn't exist
mkdir -p "$KLAYOUT_SALT_DIR"

# Target directory
TARGET_DIR="$KLAYOUT_SALT_DIR/fib-tool"

echo "Installation options:"
echo "1) Symbolic link (recommended for development)"
echo "   - Changes to source code immediately reflected"
echo "   - Easy to update"
echo ""
echo "2) Copy files (recommended for production)"
echo "   - Stable installation"
echo "   - Won't change if source is modified"
echo ""
read -p "Choose installation method (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Installing via symbolic link..."
        
        # Remove existing installation
        if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
            echo "Removing existing installation..."
            rm -rf "$TARGET_DIR"
        fi
        
        # Create symbolic link
        SOURCE_DIR="$(pwd)"
        ln -s "$SOURCE_DIR" "$TARGET_DIR"
        
        echo "✓ Symbolic link created: $TARGET_DIR -> $SOURCE_DIR"
        ;;
        
    2)
        echo ""
        echo "Installing via copy..."
        
        # Remove existing installation
        if [ -d "$TARGET_DIR" ]; then
            echo "Removing existing installation..."
            rm -rf "$TARGET_DIR"
        fi
        
        # Create target directory
        mkdir -p "$TARGET_DIR"
        
        # Copy files
        echo "Copying files..."
        cp -r python "$TARGET_DIR/"
        cp -r pymacros "$TARGET_DIR/"
        cp grain.xml "$TARGET_DIR/"
        cp README.md "$TARGET_DIR/" 2>/dev/null || true
        cp LICENSE "$TARGET_DIR/" 2>/dev/null || true
        
        echo "✓ Files copied to: $TARGET_DIR"
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="

# Verify structure
if [ -f "$TARGET_DIR/grain.xml" ]; then
    echo "✓ grain.xml found"
else
    echo "✗ grain.xml not found"
fi

if [ -d "$TARGET_DIR/python/fib_tool" ]; then
    PY_COUNT=$(ls -1 "$TARGET_DIR/python/fib_tool"/*.py 2>/dev/null | wc -l)
    echo "✓ python/fib_tool/ found ($PY_COUNT Python files)"
else
    echo "✗ python/fib_tool/ not found"
fi

if [ -d "$TARGET_DIR/pymacros" ]; then
    LYM_COUNT=$(ls -1 "$TARGET_DIR/pymacros"/*.lym 2>/dev/null | wc -l)
    echo "✓ pymacros/ found ($LYM_COUNT macro files)"
else
    echo "✗ pymacros/ not found"
fi

# Verify templates directory (critical for HTML export with screenshots)
if [ -d "$TARGET_DIR/python/fib_tool/templates" ]; then
    TMPL_COUNT=$(ls -1 "$TARGET_DIR/python/fib_tool/templates"/*.{html,js} 2>/dev/null | wc -l)
    if [ "$TMPL_COUNT" -ge 2 ]; then
        echo "✓ templates/ found ($TMPL_COUNT files)"
    else
        echo "⚠  WARNING: templates/ found but incomplete ($TMPL_COUNT files, expected 2)"
        echo "   HTML export will use fallback mode (limited features)"
    fi
else
    echo "⚠  WARNING: templates/ directory not found"
    echo "   HTML export will use fallback mode (limited features)"
    echo "   For full features, ensure python/fib_tool/templates/ contains:"
    echo "   - report_template.html"
    echo "   - report_script.js"
fi

echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "Installation location: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "1. Close KLayout completely (not just the window)"
echo "2. Reopen KLayout"
echo "3. Open a GDS file"
echo "4. Press Ctrl+Shift+F to open FIB Tool Panel"
echo "   Or use menu: Tools → Toggle FIB Tool Panel"
echo ""
echo "Troubleshooting:"
echo "- If panel doesn't appear, press F5 to check console for errors"
echo "- Make sure you completely closed and reopened KLayout"
echo "- Check that layers 337, 338, 339 are visible"
echo ""
echo "For development/testing:"
echo "- Use load_fib_tool.py in Macro Development (F5)"
echo "- Run: exec(open('$SOURCE_DIR/load_fib_tool.py').read())"
echo ""
