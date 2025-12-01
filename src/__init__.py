"""
KLayout FIB Tool

A simple, practical tool for marking FIB operations on IC layouts.
No over-engineering, no fancy abstractions - just what works.
"""

import pya
from plugin import FIBPlugin


class FIBToolMenu(pya.Action):
    """Menu action to launch FIB tool"""
    
    def __init__(self):
        super().__init__()
        self.setText("FIB Tool")
        self.setShortcut("Ctrl+Shift+F")
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


# Register the menu action
menu = FIBToolMenu()
pya.Application.instance().main_window().menu().insert_item("@toolbar.end", "fib_tool", menu)

print("FIB Tool loaded. Access via Tools menu or Ctrl+Shift+F")
