"""File I/O management for FIB Tool

This module handles all file operations including JSON export/import
and CSV export for markers.
"""

import json
import os
from ..core.logging_utils import safe_print as print
from ..ui.dialog_manager import FibDialogManager


class FibFileManager:
    """Manages file I/O operations for markers

    This class consolidates all file operations including:
    - JSON export/import
    - CSV export
    - File path handling
    """

    @staticmethod
    def save_markers_to_json(markers, filename, marker_notes_dict=None, marker_counters=None):
        """Save markers to JSON file

        Args:
            markers (list): List of marker objects to save
            filename (str): Output JSON filepath
            marker_notes_dict (dict): Optional notes dictionary
            marker_counters (dict): Optional marker counters

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure we save to a writable location
            if not os.path.isabs(filename):
                # If relative path, save to user's home directory
                home_dir = os.path.expanduser("~")
                filename = os.path.join(home_dir, filename)
                print(f"[File Manager] Saving to home directory: {filename}")

            from .marker_codec import marker_to_record
            markers_data = [marker_to_record(marker) for marker in markers]

            # Save to file
            with open(filename, 'w') as f:
                json.dump({
                    'version': '1.0',
                    'markers': markers_data,
                    'marker_notes_dict': marker_notes_dict or {},
                    'marker_counters': marker_counters or {'cut': 0, 'connect': 0, 'probe': 0}
                }, f, indent=2)

            print(f"[File Manager] Saved {len(markers_data)} markers to {filename}")
            return True

        except Exception as e:
            print(f"[File Manager] Error saving to JSON: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def load_markers_from_json(filename):
        """Load markers from JSON file

        Args:
            filename (str): JSON filepath to load

        Returns:
            tuple: (markers_list, marker_notes_dict, marker_counters) or (None, None, None) if failed
                   markers_list: List of marker dictionaries (not marker objects)
                   marker_notes_dict: Dictionary of marker notes
                   marker_counters: Dictionary of marker counters
        """
        try:
            # Handle relative paths - look in home directory
            if not os.path.isabs(filename):
                home_dir = os.path.expanduser("~")
                full_path = os.path.join(home_dir, filename)
                if os.path.exists(full_path):
                    filename = full_path
                    print(f"[File Manager] Loading from home directory: {filename}")
                elif not os.path.exists(filename):
                    print(f"[File Manager] File not found in current dir, trying home: {full_path}")
                    filename = full_path

            # Check file exists
            if not os.path.exists(filename):
                print(f"[File Manager] File not found: {filename}")
                return (None, None, None)

            # Load from file
            with open(filename, 'r') as f:
                data = json.load(f)

            # Extract components
            markers_data = data.get('markers', [])
            marker_notes_dict = data.get('marker_notes_dict', {})
            marker_counters = data.get('marker_counters', {'cut': 0, 'connect': 0, 'probe': 0})

            print(f"[File Manager] Loaded {len(markers_data)} markers from {filename}")
            return (markers_data, marker_notes_dict, marker_counters)

        except json.JSONDecodeError as e:
            # Specific handling for JSON format errors
            error_msg = f"Invalid JSON format at line {e.lineno}"
            print(f"[File Manager] JSONDecodeError: {error_msg}")
            FibDialogManager.show_error_json_parse(filename, error_msg)
            return (None, None, None)
        except FileNotFoundError:
            # File not found error
            print(f"[File Manager] File not found: {filename}")
            FibDialogManager.show_error_file_not_found(filename)
            return (None, None, None)
        except PermissionError:
            # Permission denied error
            print(f"[File Manager] Permission denied: {filename}")
            FibDialogManager.show_error_permission_denied(filename, "read")
            return (None, None, None)
        except Exception as e:
            # Other errors
            print(f"[File Manager] Error loading from JSON: {e}")
            import traceback
            traceback.print_exc()
            FibDialogManager.show_error_invalid_file(filename, str(e))
            return (None, None, None)

    @staticmethod
    def export_markers_to_csv(markers, filename):
        """Export markers to CSV file

        Args:
            markers (list): List of marker objects
            filename (str): Output CSV filepath

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            import csv

            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['ID', 'Type', 'X1', 'Y1', 'X2', 'Y2', 'Notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for marker in markers:
                    marker_class = marker.__class__.__name__
                    marker_type = marker_class.replace('Marker', '').upper()

                    row = {
                        'ID': marker.id,
                        'Type': marker_type,
                        'Notes': getattr(marker, 'notes', '')
                    }

                    if hasattr(marker, 'x1'):  # CUT or CONNECT
                        row['X1'] = marker.x1
                        row['Y1'] = marker.y1
                        row['X2'] = marker.x2
                        row['Y2'] = marker.y2
                    elif hasattr(marker, 'x'):  # PROBE
                        row['X1'] = marker.x
                        row['Y1'] = marker.y
                        row['X2'] = ''
                        row['Y2'] = ''
                    else:
                        row['X1'] = row['Y1'] = row['X2'] = row['Y2'] = ''

                    writer.writerow(row)

            print(f"[File Manager] Exported {len(markers)} markers to CSV: {filename}")
            return True

        except Exception as e:
            print(f"[File Manager] Error exporting to CSV: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def validate_json_file(filename):
        """Validate JSON file format

        Args:
            filename (str): JSON filepath to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        if not os.path.exists(filename):
            return (False, f"File not found: {filename}")

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            if 'markers' not in data:
                return (False, "JSON file missing 'markers' field")

            if not isinstance(data['markers'], list):
                return (False, "'markers' field must be a list")

            return (True, None)

        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON format: {e}")
        except Exception as e:
            return (False, f"Error reading file: {e}")
