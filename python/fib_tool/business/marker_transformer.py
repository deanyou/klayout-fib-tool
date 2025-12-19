"""Marker transformation utilities for FIB Tool

This module provides functions to convert markers between different types:
- Cut ↔ Connect ↔ Probe
- Single-point ↔ Multi-point

This eliminates ~20% code duplication by centralizing conversion logic.
"""

from ..markers import CutMarker, ConnectMarker, ProbeMarker
from ..core.validation_utils import validate_conversion

# Check if multipoint markers module exists
try:
    from ..multipoint_markers import MultiPointCutMarker, MultiPointConnectMarker
    MULTIPOINT_AVAILABLE = True
except ImportError:
    MULTIPOINT_AVAILABLE = False


class FibMarkerTransformer:
    """Handles all marker type conversions

    This class centralizes the logic for converting markers between types,
    replacing duplicated conversion code throughout fib_panel.py.
    """

    @staticmethod
    def can_convert(marker, target_type):
        """Check if marker can be converted to target type

        Args:
            marker: Source marker object
            target_type (str): Target type ('cut', 'connect', 'probe', 'multipoint')

        Returns:
            tuple: (can_convert, error_message)
        """
        return validate_conversion(marker, target_type)

    @staticmethod
    def convert_to_cut(marker, line_width=6):
        """Convert any marker to CUT type

        Args:
            marker: Source marker (Connect, Probe, or MultiPoint)
            line_width (float): Line width for the cut marker

        Returns:
            CutMarker: New CUT marker or None if conversion fails

        Example:
            >>> transformer = FibMarkerTransformer()
            >>> cut_marker = transformer.convert_to_cut(connect_marker)
        """
        # Validate conversion
        can_convert, error = FibMarkerTransformer.can_convert(marker, 'cut')
        if not can_convert:
            print(f"[Transformer] Cannot convert to CUT: {error}")
            return None

        marker_id = getattr(marker, 'id', 'CUT_0')

        # Get coordinates based on marker type
        marker_class = marker.__class__.__name__

        if 'Probe' in marker_class:
            # Probe marker: create a small horizontal cut at probe position
            x, y = marker.x, marker.y
            x1, y1 = x - 0.5, y  # 1 micron horizontal line
            x2, y2 = x + 0.5, y
        elif 'MultiPoint' in marker_class:
            # MultiPoint: use first two points
            if hasattr(marker, 'points') and len(marker.points) >= 2:
                x1, y1 = marker.points[0]
                x2, y2 = marker.points[1]
            else:
                print(f"[Transformer] MultiPoint marker has insufficient points")
                return None
        else:
            # Connect or other two-point marker
            x1, y1 = marker.x1, marker.y1
            x2, y2 = marker.x2, marker.y2

        # Create new CUT marker
        new_marker = CutMarker(marker_id, x1, y1, x2, y2, line_width)

        # Preserve layer information if available
        if hasattr(marker, 'layer1'):
            new_marker.layer1 = marker.layer1
        if hasattr(marker, 'layer2'):
            new_marker.layer2 = marker.layer2

        return new_marker

    @staticmethod
    def convert_to_connect(marker, line_width=6):
        """Convert any marker to CONNECT type

        Args:
            marker: Source marker (Cut, Probe, or MultiPoint)
            line_width (float): Line width for the connect marker

        Returns:
            ConnectMarker: New CONNECT marker or None if conversion fails
        """
        # Validate conversion
        can_convert, error = FibMarkerTransformer.can_convert(marker, 'connect')
        if not can_convert:
            print(f"[Transformer] Cannot convert to CONNECT: {error}")
            return None

        marker_id = getattr(marker, 'id', 'CONNECT_0')
        marker_class = marker.__class__.__name__

        if 'Probe' in marker_class:
            # Probe marker: create a small horizontal connect at probe position
            x, y = marker.x, marker.y
            x1, y1 = x - 0.5, y
            x2, y2 = x + 0.5, y
        elif 'MultiPoint' in marker_class:
            # MultiPoint: use first two points
            if hasattr(marker, 'points') and len(marker.points) >= 2:
                x1, y1 = marker.points[0]
                x2, y2 = marker.points[1]
            else:
                print(f"[Transformer] MultiPoint marker has insufficient points")
                return None
        else:
            # Cut or other two-point marker
            x1, y1 = marker.x1, marker.y1
            x2, y2 = marker.x2, marker.y2

        # Create new CONNECT marker
        new_marker = ConnectMarker(marker_id, x1, y1, x2, y2, line_width)

        # Preserve layer information if available
        if hasattr(marker, 'layer1'):
            new_marker.layer1 = marker.layer1
        if hasattr(marker, 'layer2'):
            new_marker.layer2 = marker.layer2

        return new_marker

    @staticmethod
    def convert_to_probe(marker, line_width=6):
        """Convert any marker to PROBE type

        Args:
            marker: Source marker (Cut, Connect, or MultiPoint)
            line_width (float): Line width for the probe marker

        Returns:
            ProbeMarker: New PROBE marker or None if conversion fails
        """
        # Validate conversion
        can_convert, error = FibMarkerTransformer.can_convert(marker, 'probe')
        if not can_convert:
            print(f"[Transformer] Cannot convert to PROBE: {error}")
            return None

        marker_id = getattr(marker, 'id', 'PROBE_0')
        marker_class = marker.__class__.__name__

        if 'MultiPoint' in marker_class:
            # MultiPoint with single point
            if hasattr(marker, 'points') and len(marker.points) >= 1:
                x, y = marker.points[0]
            else:
                print(f"[Transformer] MultiPoint marker has no points")
                return None
        else:
            # Two-point marker: use first point
            x, y = marker.x1, marker.y1

        # Create new PROBE marker
        new_marker = ProbeMarker(marker_id, x, y, line_width)

        # Preserve target layer if available
        if hasattr(marker, 'target_layer'):
            new_marker.target_layer = marker.target_layer
        elif hasattr(marker, 'layer1'):
            new_marker.target_layer = marker.layer1

        return new_marker

    @staticmethod
    def convert_to_multipoint(marker, marker_type='cut', line_width=6):
        """Convert any marker to MultiPoint type

        Args:
            marker: Source marker (Cut, Connect, or Probe)
            marker_type (str): Type of multipoint marker ('cut' or 'connect')
            line_width (float): Line width for the multipoint marker

        Returns:
            MultiPointMarker: New MULTIPOINT marker or None if conversion fails
        """
        if not MULTIPOINT_AVAILABLE:
            print(f"[Transformer] MultiPoint markers not available")
            return None

        # Validate conversion
        can_convert, error = FibMarkerTransformer.can_convert(marker, 'multipoint')
        if not can_convert:
            print(f"[Transformer] Cannot convert to MULTIPOINT: {error}")
            return None

        marker_id = getattr(marker, 'id', 'MULTIPOINT_0')
        marker_class = marker.__class__.__name__

        # Collect points from source marker
        points = []
        if 'Probe' in marker_class:
            points = [(marker.x, marker.y)]
        elif 'MultiPoint' in marker_class:
            # Already multipoint, return copy
            if hasattr(marker, 'points'):
                points = list(marker.points)
            else:
                return None
        else:
            # Two-point marker
            points = [(marker.x1, marker.y1), (marker.x2, marker.y2)]

        # Create appropriate multipoint marker
        if marker_type.lower() == 'cut':
            new_marker = MultiPointCutMarker(marker_id, points, line_width)
        elif marker_type.lower() == 'connect':
            new_marker = MultiPointConnectMarker(marker_id, points, line_width)
        else:
            print(f"[Transformer] Unknown multipoint type: {marker_type}")
            return None

        return new_marker

    @staticmethod
    def get_marker_type(marker):
        """Get the type string for a marker

        Args:
            marker: Marker object

        Returns:
            str: Marker type ('cut', 'connect', 'probe', 'multipoint')
        """
        if not marker:
            return 'unknown'

        marker_class = marker.__class__.__name__.lower()

        if 'cut' in marker_class:
            return 'cut'
        elif 'connect' in marker_class:
            return 'connect'
        elif 'probe' in marker_class:
            return 'probe'
        elif 'multipoint' in marker_class:
            return 'multipoint'
        else:
            return 'unknown'
