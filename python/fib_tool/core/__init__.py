"""Core utilities for FIB Tool

This module provides core utility functions and classes for geometry calculations,
validation, and state management.
"""

from .geometry_utils import (
    calculate_distance,
    calculate_direction,
    get_bounding_box,
    get_marker_center
)
from .validation_utils import (
    validate_marker_id,
    validate_coordinates,
    validate_file_path,
    validate_conversion
)
from .global_state import FibGlobalState

__all__ = [
    'calculate_distance',
    'calculate_direction',
    'get_bounding_box',
    'get_marker_center',
    'validate_marker_id',
    'validate_coordinates',
    'validate_file_path',
    'validate_conversion',
    'FibGlobalState',
]
