#!/usr/bin/env python3
"""
KLayout Package Entry Point for FIB Tool

This file is automatically loaded by KLayout when the package is installed via SALT.
It initializes the FIB Tool plugin system.
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Global flag to prevent double initialization
_FIB_TOOL_INITIALIZED = False

def init_fib_tool():
    """
    Initialize FIB Tool plugin system.
    
    This function:
    1. Checks and creates required layers (317, 318, 319)
    2. Registers plugin factories for toolbar buttons
    3. Creates and docks the FIB Panel
    
    Can be called multiple times safely (will only initialize once).
    """
    global _FIB_TOOL_INITIALIZED
    
    if _FIB_TOOL_INITIALIZED:
        print("[FIB Tool] Already initialized, skipping...")
        return
    
    try:
        print("\n" + "=" * 60)
        print("FIB TOOL - SALT Package Initialization")
        print("=" * 60)
        
        # Import and execute the main plugin
        # This will register plugin factories and create the panel
        from . import fib_plugin
        
        # Mark as initialized
        _FIB_TOOL_INITIALIZED = True
        
        print("=" * 60)
        print("✓ FIB Tool initialized successfully")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"✗ Error initializing FIB Tool: {e}")
        import traceback
        traceback.print_exc()

# Auto-initialize when loaded by KLayout
if __name__ != "__main__":
    # We're being imported by KLayout's SALT system
    init_fib_tool()
