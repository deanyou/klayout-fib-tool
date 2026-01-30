"""Dialog management for FIB Tool

This module consolidates all QMessageBox and dialog operations into a single
manager class, replacing 41+ scattered QMessageBox calls throughout the codebase.
"""

try:
    import pya
except ImportError:
    pya = None


class FibDialogManager:
    """Centralized dialog manager for all user interactions

    This class provides standardized dialogs for:
    - Confirmations (Yes/No questions)
    - Warnings and errors
    - Information messages
    - File operations (save/load/overwrite)

    All methods are static and can be called without instantiation.
    """

    # Dialog result constants (Phase 3: for three-button dialogs)
    RESULT_YES = 'yes'
    RESULT_NO = 'no'
    RESULT_CANCEL = 'cancel'
    RESULT_OK = 'ok'

    @staticmethod
    def confirm(title, message, parent=None):
        """Show a Yes/No confirmation dialog

        Args:
            title (str): Dialog title
            message (str): Confirmation message
            parent: Parent widget (optional)

        Returns:
            bool: True if user clicked Yes, False if No

        Example:
            >>> FibDialogManager.confirm("Delete", "Delete marker?")
            True  # if user clicks Yes
        """
        if pya:
            result = pya.QMessageBox.question(
                parent,
                title,
                message,
                pya.QMessageBox.Yes | pya.QMessageBox.No,
                pya.QMessageBox.No
            )
            return result == pya.QMessageBox.Yes
        return False

    @staticmethod
    def confirm_with_cancel(title, message, parent=None):
        """Show a Yes/No/Cancel confirmation dialog (Phase 3)

        Args:
            title (str): Dialog title
            message (str): Confirmation message
            parent: Parent widget (optional)

        Returns:
            str: 'yes', 'no', or 'cancel'

        Example:
            >>> result = FibDialogManager.confirm_with_cancel("Save", "Save changes?")
            >>> if result == FibDialogManager.RESULT_YES:
            >>>     save()
            >>> elif result == FibDialogManager.RESULT_CANCEL:
            >>>     return
        """
        if pya:
            result = pya.MessageBox.warning(
                title,
                message,
                pya.MessageBox.Yes | pya.MessageBox.No | pya.MessageBox.Cancel
            )
            if result == pya.MessageBox.Yes:
                return FibDialogManager.RESULT_YES
            elif result == pya.MessageBox.No:
                return FibDialogManager.RESULT_NO
            else:
                return FibDialogManager.RESULT_CANCEL
        return FibDialogManager.RESULT_CANCEL

    @staticmethod
    def confirm_delete(marker_id, parent=None):
        """Confirm marker deletion

        Args:
            marker_id (str): ID of marker to delete
            parent: Parent widget (optional)

        Returns:
            bool: True if user confirms deletion
        """
        return FibDialogManager.confirm(
            "Confirm Delete",
            f"Are you sure you want to delete marker '{marker_id}'?",
            parent
        )

    @staticmethod
    def confirm_clear_all(count, parent=None):
        """Confirm clearing all markers

        Args:
            count (int): Number of markers to clear
            parent: Parent widget (optional)

        Returns:
            bool: True if user confirms clearing all
        """
        return FibDialogManager.confirm(
            "Confirm Clear All",
            f"Are you sure you want to clear all {count} markers? This cannot be undone.",
            parent
        )

    @staticmethod
    def confirm_overwrite(filepath, parent=None):
        """Confirm file overwrite

        Args:
            filepath (str): Path to file that would be overwritten
            parent: Parent widget (optional)

        Returns:
            bool: True if user confirms overwrite
        """
        import os
        filename = os.path.basename(filepath)
        return FibDialogManager.confirm(
            "Confirm Overwrite",
            f"File '{filename}' already exists. Overwrite?",
            parent
        )

    @staticmethod
    def warning(message, title="Warning", parent=None):
        """Show a warning message (Phase 3: added title parameter)

        Args:
            message (str): Warning message
            title (str): Dialog title (default: "Warning")
            parent: Parent widget (optional)
        """
        if pya:
            pya.MessageBox.warning(title, message, pya.MessageBox.Ok)

    @staticmethod
    def error(message, title="Error", parent=None):
        """Show an error message (Phase 3: added title parameter)

        Args:
            message (str): Error message
            title (str): Dialog title (default: "Error")
            parent: Parent widget (optional)
        """
        if pya:
            pya.MessageBox.warning(title, message, pya.MessageBox.Ok)

    @staticmethod
    def info(message, title="Information", parent=None):
        """Show an information message (Phase 3: added title parameter)

        Args:
            message (str): Information message
            title (str): Dialog title (default: "Information")
            parent: Parent widget (optional)
        """
        if pya:
            pya.MessageBox.info(title, message, pya.MessageBox.Ok)

    @staticmethod
    def show_export_success(filepath, parent=None):
        """Show export success message

        Args:
            filepath (str): Path where file was exported
            parent: Parent widget (optional)
        """
        import os
        filename = os.path.basename(filepath)
        FibDialogManager.info(
            f"Successfully exported to '{filename}'",
            parent
        )

    @staticmethod
    def show_import_success(count, parent=None):
        """Show import success message

        Args:
            count (int): Number of markers imported
            parent: Parent widget (optional)
        """
        FibDialogManager.info(
            f"Successfully imported {count} marker{'s' if count != 1 else ''}",
            parent
        )

    @staticmethod
    def show_error_no_markers(parent=None):
        """Show error when no markers exist for an operation

        Args:
            parent: Parent widget (optional)
        """
        FibDialogManager.error("No markers to export", parent)

    @staticmethod
    def show_error_no_layout(parent=None):
        """Show error when no layout is open

        Args:
            parent: Parent widget (optional)
        """
        FibDialogManager.error("No layout open. Please open a GDS file first.", parent)

    @staticmethod
    def show_error_no_cell(parent=None):
        """Show error when no cell is selected

        Args:
            parent: Parent widget (optional)
        """
        FibDialogManager.error("No cell selected", parent)

    @staticmethod
    def show_error_file_not_found(filepath, parent=None):
        """Show error when file is not found

        Args:
            filepath (str): Path to file that was not found
            parent: Parent widget (optional)
        """
        import os
        filename = os.path.basename(filepath)
        FibDialogManager.error(f"File not found: '{filename}'", parent)

    @staticmethod
    def show_error_invalid_file(filepath, reason="", parent=None):
        """Show error when file format is invalid

        Args:
            filepath (str): Path to invalid file
            reason (str): Optional reason why file is invalid
            parent: Parent widget (optional)
        """
        import os
        filename = os.path.basename(filepath)
        message = f"Invalid file: '{filename}'"
        if reason:
            message += f"\n\nReason: {reason}"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_conversion_failed(marker_id, target_type, reason="", parent=None):
        """Show error when marker conversion fails

        Args:
            marker_id (str): ID of marker that failed to convert
            target_type (str): Target marker type
            reason (str): Optional reason for failure
            parent: Parent widget (optional)
        """
        message = f"Cannot convert marker '{marker_id}' to type '{target_type}'"
        if reason:
            message += f"\n\nReason: {reason}"
        FibDialogManager.error(message, parent)

    @staticmethod
    def ask_save_filepath(default_filename="", file_filter="", parent=None):
        """Ask user for a save file path

        Args:
            default_filename (str): Default filename to suggest
            file_filter (str): File type filter (e.g., "JSON files (*.json)")
            parent: Parent widget (optional)

        Returns:
            str: Selected filepath or empty string if cancelled
        """
        if pya:
            filepath = pya.QFileDialog.getSaveFileName(
                parent,
                "Save File",
                default_filename,
                file_filter
            )
            return filepath if filepath else ""
        return ""

    @staticmethod
    def ask_open_filepath(file_filter="", parent=None):
        """Ask user for a file to open

        Args:
            file_filter (str): File type filter (e.g., "JSON files (*.json)")
            parent: Parent widget (optional)

        Returns:
            str: Selected filepath or empty string if cancelled
        """
        if pya:
            filepath = pya.QFileDialog.getOpenFileName(
                parent,
                "Open File",
                "",
                file_filter
            )
            return filepath if filepath else ""
        return ""

    # --------------------------------------------------------------------------
    # MVF Error Handlers (Linus-style minimal additions)
    # --------------------------------------------------------------------------

    @staticmethod
    def show_error_screenshot_failed(marker_id, zoom_level, reason="", parent=None):
        """Screenshot capture failed (overview/zoom2x/detail)

        Args:
            marker_id (str): ID of marker for which screenshot failed
            zoom_level (str): Zoom level that failed (e.g., "overview", "zoom2x")
            reason (str): Optional reason for failure
            parent: Parent widget (optional)
        """
        import os
        message = f"Failed to capture screenshot for marker '{marker_id}'\nZoom level: {zoom_level}"
        if reason:
            message += f"\n\nReason: {reason}"
        message += "\n\nPlease check:\n• Layout is open and valid\n• Marker is visible in current view"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_active_view_required(parent=None):
        """No active KLayout view found

        Args:
            parent: Parent widget (optional)
        """
        message = "No active layout view found"
        message += "\n\nPlease:\n• Open a GDS/OASIS file\n• Ensure a cell is loaded"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_directory_creation(dir_path, reason="", parent=None):
        """Directory creation failed

        Args:
            dir_path (str): Path to directory that failed to create
            reason (str): Optional reason for failure
            parent: Parent widget (optional)
        """
        import os
        dir_name = os.path.basename(dir_path)
        message = f"Failed to create export directory:\n{dir_name}"
        if reason:
            message += f"\n\nReason: {reason}"
        message += "\n\nPlease check:\n• Parent directory exists\n• Write permissions\n• Disk space available"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_json_parse(filepath, reason="", parent=None):
        """JSON file format error

        Args:
            filepath (str): Path to invalid JSON file
            reason (str): Optional reason for failure
            parent: Parent widget (optional)
        """
        import os
        filename = os.path.basename(filepath)
        message = f"Invalid JSON file: {filename}"
        if reason:
            message += f"\n\nReason: {reason}"
        message += "\n\nThe file may be:\n• Corrupted\n• Not a valid FIB Tool export\n• From incompatible version"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_permission_denied(filepath, operation="access", parent=None):
        """File permission denied

        Args:
            filepath (str): Path to file with permission issue
            operation (str): Operation that was denied (e.g., "read", "write")
            parent: Parent widget (optional)
        """
        import os
        filename = os.path.basename(filepath)
        message = f"Permission denied: Cannot {operation} file\n{filename}"
        message += "\n\nPlease check:\n• File permissions\n• File is not locked by another program\n• You have necessary access rights"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_layer_creation_failed(layer_num, reason="", parent=None):
        """FIB layer creation failed

        Args:
            layer_num (int): Layer number that failed to create
            reason (str): Optional reason for failure
            parent: Parent widget (optional)
        """
        message = f"Failed to create FIB layer {layer_num}"
        if reason:
            message += f"\n\nReason: {reason}"
        message += "\n\nPlease:\n• Ensure a layout is open\n• Check if layer already exists with different properties"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_marker_not_found(marker_id, parent=None):
        """Marker not found

        Args:
            marker_id (str): ID of marker that was not found
            parent: Parent widget (optional)
        """
        message = f"Marker not found: '{marker_id}'"
        message += "\n\nThe marker may have been:\n• Deleted\n• Renamed\n• Not yet saved"
        FibDialogManager.error(message, parent)

    @staticmethod
    def show_error_insufficient_points(marker_id, required=2, actual=0, parent=None):
        """Marker has insufficient points

        Args:
            marker_id (str): ID of marker with insufficient points
            required (int): Number of points required
            actual (int): Actual number of points
            parent: Parent widget (optional)
        """
        message = f"Marker '{marker_id}' has insufficient points"
        message += f"\n\nRequired: {required} points\nActual: {actual} points"
        message += "\n\nPlease add more points to complete this marker."
        FibDialogManager.error(message, parent)
