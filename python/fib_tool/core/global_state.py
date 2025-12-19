"""Global state management for FIB Tool

This module provides centralized state management to replace sys.modules accesses.
It manages marker counters, active marker list, screenshots, and current mode.
"""


class FibGlobalState:
    """Centralized state manager for FIB Tool

    This class replaces all sys.modules['__main__'] global state accesses.
    It provides a clean, testable interface for managing application state.

    Attributes:
        marker_counters (dict): Counter for each marker type
        markers (list): List of all active markers
        screenshots (dict): Screenshot data indexed by marker ID
        current_mode (str): Current drawing mode ('cut', 'connect', 'probe', None)
    """

    def __init__(self):
        """Initialize global state with default values"""
        self.marker_counters = {
            'cut': 0,
            'connect': 0,
            'probe': 0,
            'multipoint': 0
        }
        self.markers = []
        self.screenshots = {}
        self.current_mode = None
        self._marker_id_set = set()  # For fast ID lookup

    def reset_counters(self):
        """Reset all marker counters to zero"""
        for key in self.marker_counters:
            self.marker_counters[key] = 0

    def get_next_marker_id(self, marker_type):
        """Get next ID for marker type and increment counter

        Args:
            marker_type (str): Type of marker ('cut', 'connect', 'probe', 'multipoint')

        Returns:
            str: Next marker ID (e.g., "CUT_0", "PROBE_5")

        Example:
            >>> state = FibGlobalState()
            >>> state.get_next_marker_id('cut')
            'CUT_0'
            >>> state.get_next_marker_id('cut')
            'CUT_1'
        """
        marker_type = marker_type.lower()
        if marker_type not in self.marker_counters:
            self.marker_counters[marker_type] = 0

        marker_id = f"{marker_type.upper()}_{self.marker_counters[marker_type]}"
        self.marker_counters[marker_type] += 1
        self._marker_id_set.add(marker_id)
        return marker_id

    def add_marker(self, marker):
        """Add marker to the active marker list

        Args:
            marker: Marker object to add

        Returns:
            bool: True if added successfully, False if marker ID already exists
        """
        if not marker:
            return False

        # Check if marker ID already exists
        marker_id = getattr(marker, 'id', None)
        if marker_id and marker_id in self._marker_id_set:
            return False

        self.markers.append(marker)
        if marker_id:
            self._marker_id_set.add(marker_id)
        return True

    def remove_marker(self, marker_or_id):
        """Remove marker from the active marker list

        Args:
            marker_or_id: Marker object or marker ID string

        Returns:
            bool: True if removed, False if not found
        """
        if isinstance(marker_or_id, str):
            # Remove by ID
            marker_id = marker_or_id
            for i, m in enumerate(self.markers):
                if getattr(m, 'id', None) == marker_id:
                    self.markers.pop(i)
                    self._marker_id_set.discard(marker_id)
                    # Also remove screenshot if exists
                    self.screenshots.pop(marker_id, None)
                    return True
            return False
        else:
            # Remove by object
            marker = marker_or_id
            if marker in self.markers:
                self.markers.remove(marker)
                marker_id = getattr(marker, 'id', None)
                if marker_id:
                    self._marker_id_set.discard(marker_id)
                    self.screenshots.pop(marker_id, None)
                return True
            return False

    def clear_markers(self):
        """Clear all markers and reset state"""
        self.markers = []
        self.screenshots = {}
        self._marker_id_set = set()

    def get_marker_by_id(self, marker_id):
        """Get marker by ID

        Args:
            marker_id (str): Marker ID to find

        Returns:
            Marker object or None if not found
        """
        for marker in self.markers:
            if getattr(marker, 'id', None) == marker_id:
                return marker
        return None

    def marker_id_exists(self, marker_id):
        """Check if marker ID already exists

        Args:
            marker_id (str): Marker ID to check

        Returns:
            bool: True if ID exists, False otherwise
        """
        return marker_id in self._marker_id_set

    def get_marker_count(self):
        """Get total number of active markers

        Returns:
            int: Number of markers
        """
        return len(self.markers)

    def add_screenshot(self, marker_id, screenshot_data):
        """Add screenshot for a marker

        Args:
            marker_id (str): Marker ID
            screenshot_data: Screenshot data (format depends on implementation)

        Returns:
            bool: True if added successfully
        """
        if not marker_id:
            return False
        self.screenshots[marker_id] = screenshot_data
        return True

    def get_screenshot(self, marker_id):
        """Get screenshot for a marker

        Args:
            marker_id (str): Marker ID

        Returns:
            Screenshot data or None if not found
        """
        return self.screenshots.get(marker_id)

    def has_screenshot(self, marker_id):
        """Check if marker has a screenshot

        Args:
            marker_id (str): Marker ID

        Returns:
            bool: True if screenshot exists
        """
        return marker_id in self.screenshots

    def set_mode(self, mode):
        """Set current drawing mode

        Args:
            mode (str): Mode name ('cut', 'connect', 'probe', None)
        """
        self.current_mode = mode

    def get_mode(self):
        """Get current drawing mode

        Returns:
            str: Current mode or None
        """
        return self.current_mode
