"""Validation utility functions for FIB Tool

This module provides validation functions for marker IDs, coordinates,
file paths, and marker conversions.
"""

import os
import re


def validate_marker_id(marker_id, existing_ids=None):
    """Validate marker ID format and uniqueness

    Args:
        marker_id (str): Marker ID to validate (e.g., "CUT_0", "PROBE_5")
        existing_ids (set, optional): Set of existing marker IDs to check uniqueness

    Returns:
        tuple: (is_valid, error_message)
               is_valid is True if valid, False otherwise
               error_message is None if valid, error string otherwise

    Example:
        >>> validate_marker_id("CUT_0")
        (True, None)
        >>> validate_marker_id("INVALID")
        (False, 'Invalid marker ID format')
        >>> validate_marker_id("CUT_0", {"CUT_0"})
        (False, 'Marker ID already exists')
    """
    if not marker_id:
        return (False, "Marker ID cannot be empty")

    # Check format: TYPE_NUMBER
    pattern = r'^(CUT|CONNECT|PROBE|MULTIPOINT)_\d+$'
    if not re.match(pattern, marker_id):
        return (False, "Invalid marker ID format. Expected: TYPE_NUMBER (e.g., CUT_0)")

    # Check uniqueness if existing_ids provided
    if existing_ids is not None and marker_id in existing_ids:
        return (False, "Marker ID already exists")

    return (True, None)


def validate_coordinates(x, y, layout=None):
    """Validate coordinates are within layout bounds

    Args:
        x, y: Coordinates in microns
        layout: Optional pya.Layout object to check bounds

    Returns:
        tuple: (is_valid, error_message)

    Example:
        >>> validate_coordinates(10.5, 20.3)
        (True, None)
        >>> validate_coordinates(float('inf'), 0)
        (False, 'Coordinates cannot be infinite or NaN')
    """
    import math

    # Check for invalid numeric values
    if not math.isfinite(x) or not math.isfinite(y):
        return (False, "Coordinates cannot be infinite or NaN")

    # If layout provided, check bounds
    if layout is not None:
        try:
            # Get layout bounding box if available
            bbox = layout.top_cell().bbox()
            if bbox and not bbox.empty():
                # Convert to microns
                dbu = layout.dbu
                min_x = bbox.left * dbu
                min_y = bbox.bottom * dbu
                max_x = bbox.right * dbu
                max_y = bbox.top * dbu

                # Check if coordinates are within bounds (with some tolerance)
                tolerance = 1000.0  # 1mm tolerance
                if (x < min_x - tolerance or x > max_x + tolerance or
                    y < min_y - tolerance or y > max_y + tolerance):
                    return (False, f"Coordinates ({x:.2f}, {y:.2f}) are outside layout bounds")
        except:
            # If we can't get bounds, just skip this check
            pass

    return (True, None)


def validate_file_path(filepath, must_exist=False, must_be_writable=False):
    """Validate file path is valid and optionally check existence/writeability

    Args:
        filepath (str): File path to validate
        must_exist (bool): If True, file must exist
        must_be_writable (bool): If True, directory must be writable

    Returns:
        tuple: (is_valid, error_message)

    Example:
        >>> validate_file_path("/tmp/test.json")
        (True, None)
        >>> validate_file_path("")
        (False, 'File path cannot be empty')
    """
    if not filepath:
        return (False, "File path cannot be empty")

    # Check if path contains invalid characters (basic check)
    if '\0' in filepath:
        return (False, "File path contains invalid characters")

    # Check existence if required
    if must_exist and not os.path.exists(filepath):
        return (False, f"File does not exist: {filepath}")

    # Check if directory is writable if required
    if must_be_writable:
        directory = os.path.dirname(filepath) or '.'
        if not os.path.exists(directory):
            return (False, f"Directory does not exist: {directory}")
        if not os.access(directory, os.W_OK):
            return (False, f"Directory is not writable: {directory}")

    return (True, None)


def validate_conversion(source_marker, target_type):
    """Check if a marker can be converted to target type

    Args:
        source_marker: Source marker object
        target_type (str): Target marker type ('cut', 'connect', 'probe', 'multipoint')

    Returns:
        tuple: (is_valid, error_message)

    Example:
        >>> class Marker:
        ...     def __init__(self, marker_type):
        ...         self.marker_type = marker_type
        ...         self.x1, self.y1 = 0, 0
        >>> m = Marker('cut')
        >>> validate_conversion(m, 'connect')
        (True, None)
    """
    if not source_marker:
        return (False, "Source marker is None")

    # Get source type
    source_type = getattr(source_marker, 'marker_type', 'unknown').lower()

    # Normalize target type
    target_type = target_type.lower()

    # Check if conversion to same type
    if source_type == target_type:
        return (False, f"Marker is already type '{target_type}'")

    # Probe markers (single point) can convert to anything
    if source_type == 'probe':
        return (True, None)

    # Two-point markers (cut, connect) can convert between each other and to multipoint
    if source_type in ('cut', 'connect'):
        if target_type in ('cut', 'connect', 'probe', 'multipoint'):
            return (True, None)
        return (False, f"Cannot convert from '{source_type}' to '{target_type}'")

    # Multipoint markers can convert to two-point if they have exactly 2 points
    if source_type == 'multipoint':
        if hasattr(source_marker, 'points'):
            num_points = len(source_marker.points)
            if num_points == 1 and target_type == 'probe':
                return (True, None)
            elif num_points == 2 and target_type in ('cut', 'connect'):
                return (True, None)
            elif num_points >= 2:
                return (False, f"Multipoint marker with {num_points} points can only convert to multipoint or (if 2 points) cut/connect")
            else:
                return (False, "Multipoint marker has no points")
        return (False, "Multipoint marker has no points attribute")

    return (False, f"Unknown source marker type: {source_type}")
