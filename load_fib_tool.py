#!/usr/bin/env python3
"""
Load FIB Tool in KLayout Macro Development (F5)

Usage in KLayout Macro Development:
    
    # Method 1: Set path before exec (RECOMMENDED)
    FIB_TOOL_PATH = '/Users/dean/Documents/git/klayout-fib-tool'
    exec(open(FIB_TOOL_PATH + '/load_fib_tool.py', encoding='utf-8').read())
    
    # Method 2: Use full path in exec (also works)
    exec(open('/Users/dean/Documents/git/klayout-fib-tool/load_fib_tool.py', encoding='utf-8').read())
    # Then when prompted, enter: /Users/dean/Documents/git/klayout-fib-tool

The script will:
1. Check if FIB_TOOL_PATH is already set in the environment
2. If not, try to extract it from the exec() command
3. If that fails, prompt you to enter it

This avoids hardcoding while still being reliable.
"""

import sys
import os
import pya

# ============================================================================
# GET FIB_TOOL_PATH
# ============================================================================
FIB_TOOL_PATH = None

# Method 1: Check if user set it before exec()
if 'FIB_TOOL_PATH' in globals():
    FIB_TOOL_PATH = globals()['FIB_TOOL_PATH']
    print(f"[OK] Using FIB_TOOL_PATH from environment: {FIB_TOOL_PATH}")

# Method 2: Check if it's in __main__ namespace
elif 'FIB_TOOL_PATH' in sys.modules['__main__'].__dict__:
    FIB_TOOL_PATH = sys.modules['__main__'].__dict__['FIB_TOOL_PATH']
    print(f"[OK] Using FIB_TOOL_PATH from __main__: {FIB_TOOL_PATH}")

# Method 3: Try to extract from exec command history (if available)
# This won't work reliably, so we'll ask the user

if FIB_TOOL_PATH is None:
    # Ask user for path
    print("")
    print("=" * 70)
    print("FIB_TOOL_PATH not set!")
    print("=" * 70)
    print("")
    print("Please set FIB_TOOL_PATH before running this script:")
    print("")
    print("Example:")
    print("  FIB_TOOL_PATH = '/Users/dean/Documents/git/klayout-fib-tool'")
    print("  exec(open(FIB_TOOL_PATH + '/load_fib_tool.py', encoding='utf-8').read())")
    print("")
    
    # Try to get it via dialog
    result = pya.InputDialog.ask_string(
        "FIB Tool Path",
        "Enter the full path to klayout-fib-tool directory:",
        "/Users/dean/Documents/git/klayout-fib-tool"
    )
    
    if result:
        FIB_TOOL_PATH = result
        print(f"[OK] Using path from dialog: {FIB_TOOL_PATH}")
    else:
        print("[X] No path provided. Exiting.")
        sys.exit(1)

# Validate path
if not FIB_TOOL_PATH or not os.path.exists(FIB_TOOL_PATH):
    pya.MessageBox.warning(
        "FIB Tool Loader",
        f"Invalid path: {FIB_TOOL_PATH}\n\n"
        f"Please check the path and try again.",
        pya.MessageBox.Ok
    )
    sys.exit(1)

# Store in __main__ for future use
sys.modules['__main__'].FIB_TOOL_PATH = FIB_TOOL_PATH
# ============================================================================

print("=" * 70)
print("FIB Tool - Development Loader")
print("=" * 70)
print("")

script_dir = FIB_TOOL_PATH
python_dir = os.path.join(script_dir, 'python')

print(f"FIB Tool directory: {script_dir}")
print(f"Python directory: {python_dir}")
print("")

# Check if python directory exists
if not os.path.exists(python_dir):
    print(f"[X] Error: {python_dir} not found")
    print("")
    print("Please check:")
    print(f"1. Is the detected path correct? Currently: {FIB_TOOL_PATH}")
    print("2. Has the project been refactored? Run: ./refactor.sh")
    print("3. Does python/fib_tool/ directory exist?")
    print("")
    
    pya.MessageBox.warning(
        "FIB Tool Loader",
        f"Python directory not found:\n{python_dir}\n\n"
        f"Detected path: {FIB_TOOL_PATH}\n\n"
        f"Please check the installation or use load_fib_tool_configured.py",
        pya.MessageBox.Ok
    )
    sys.exit(1)

# Add to sys.path if not already there
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)
    print(f"[OK] Added to sys.path: {python_dir}")
else:
    print(f"[OK] Already in sys.path: {python_dir}")

print("")

