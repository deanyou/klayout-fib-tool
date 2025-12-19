"""Export management for FIB Tool

This module provides a clean API for exporting markers to various formats
including PDF and HTML reports with screenshots.

This is a facade that wraps the existing screenshot_export and report modules.
"""

import os


class FibExportManager:
    """Manages export operations for markers

    This class provides a unified interface for exporting markers
    to different formats (PDF, HTML, etc.)
    """

    @staticmethod
    def export_to_html(markers, screenshots_dict, output_path):
        """Export markers to HTML report with screenshots

        Args:
            markers (list): List of marker objects
            screenshots_dict (dict): Dictionary of screenshots indexed by marker ID
            output_path (str): Output HTML file path

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            from ..screenshot_export import generate_html_report_with_screenshots

            result = generate_html_report_with_screenshots(
                markers,
                screenshots_dict,
                output_path
            )
            return result

        except Exception as e:
            print(f"[Export Manager] Error exporting to HTML: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def export_to_pdf(markers, screenshots_dict, output_path):
        """Export markers to PDF report

        Args:
            markers (list): List of marker objects
            screenshots_dict (dict): Dictionary of screenshots indexed by marker ID
            output_path (str): Output PDF file path

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            from ..report import generate_pdf_report

            result = generate_pdf_report(
                markers,
                screenshots_dict,
                output_path
            )
            return result

        except Exception as e:
            print(f"[Export Manager] Error exporting to PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def capture_screenshot(view, marker):
        """Capture screenshot for a marker

        Args:
            view: KLayout view object
            marker: Marker object to capture

        Returns:
            screenshot data or None if failed
        """
        try:
            from ..screenshot_export import capture_marker_screenshot

            screenshot = capture_marker_screenshot(view, marker)
            return screenshot

        except Exception as e:
            print(f"[Export Manager] Error capturing screenshot: {e}")
            return None

    @staticmethod
    def create_output_directory(base_path, project_name="fib_export"):
        """Create output directory for exports

        Args:
            base_path (str): Base directory path
            project_name (str): Project name for subdirectory

        Returns:
            str: Full output directory path or None if failed
        """
        try:
            output_dir = os.path.join(base_path, project_name)
            os.makedirs(output_dir, exist_ok=True)
            print(f"[Export Manager] Created output directory: {output_dir}")
            return output_dir

        except Exception as e:
            print(f"[Export Manager] Error creating output directory: {e}")
            return None

    @staticmethod
    def validate_export_prerequisites(markers):
        """Validate that export can proceed

        Args:
            markers (list): List of markers to export

        Returns:
            tuple: (is_valid, error_message)
        """
        if not markers:
            return (False, "No markers to export")

        if len(markers) == 0:
            return (False, "Marker list is empty")

        return (True, None)
