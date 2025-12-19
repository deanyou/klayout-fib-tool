"""UI components for FIB Tool

This module provides UI components including the main panel,
dialog management, and UI factory functions.
"""

from .dialog_manager import FibDialogManager

# FIBPanel will be imported after refactoring
# from .fib_panel import FIBPanel

__all__ = [
    'FibDialogManager',
    # 'FIBPanel',  # Uncomment after refactoring
]