# Check if we can import fib_tool
print("Checking fib_tool package...")
try:
    import fib_tool
    print(f"[OK] fib_tool module found")
    print(f"  Location: {fib_tool.__file__}")
except ImportError as e:
    print(f"[X] Cannot import fib_tool: {e}")
    print("")
    print("Troubleshooting:")
    print("1. Check if python/fib_tool/ directory exists")
    print("2. Check if python/fib_tool/__init__.py exists")
    print("3. Run: python3 test_imports.py")
    print("")
    
    pya.MessageBox.warning(
        "FIB Tool Loader",
        f"Cannot import fib_tool module.\n\n"
        f"Error: {e}\n\n"
        f"Please check the installation.",
        pya.MessageBox.Ok
    )
    sys.exit(1)

print("")

# Check if already initialized
if hasattr(sys.modules['__main__'], '_FIB_TOOL_LOADED'):
    print("[!] FIB Tool already loaded in this session")
    print("")
    
    # Try to show existing panel
    try:
        from fib_tool.fib_panel import get_fib_panel
        panel = get_fib_panel()
        if panel:
            panel.show()
            print("[OK] Showed existing FIB Panel")
        else:
            print("[!] No existing panel found, creating new one...")
            from fib_tool.fib_panel import create_fib_panel
            panel = create_fib_panel()
            print("[OK] New panel created")
    except Exception as e:
        print(f"[X] Error showing panel: {e}")
        import traceback
        traceback.print_exc()
    
    print("")
    print("=" * 70)
    sys.exit(0)

# Check if GDS file is open
print("Checking for active layout...")
main_window = pya.Application.instance().main_window()
current_view = main_window.current_view()

if not current_view or not current_view.active_cellview().is_valid():
    print("[!] No GDS file is currently open")
    print("")
    
    response = pya.MessageBox.warning(
        "FIB Tool Loader",
        "No GDS file is currently open.\n\n"
        "FIB Tool requires an active layout to create markers and layers.\n\n"
        "Do you want to continue loading anyway?",
        pya.MessageBox.Yes | pya.MessageBox.No
    )
    
    if response == pya.MessageBox.No:
        print("Loading cancelled by user.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("Continuing without active layout...")
        print("")
else:
    cellview = current_view.active_cellview()
    cell_name = cellview.cell.name if cellview.cell else "Unknown"
    print(f"[OK] Active layout found: {cell_name}")
    print("")

# Initialize FIB Tool
print("Initializing FIB Tool...")
print("-" * 70)

try:
    from fib_tool import klayout_package
    
    # Check if already initialized by __init__.py
    if hasattr(klayout_package, '_FIB_TOOL_INITIALIZED') and klayout_package._FIB_TOOL_INITIALIZED:
        print("[OK] FIB Tool already initialized by package import")
    else:
        # Call the correct function name
        klayout_package.init_fib_tool()
    
    # Mark as loaded
    sys.modules['__main__']._FIB_TOOL_LOADED = True
    
    print("-" * 70)
    print("[OK] FIB Tool initialized successfully")
    print("")
    
except Exception as e:
    print("-" * 70)
    print(f"[X] Error initializing FIB Tool: {e}")
    print("")
    import traceback
    traceback.print_exc()
    print("")
    print("=" * 70)
    sys.exit(1)

# Ensure FIB layers exist (if layout is open)
if current_view and current_view.active_cellview().is_valid():
    print("Ensuring FIB layers exist...")
    try:
        from fib_tool.layer_manager import ensure_fib_layers
        layer_success = ensure_fib_layers()
        
        if layer_success:
            print("[OK] FIB layers verified/created (337, 338, 339)")
        else:
            print("[!] Some layers may not have been created properly")
        print("")
    except Exception as e:
        print(f"[!] Error ensuring layers: {e}")
        print("")

# Show the panel
print("Creating FIB Panel...")
try:
    from fib_tool.fib_panel import create_fib_panel, get_fib_panel
    
    panel = get_fib_panel()
    if panel is None:
        panel = create_fib_panel()
    else:
        panel.show()
    
    print("[OK] FIB Panel is now visible")
    print("")
    
except Exception as e:
    print(f"[X] Error showing panel: {e}")
    print("")
    import traceback
    traceback.print_exc()
    print("")
    print("=" * 70)
    sys.exit(1)

# Success!
print("=" * 70)
print("[OK] FIB Tool Loaded Successfully!")
print("=" * 70)
print("")
print("Panel should be visible on the right side of KLayout")
print("")
print("To reload after code changes:")
print("1. Close KLayout completely")
print("2. Reopen KLayout")
print("3. Run this script again")
print("")
print("=" * 70)
