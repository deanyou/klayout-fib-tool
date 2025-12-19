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

# Import new modular components (version 4.0+)
from .core.global_state import FibGlobalState
from .core.geometry_utils import (
    calculate_distance,
    calculate_direction,
    get_bounding_box,
    get_marker_center
)
from .core.validation_utils import (
    validate_marker_id,
    validate_coordinates,
    validate_file_path,
    validate_conversion
)
from .ui.dialog_manager import FibDialogManager
from .business.marker_transformer import FibMarkerTransformer
from .business.file_manager import FibFileManager
from .business.export_manager import FibExportManager

# Backward compatibility: FIBPanel will be imported from ui/ after refactoring
# For now, it's still in the old location
# from .ui.fib_panel import FIBPanel

# Package metadata
__all__ = [
    # Legacy module names (for backward compatibility)
    'markers',
    'multipoint_markers',
    'config',
    'layer_manager',
    'layer_tap',
    'fib_panel',
    'fib_plugin',
    # New modular components (version 4.0+)
    'FibGlobalState',
    'calculate_distance',
    'calculate_direction',
    'get_bounding_box',
    'get_marker_center',
    'validate_marker_id',
    'validate_coordinates',
    'validate_file_path',
    'validate_conversion',
    'FibDialogManager',
    'FibMarkerTransformer',
    'FibFileManager',
    'FibExportManager',
    # 'FIBPanel',  # Uncomment after refactoring fib_panel.py
]
