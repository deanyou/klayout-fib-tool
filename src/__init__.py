"""
KLayout FIB Tool

A simple, practical tool for marking FIB operations on IC layouts.
No over-engineering, no fancy abstractions - just what works.
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import pya
from plugin import FIBPlugin


class FIBToolMenu(pya.Action):
    """Menu action to launch FIB tool"""
    
    def __init__(self):
        super().__init__()
        self.set_text("FIB Tool")
        self.set_shortcut("Ctrl+Shift+F")
        self.triggered(self.on_triggered)
        self.plugin = None
    
    def on_triggered(self):
        """Launch FIB tool dialog"""
        view = pya.Application.instance().main_window().current_view()
        
        if view is None:
            pya.MessageBox.warning("No Layout", "Please open a layout first.", pya.MessageBox.Ok)
            return
        
        # Create plugin instance if needed
        if self.plugin is None:
            self.plugin = FIBPlugin(view)
        
        # Show dialog
        self.plugin.show_dialog()


# Register the menu action in the Tools menu
menu = FIBToolMenu()
main_menu = pya.Application.instance().main_window().menu()

# First try to insert into Tools menu
result = main_menu.insert_item("@tools.end", "fib_tool", menu)
if not result:
    # Fallback to main menu if Tools menu not found
    result = main_menu.insert_item("@main/end", "fib_tool", menu)

# Also add to toolbar
main_menu.insert_item("@toolbar.end", "fib_tool", menu)

print(f"FIB Tool loaded. Access via {result and 'Tools menu' or 'Main menu'} or Ctrl+Shift+F")
