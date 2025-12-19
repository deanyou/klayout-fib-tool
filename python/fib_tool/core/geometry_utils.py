"""Geometry utility functions for FIB Tool

This module provides common geometry calculations for markers including
distance calculations, direction detection, and bounding box computations.
"""

import math


def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points

    Args:
        x1, y1: First point coordinates (in microns)
        x2, y2: Second point coordinates (in microns)

    Returns:
        float: Distance in microns

    Example:
        >>> calculate_distance(0, 0, 3, 4)
        5.0
    """
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def calculate_direction(x1, y1, x2, y2):
    """Determine direction from point1 to point2

    Args:
        x1, y1: Starting point coordinates
        x2, y2: Ending point coordinates

    Returns:
        str: Direction as 'up', 'down', 'left', or 'right'

    Example:
        >>> calculate_direction(0, 0, 10, 0)
        'right'
        >>> calculate_direction(0, 0, 0, 10)
        'up'
    """
    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > abs(dy):
        return 'right' if dx > 0 else 'left'
    else:
        return 'up' if dy > 0 else 'down'


def get_bounding_box(points):
    """Calculate bounding box for a list of points

    Args:
        points: List of (x, y) tuples in microns

    Returns:
        tuple: (min_x, min_y, max_x, max_y) or None if points is empty

    Example:
        >>> get_bounding_box([(0, 0), (10, 5), (3, 8)])
        (0, 0, 10, 8)
    """
    if not points:
        return None

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    return (min(xs), min(ys), max(xs), max(ys))


def get_marker_center(marker):
    """Get center point of a marker

    Args:
        marker: Marker object with attributes (x1, y1) or (x1, y1, x2, y2)
               or points list for multipoint markers

    Returns:
        tuple: (center_x, center_y) in microns

    Example:
        For a CUT marker from (0,0) to (10, 10):
        >>> class Marker:
        ...     def __init__(self):
        ...         self.x1, self.y1 = 0, 0
        ...         self.x2, self.y2 = 10, 10
        >>> m = Marker()
        >>> get_marker_center(m)
        (5.0, 5.0)
    """
    # Check if marker has points list (multipoint marker)
    if hasattr(marker, 'points') and marker.points:
        bbox = get_bounding_box(marker.points)
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            return ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    # Check if marker has two points (line marker)
    if hasattr(marker, 'x2') and hasattr(marker, 'y2'):
        return ((marker.x1 + marker.x2) / 2.0, (marker.y1 + marker.y2) / 2.0)

    # Single point marker
    if hasattr(marker, 'x1') and hasattr(marker, 'y1'):
        return (marker.x1, marker.y1)

    # Fallback
    return (0.0, 0.0)
