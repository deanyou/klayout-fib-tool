"""
KLayout FIB Tool

A simple, practical tool for marking FIB operations on IC layouts.
No over-engineering, no fancy abstractions - just what works.

Version: 1.0.0
Author: Dean
License: MIT

Features:
- CUT, CONNECT, PROBE markers with multi-point support
- Automatic layer creation (317, 318, 319)
- PDF export with 3-level screenshots
- Coordinate jump and display
- Right-click menu operations

Installation:
1. Via SALT Package Manager (recommended):
   - Tools → Salt Package Manager → Install from URL
   - Enter GitHub release URL

2. Via manual copy:
   - Copy fib_tool/ to ~/.klayout/salt/
   - Restart KLayout

3. Via exec() for development:
   import sys; sys.path.insert(0, '/path/to/fib_tool')
   exec(open('/path/to/fib_tool/fib_plugin.py', encoding='utf-8').read())

Usage:
- Use toolbar buttons: FIB Cut, FIB Connect, FIB Probe
- Or open FIB Panel for full features
- Right-click on markers for operations (delete, add notes, etc.)
"""

__version__ = "1.0.0"
__author__ = "Dean"
__license__ = "MIT"

# Package metadata
__all__ = [
    'markers',
    'multipoint_markers',
    'config',
    'layer_manager',
    'layer_tap',
    'fib_panel',
    'fib_plugin',
]
