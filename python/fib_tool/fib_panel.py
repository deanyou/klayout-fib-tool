#!/usr/bin/env python3
"""
FIB Panel - Dockable panel for FIB Tool management
Integrates with fib_plugin.py to provide a comprehensive FIB workflow interface
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import pya
from .markers import CutMarker, ConnectMarker, ProbeMarker
from .config import LAYERS, GEOMETRIC_PARAMS, UI_TIMEOUTS, DEFAULT_MARKER_NOTES
from .marker_menu import MarkerContextMenu
from .smart_counter import SmartCounter
from .file_dialog_helper import FileDialogHelper

# Phase 2 refactoring: Import new modular components
from .core.global_state import FibGlobalState
from .ui.dialog_manager import FibDialogManager
from .business.marker_transformer import FibMarkerTransformer
from .business.file_manager import FibFileManager
from .business.export_manager import FibExportManager

class FIBPanel(pya.QDockWidget):
    """Main FIB Panel - Dockable widget for KLayout"""
    
    def __init__(self, parent=None):
        super().__init__("FIB Panel", parent)
        self.markers_list = []  # Global marker list
        self.active_mode = None
        self.marker_notes_dict = {}  # Centralized notes storage: marker_id -> notes

        # Phase 2 refactoring: Initialize global state and business logic modules
        self.state = FibGlobalState()
        self.transformer = FibMarkerTransformer()
        self.file_manager = FibFileManager()
        self.export_manager = FibExportManager()

        # Initialize context menu handler and smart counter
        self.context_menu = MarkerContextMenu(self)
        self.smart_counter = SmartCounter(self)
        
        # Setup UI
        try:
            self.setup_ui()
            print("[FIB Panel] Initialized successfully")
        except Exception as e:
            print(f"[FIB Panel] Error in setup_ui: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup the panel UI"""
        try:
            # Main container with compact spacing
            self.container = pya.QWidget()
            self.main_layout = pya.QVBoxLayout(self.container)
            self.main_layout.setContentsMargins(2, 2, 2, 2)  # Reduced margins
            self.main_layout.setSpacing(1)  # Further reduced spacing for height compression
            
            # Title with compact styling (removed to save space)
            # title = pya.QLabel("FIB Tool Panel")
            # title.setStyleSheet("font-weight: bold; font-size: 12px; margin: 0px; padding: 1px;")
            # self.main_layout.addWidget(title)
            
            # Project management section
            self.create_project_section()
            
            # Marker creation section
            self.create_marker_section()
            
            # Coordinate jump section
            self.create_coordinate_jump_section()
            
            # Marker list section
            self.create_marker_list_section()
            
            # Set the widget
            self.setWidget(self.container)
            self.setMinimumWidth(170)  # Reduced from 250 to 170 (about 1/3 smaller)
            
        except Exception as e:
            print(f"[FIB Panel] Error in setup_ui: {e}")
            # Create minimal fallback UI
            fallback = pya.QWidget()
            fallback_layout = pya.QVBoxLayout(fallback)
            fallback_layout.addWidget(pya.QLabel("FIB Panel (Minimal Mode)"))
            self.setWidget(fallback)
    
    def create_project_section(self):
        """Create project management section"""
        try:
            group = pya.QGroupBox("Project")
            group_layout = pya.QVBoxLayout(group)
            group_layout.setSpacing(1)  # Further reduced spacing for height compression
            group_layout.setContentsMargins(2, 1, 2, 1)  # Minimal margins for height compression
            
            # First row: New, Save, Load
            btn_layout1 = pya.QHBoxLayout()
            
            btn_new = pya.QPushButton("New")
            btn_save = pya.QPushButton("Save")
            btn_load = pya.QPushButton("Load")
            
            btn_new.clicked.connect(self.on_new_project)
            btn_save.clicked.connect(self.on_save_project)
            btn_load.clicked.connect(self.on_load_project)
            
            btn_layout1.addWidget(btn_new)
            btn_layout1.addWidget(btn_save)
            btn_layout1.addWidget(btn_load)
            
            group_layout.addLayout(btn_layout1)
            
            # Second row: Export HTML
            btn_layout2 = pya.QHBoxLayout()

            btn_export_html = pya.QPushButton("Export HTML")
            btn_export_html.clicked.connect(self.on_export_html)

            btn_layout2.addWidget(btn_export_html)

            group_layout.addLayout(btn_layout2)
            self.main_layout.addWidget(group)
            
        except Exception as e:
            print(f"[FIB Panel] Error creating project section: {e}")
    
    def create_marker_section(self):
        """Create marker creation section"""
        try:
            group = pya.QGroupBox("Add Markers")
            group_layout = pya.QVBoxLayout(group)
            group_layout.setSpacing(1)  # Further reduced spacing for height compression
            group_layout.setContentsMargins(2, 1, 2, 1)  # Minimal margins for height compression
            
            # Use grid layout for perfect alignment with flexible sizing (very compact)
            grid_layout = pya.QGridLayout()
            grid_layout.setSpacing(2)  # Further reduced spacing for height compression
            
            # Create all widgets with identical sizing and styling (very compact layout)
            widget_height = 24  # Reduced from 32 to 24 for height compression
            widget_min_width = 75  # Compact width, using "MP" abbreviation for Multi Points
            
            # Cut button with explicit styling
            self.btn_cut = pya.QPushButton("Cut")
            self.btn_cut.setFixedWidth(widget_min_width)  # Fixed width for consistency
            self.btn_cut.setFixedHeight(widget_height)
            self.btn_cut.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
            
            # Cut mode combo with identical styling
            self.cut_mode_combo = pya.QComboBox()
            self.cut_mode_combo.addItem("2 Points")
            self.cut_mode_combo.addItem("MP")
            self.cut_mode_combo.setFixedWidth(widget_min_width)  # Fixed width to prevent expansion
            self.cut_mode_combo.setFixedHeight(widget_height)
            self.cut_mode_combo.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
            
            # Connect button with identical styling
            self.btn_connect = pya.QPushButton("Connect")
            self.btn_connect.setFixedWidth(widget_min_width)  # Fixed width for consistency
            self.btn_connect.setFixedHeight(widget_height)
            self.btn_connect.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
            
            # Connect mode combo with identical styling
            self.connect_mode_combo = pya.QComboBox()
            self.connect_mode_combo.addItem("2 Points")
            self.connect_mode_combo.addItem("MP")
            self.connect_mode_combo.setFixedWidth(widget_min_width)  # Fixed width to prevent expansion
            self.connect_mode_combo.setFixedHeight(widget_height)
            self.connect_mode_combo.setContentsMargins(0, 0, 0, 0)  # Remove internal margins

            # Connect dropdown change signals for auto-activation
            self.cut_mode_combo.currentIndexChanged.connect(self.on_cut_mode_changed)
            self.connect_mode_combo.currentIndexChanged.connect(self.on_connect_mode_changed)

            # Probe button with identical styling
            self.btn_probe = pya.QPushButton("Probe")
            self.btn_probe.setFixedWidth(widget_min_width)  # Fixed width for consistency
            self.btn_probe.setFixedHeight(widget_height)
            self.btn_probe.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
            
            # Apply consistent styling to ensure perfect alignment
            button_style = """
                QPushButton {
                    margin: 0px;
                    padding: 0px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    text-align: center;
                }
            """
            
            combo_style = """
                QComboBox {
                    margin: 0px;
                    padding: 0px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
            """
            
            # Apply styles to ensure identical rendering
            self.btn_cut.setStyleSheet(button_style)
            self.btn_connect.setStyleSheet(button_style)
            self.btn_probe.setStyleSheet(button_style)
            self.cut_mode_combo.setStyleSheet(combo_style)
            self.connect_mode_combo.setStyleSheet(combo_style)
            
            # Connect signals
            self.btn_cut.clicked.connect(self.on_cut_clicked)
            self.btn_connect.clicked.connect(self.on_connect_clicked)
            self.btn_probe.clicked.connect(self.on_probe_clicked)
            
            # Add widgets to grid with explicit alignment flags
            grid_layout.addWidget(self.btn_cut, 0, 0, pya.Qt.AlignTop | pya.Qt.AlignLeft)
            grid_layout.addWidget(self.cut_mode_combo, 0, 1, pya.Qt.AlignTop | pya.Qt.AlignLeft)
            grid_layout.addWidget(self.btn_connect, 1, 0, pya.Qt.AlignTop | pya.Qt.AlignLeft)
            grid_layout.addWidget(self.connect_mode_combo, 1, 1, pya.Qt.AlignTop | pya.Qt.AlignLeft)
            grid_layout.addWidget(self.btn_probe, 2, 0, pya.Qt.AlignTop | pya.Qt.AlignLeft)
            
            # Set uniform row heights to ensure consistent spacing
            grid_layout.setRowMinimumHeight(0, widget_height)
            grid_layout.setRowMinimumHeight(1, widget_height)
            grid_layout.setRowMinimumHeight(2, widget_height)
            
            # Set column stretch factors so both columns expand equally
            grid_layout.setColumnStretch(0, 1)  # Column 0 (buttons) can stretch
            grid_layout.setColumnStretch(1, 1)  # Column 1 (combos) can stretch
            
            # Remove any default spacing that might cause misalignment
            grid_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add the grid layout to the group
            group_layout.addLayout(grid_layout)
            
            # Status label with word wrap to prevent panel expansion
            self.status_label = pya.QLabel("Ready")
            self.status_label.setWordWrap(True)  # Enable word wrap
            self.status_label.setMaximumWidth(160)  # Limit width to prevent panel expansion
            self.status_label.setAlignment(pya.Qt.AlignLeft | pya.Qt.AlignTop)  # Align text
            group_layout.addWidget(self.status_label)
            
            self.main_layout.addWidget(group)
            
            # Track active mode
            self.mode_buttons = {
                'cut': self.btn_cut,
                'connect': self.btn_connect,
                'probe': self.btn_probe
            }
            
        except Exception as e:
            print(f"[FIB Panel] Error creating marker section: {e}")
    
    def create_coordinate_jump_section(self):
        """Create coordinate jump section"""
        try:
            group = pya.QGroupBox("Coordinate")
            group_layout = pya.QVBoxLayout(group)
            group_layout.setSpacing(1)
            group_layout.setContentsMargins(2, 1, 2, 1)
            
            # Coordinate input layout
            coord_layout = pya.QHBoxLayout()
            coord_layout.setSpacing(2)
            
            # Input field for coordinates
            self.coord_input = pya.QLineEdit()
            self.coord_input.setPlaceholderText("e.g. 100,100")
            self.coord_input.setFixedHeight(24)
            # Connect Enter key to jump function
            self.coord_input.returnPressed.connect(self.on_coordinate_jump)
            
            # Jump button
            btn_jump = pya.QPushButton("Go")
            btn_jump.setFixedHeight(24)
            btn_jump.setFixedWidth(40)
            btn_jump.clicked.connect(self.on_coordinate_jump)
            
            coord_layout.addWidget(self.coord_input)
            coord_layout.addWidget(btn_jump)
            
            group_layout.addLayout(coord_layout)
            self.main_layout.addWidget(group)
            
        except Exception as e:
            print(f"[FIB Panel] Error creating coordinate jump section: {e}")
    
    def create_marker_list_section(self):
        """Create marker list section"""
        try:
            group = pya.QGroupBox("Markers")
            group_layout = pya.QVBoxLayout(group)
            group_layout.setSpacing(1)
            group_layout.setContentsMargins(2, 1, 2, 1)
            
            # Simple list widget that can expand with window
            self.marker_list = pya.QListWidget()
            
            # Enable multi-selection with Ctrl/Cmd and Shift keys
            self.marker_list.setSelectionMode(pya.QAbstractItemView.ExtendedSelection)
            
            self.marker_list.setContextMenuPolicy(pya.Qt.CustomContextMenu)
            self.marker_list.customContextMenuRequested.connect(self.on_marker_context_menu)
            self.marker_list.itemDoubleClicked.connect(self.on_marker_double_clicked)
            # Remove maximum height constraint to allow expansion

            # Try to enable drag-drop reordering (may not work in all KLayout versions)
            try:
                self.marker_list.setDragEnabled(True)
                self.marker_list.setAcceptDrops(True)
                self.marker_list.setDropIndicatorShown(True)
                self.marker_list.setDragDropMode(pya.QAbstractItemView.InternalMove)
                self.marker_list.setDefaultDropAction(pya.Qt.MoveAction)
                print("[FIB Panel] Drag-drop enabled (may not work in all KLayout versions)")
            except Exception as drag_error:
                print(f"[FIB Panel] Drag-drop not available: {drag_error}")

            # Connect reorder signal (with fallback for different Qt versions)
            try:
                # Try to get model - it might be a method or a property
                list_model = None
                if callable(self.marker_list.model):
                    list_model = self.marker_list.model()
                else:
                    list_model = self.marker_list.model
                
                # Try to connect rowsMoved signal
                if list_model and hasattr(list_model, 'rowsMoved'):
                    list_model.rowsMoved.connect(self.on_markers_reordered)
                    print("[FIB Panel] Connected to rowsMoved signal")
                else:
                    raise AttributeError("rowsMoved not available")
                    
            except (AttributeError, TypeError) as e:
                # Fallback: use selection change detection
                print(f"[FIB Panel] rowsMoved signal not available ({e}), using fallback")
                self.marker_list.itemSelectionChanged.connect(self._check_reorder_needed)
            
            # Add list with stretch factor so it expands
            group_layout.addWidget(self.marker_list, 1)  # Stretch factor = 1
            
            # Add move up/down buttons for reordering (more reliable than drag-drop)
            reorder_layout = pya.QHBoxLayout()
            reorder_layout.setSpacing(2)
            reorder_layout.setContentsMargins(0, 2, 0, 2)
            
            btn_move_up = pya.QPushButton("↑ Move Up")
            btn_move_up.setFixedHeight(24)
            btn_move_up.clicked.connect(self.on_move_marker_up)
            
            btn_move_down = pya.QPushButton("↓ Move Down")
            btn_move_down.setFixedHeight(24)
            btn_move_down.clicked.connect(self.on_move_marker_down)
            
            reorder_layout.addWidget(btn_move_up)
            reorder_layout.addWidget(btn_move_down)
            
            group_layout.addLayout(reorder_layout)
            
            # Clear button with compact height - always at bottom
            btn_clear = pya.QPushButton("Clear All")
            btn_clear.setFixedHeight(24)
            btn_clear.clicked.connect(self.on_clear_all)
            group_layout.addWidget(btn_clear, 0)  # Stretch factor = 0, stays at bottom
            
            # Add group with stretch factor so it expands vertically
            self.main_layout.addWidget(group, 1)  # Stretch factor = 1
            
        except Exception as e:
            print(f"[FIB Panel] Error creating marker list section: {e}")
            # Create minimal fallback
            self.marker_list = None
    
    # Event handlers
    def on_new_project(self):
        """Handle New project with save prompt"""
        try:
            # Check if there are existing markers
            if not self.markers_list or len(self.markers_list) == 0:
                # No markers, just clear
                self._clear_project_internal()
                FibDialogManager.info("New project created", "FIB Panel")
                return

            # Show confirmation dialog with save option
            marker_count = len(self.markers_list)

            # Create custom dialog with three buttons (Phase 3: using FibDialogManager)
            result = FibDialogManager.confirm_with_cancel(
                "New Project",
                f"You have {marker_count} marker(s) in the current project.\n\n"
                f"Do you want to save before clearing?"
            )

            if result == FibDialogManager.RESULT_CANCEL:
                print("[FIB Panel] New project cancelled by user")
                return

            if result == FibDialogManager.RESULT_YES:
                # User wants to save first
                print("[FIB Panel] User chose to save before clearing")

                # Trigger save dialog
                try:
                    from .file_dialog_helper import FileDialogHelper
                    filename = FileDialogHelper.get_save_filename(self)

                    if filename:
                        # Save markers
                        success = self.save_markers_to_json(filename)

                        if not success:
                            # Save failed, ask if user wants to continue anyway
                            if not FibDialogManager.confirm("Save Failed", f"Failed to save markers.\n\n"
                                f"Do you still want to clear the project?"):
                                print("[FIB Panel] New project cancelled after save failure")
                                return
                        else:
                            import os
                            basename = os.path.basename(filename)
                            print(f"[FIB Panel] Markers saved to {basename} before clearing")

                            # Show brief success message
                            try:
                                pya.MainWindow.instance().message(f"Saved to {basename}", 2000)
                            except:
                                pass
                    else:
                        # User cancelled save dialog, ask if want to continue
                        if not FibDialogManager.confirm("Save Cancelled", f"Save cancelled.\n\n"
                            f"Do you still want to clear the project without saving?"):
                            print("[FIB Panel] New project cancelled after save cancellation")
                            return

                except Exception as save_error:
                    print(f"[FIB Panel] Error during save: {save_error}")

                    # Ask if user wants to continue despite error
                    if not FibDialogManager.confirm("Save Error", f"Error during save: {save_error}\n\n"
                        f"Do you still want to clear the project?"):
                        print("[FIB Panel] New project cancelled after save error")
                        return

            # Clear project (both "No" and "Yes after save" paths reach here)
            self._clear_project_internal()

            FibDialogManager.info("New project created", "FIB Panel")
            print(f"[FIB Panel] New project created, cleared {marker_count} markers")

        except Exception as e:
            print(f"[FIB Panel] Error in on_new_project: {e}")
            import traceback
            traceback.print_exc()
            FibDialogManager.warning(f"Error creating new project: {e}", "FIB Panel")

    def _clear_project_internal(self):
        """Internal method to clear all project data (called after confirmation)"""
        try:
            # Clear markers from GDS layout
            self.clear_markers_from_gds()

            # Clear coordinate texts
            self.clear_coordinate_texts()

            # Reset marker counters
            self.reset_marker_counters()

            # Clear panel data
            self.markers_list.clear()
            self._safe_call(self.marker_list, 'clear')

            # Clear notes dictionary
            if hasattr(self, 'marker_notes_dict'):
                self.marker_notes_dict.clear()

            # Reset smart counters
            if hasattr(self, 'smart_counter'):
                self.smart_counter.reset_counters()

            # Deactivate any active mode
            self.active_mode = None
            if hasattr(self, 'mode_buttons'):
                for btn in self.mode_buttons.values():
                    btn.setStyleSheet("")
            self.status_label.setText("Ready")

            print("[FIB Panel] Project cleared successfully")

        except Exception as e:
            print(f"[FIB Panel] Error in _clear_project_internal: {e}")
            import traceback
            traceback.print_exc()
    
    def on_close_project(self):
        """Handle Close project"""
        if FibDialogManager.confirm("FIB Panel", "Close current project?"):
            self.on_new_project()
    
    def on_save_project(self):
        """Handle Save project"""
        try:
            # Use better file dialog
            filename = FileDialogHelper.get_save_filename(self)
            
            if filename:
                success = self.save_markers_to_json(filename)
                if success:
                    basename = os.path.basename(filename)
                    FibDialogManager.info(f"Project saved as {basename} with {len(self.markers_list)} markers", "FIB Panel")
                else:
                    FibDialogManager.warning("Failed to save project", "FIB Panel")
            else:
                # User cancelled or error, try auto-save as fallback
                try:
                    from simple_save_load import simple_save_project
                    saved_filename = simple_save_project(self)
                    if saved_filename:
                        basename = os.path.basename(saved_filename)
                        FibDialogManager.info(f"Project auto-saved as {basename} with {len(self.markers_list)} markers", "FIB Panel")
                except Exception as fallback_error:
                    print(f"[FIB Panel] Fallback save error: {fallback_error}")
                    FibDialogManager.warning("Save failed. Check console for details.", "FIB Panel")
                    
        except Exception as e:
            print(f"[FIB Panel] Error in save project: {e}")
            FibDialogManager.warning(f"Error saving project: {e}", "FIB Panel")
    
    def on_load_project(self):
        """Handle Load project"""
        try:
            # Use better file dialog
            filename = FileDialogHelper.get_load_filename(self)
            
            if filename:
                success = self.load_markers_from_json(filename)
                if success:
                    basename = os.path.basename(filename)
                    FibDialogManager.info(f"Project '{basename}' loaded successfully with {len(self.markers_list)} markers", "FIB Panel")
                else:
                    FibDialogManager.warning("Failed to load project", "FIB Panel")
            else:
                print("[FIB Panel] Load cancelled by user")
                
        except Exception as e:
            print(f"[FIB Panel] Error in load project: {e}")
            FibDialogManager.warning(f"Error loading project: {e}", "FIB Panel")

    def get_gds_filename(self, view):
        """Get GDS filename from current cellview (basename without extension)"""
        import os

        cellview = view.active_cellview()
        if not cellview.is_valid():
            return "unknown"

        # Try to get filename from cellview
        try:
            # Try cellview.filename() method
            if hasattr(cellview, 'filename') and callable(cellview.filename):
                gds_path = cellview.filename()
            else:
                gds_path = None
        except:
            gds_path = None

        # If no filename, try to get from layout handle
        if not gds_path:
            try:
                layout_handle = view.cellview(view.active_cellview_index())
                if hasattr(layout_handle, 'filename') and callable(layout_handle.filename):
                    gds_path = layout_handle.filename()
                else:
                    gds_path = None
            except:
                gds_path = None

        # If still no filename, try cell name
        if not gds_path:
            try:
                cell_name = cellview.cell.name
                if cell_name:
                    return cell_name
            except:
                pass
            return "unknown"

        # Extract basename without extension
        basename = os.path.basename(gds_path)
        name_without_ext = os.path.splitext(basename)[0]
        return name_without_ext

    def get_next_export_number(self, parent_dir, gds_basename):
        """Scan directory for existing numbered exports and return next available number"""
        import os
        import re

        # Pattern: {gds_basename}_#数字_日期
        # Example: chip_v2_#1_20251218, chip_v2_#2_20251218
        pattern = re.compile(rf"^{re.escape(gds_basename)}_#(\d+)_\d{{8}}$")

        max_number = 0

        if os.path.exists(parent_dir):
            for item in os.listdir(parent_dir):
                full_path = os.path.join(parent_dir, item)
                if os.path.isdir(full_path):
                    match = pattern.match(item)
                    if match:
                        number = int(match.group(1))
                        max_number = max(max_number, number)

        return max_number + 1

    def generate_export_dirname(self, gds_basename, number):
        """Generate export directory name: {gds_basename}_#{number}_{YYYYMMDD}"""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{gds_basename}_#{number}_{date_str}"

    def on_export_html(self):
        """Handle Export HTML Only - with directory selection"""
        try:
            if not self.markers_list:
                FibDialogManager.warning("No markers to export. Create some markers first.", "FIB Panel")
                return

            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()

            if not current_view:
                FibDialogManager.warning("No active view", "FIB Panel")
                return

            # Get GDS filename
            gds_basename = self.get_gds_filename(current_view)

            # Select parent directory
            home_dir = os.path.expanduser("~")
            file_dialog = pya.QFileDialog()
            parent_dir = file_dialog.getExistingDirectory(
                self, "Select Export Directory for HTML", home_dir
            )

            # Handle different return types
            if isinstance(parent_dir, tuple):
                parent_dir = parent_dir[0] if parent_dir[0] else None

            if not parent_dir:
                print("[FIB Panel] Export HTML cancelled by user")
                return

            # Auto-increment number
            next_number = self.get_next_export_number(parent_dir, gds_basename)

            # Generate directory name
            export_dirname = self.generate_export_dirname(gds_basename, next_number)
            export_dir = os.path.join(parent_dir, export_dirname)

            # Create directory
            try:
                os.makedirs(export_dir, exist_ok=False)
                print(f"[FIB Panel] Created export directory: {export_dir}")
            except FileExistsError:
                # Rare case: directory just created, increment and retry
                next_number += 1
                export_dirname = self.generate_export_dirname(gds_basename, next_number)
                export_dir = os.path.join(parent_dir, export_dirname)
                try:
                    os.makedirs(export_dir, exist_ok=True)
                    print(f"[FIB Panel] Created export directory (retry): {export_dir}")
                except Exception as e:
                    FibDialogManager.warning(f"Failed to create directory:\n{export_dir}\n\nError: {str(e)}", "FIB Panel")
                    return
            except Exception as e:
                FibDialogManager.warning(f"Failed to create directory:\n{export_dir}\n\nError: {str(e)}", "FIB Panel")
                return

            # Export HTML with screenshots
            success = self.export_markers(export_dir, current_view)

            if success:
                FibDialogManager.info(f"HTML report exported successfully to:\n{export_dir}\n\n{len(self.markers_list)} markers included", "FIB Panel")
            else:
                FibDialogManager.warning("Failed to export HTML. Check console for details.", "FIB Panel")

        except Exception as e:
            print(f"[FIB Panel] Error in export HTML: {e}")
            import traceback
            traceback.print_exc()
            FibDialogManager.warning(f"Error exporting HTML: {e}", "FIB Panel")

    def export_markers(self, output_dir, view):
        """Export markers to HTML report with screenshots

        Args:
            output_dir: Directory to save all output files (HTML, screenshots)
            view: Current KLayout view

        Returns:
            bool: True if successful, False otherwise
        """
        print("=" * 80)
        print("[FIB Panel] export_markers() CALLED")
        print("=" * 80)
        print(f"[FIB Panel] Output directory: {output_dir}")
        print(f"[FIB Panel] Number of markers: {len(self.markers_list)}")
        print(f"[FIB Panel] View: {view}")

        try:
            print("[FIB Panel] Importing screenshot_export module...")
            import os
            from .screenshot_export import (
                export_markers_with_screenshots,
                generate_html_report_with_screenshots
            )
            print("[FIB Panel] Import successful")

            print(f"[FIB Panel] Starting HTML export with screenshots...")

            # Generate screenshots for all markers
            print(f"[FIB Panel] Calling export_markers_with_screenshots with {len(self.markers_list)} markers...")
            try:
                screenshots_dict = export_markers_with_screenshots(
                    self.markers_list,
                    view,
                    output_dir
                )
                print(f"[FIB Panel] Screenshots generated: {len(screenshots_dict)} markers")
            except Exception as screenshot_error:
                print(f"[FIB Panel] ERROR in export_markers_with_screenshots: {screenshot_error}")
                import traceback
                traceback.print_exc()
                return False

            # Define output filename
            html_filename = os.path.join(output_dir, "fib_markers_report.html")

            # Generate HTML report with screenshots
            print(f"[FIB Panel] Calling generate_html_report_with_screenshots...")
            try:
                success = generate_html_report_with_screenshots(
                    self.markers_list,
                    screenshots_dict,
                    html_filename
                )

                if not success:
                    print(f"[FIB Panel] Failed to generate HTML report (returned False)")
                    return False

                print(f"[FIB Panel] HTML report saved to: {html_filename}")
                return True

            except Exception as html_error:
                print(f"[FIB Panel] ERROR in generate_html_report_with_screenshots: {html_error}")
                import traceback
                traceback.print_exc()
                return False

        except Exception as e:
            print(f"[FIB Panel] Error in export_markers: {e}")
            import traceback
            traceback.print_exc()
            return False

    
    def on_cut_clicked(self):
        """Handle Cut button - activate toolbar plugin"""
        try:
            # Get selected mode from dropdown
            current_text = self.cut_mode_combo.currentText
            if callable(current_text):
                is_multipoint = current_text() == "MP"
            else:
                is_multipoint = current_text == "MP"
            mode = 'cut_multi' if is_multipoint else 'cut'
            
            self.activate_toolbar_plugin(mode)
            self.activate_mode(mode)
        except Exception as e:
            print(f"[FIB Panel] Error in on_cut_clicked: {e}")
            # Fallback to regular cut mode
            self.activate_toolbar_plugin('cut')
            self.activate_mode('cut')
    
    def on_connect_clicked(self):
        """Handle Connect button - activate toolbar plugin"""
        try:
            # Get selected mode from dropdown
            current_text = self.connect_mode_combo.currentText
            if callable(current_text):
                is_multipoint = current_text() == "MP"
            else:
                is_multipoint = current_text == "MP"
            mode = 'connect_multi' if is_multipoint else 'connect'
            
            self.activate_toolbar_plugin(mode)
            self.activate_mode(mode)
        except Exception as e:
            print(f"[FIB Panel] Error in on_connect_clicked: {e}")
            # Fallback to regular connect mode
            self.activate_toolbar_plugin('connect')
            self.activate_mode('connect')
    
    def on_probe_clicked(self):
        """Handle Probe button - activate toolbar plugin"""
        self.activate_toolbar_plugin('probe')
        self.activate_mode('probe')

    def on_cut_mode_changed(self, index):
        """Handle Cut mode dropdown change - auto-switch to Cut mode"""
        try:
            print(f"[FIB Panel] Cut dropdown changed to index {index}")

            # Determine new mode
            current_text = self.cut_mode_combo.currentText
            if callable(current_text):
                is_multipoint = current_text() == "MP"
            else:
                is_multipoint = current_text == "MP"

            new_mode = 'cut_multi' if is_multipoint else 'cut'

            # Clear pending points from all modes
            self.clear_pending_points()

            # Always activate the new Cut mode (auto-switch)
            self.activate_toolbar_plugin(new_mode)
            self.activate_mode(new_mode)

            print(f"[FIB Panel] Auto-switched to {new_mode}")

        except Exception as e:
            print(f"[FIB Panel] Error in on_cut_mode_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_connect_mode_changed(self, index):
        """Handle Connect mode dropdown change - auto-switch to Connect mode"""
        try:
            print(f"[FIB Panel] Connect dropdown changed to index {index}")

            # Determine new mode
            current_text = self.connect_mode_combo.currentText
            if callable(current_text):
                is_multipoint = current_text() == "MP"
            else:
                is_multipoint = current_text == "MP"

            new_mode = 'connect_multi' if is_multipoint else 'connect'

            # Clear pending points from all modes
            self.clear_pending_points()

            # Always activate the new Connect mode (auto-switch)
            self.activate_toolbar_plugin(new_mode)
            self.activate_mode(new_mode)

            print(f"[FIB Panel] Auto-switched to {new_mode}")

        except Exception as e:
            print(f"[FIB Panel] Error in on_connect_mode_changed: {e}")
            import traceback
            traceback.print_exc()

    def activate_toolbar_plugin(self, mode):
        """Activate the corresponding plugin mode"""
        print("=" * 80)
        print(f"[FIB Panel] DEBUG: activate_toolbar_plugin called with mode='{mode}'")
        print("=" * 80)
        
        try:
            # PRIORITY 1: Import directly from fib_plugin module (most reliable for SALT packages)
            print(f"[FIB Panel] Step 1: Attempting to import fib_plugin module...")
            try:
                from . import fib_plugin
                print(f"[FIB Panel] [OK] fib_plugin module imported successfully")
                print(f"[FIB Panel] fib_plugin module location: {fib_plugin.__file__ if hasattr(fib_plugin, '__file__') else 'unknown'}")
                
                # Check if activate_fib_mode exists
                has_function = hasattr(fib_plugin, 'activate_fib_mode')
                print(f"[FIB Panel] Has activate_fib_mode: {has_function}")
                
                if has_function:
                    print(f"[FIB Panel] Step 2: Calling fib_plugin.activate_fib_mode('{mode}')...")
                    
                    # Get the function
                    activate_func = getattr(fib_plugin, 'activate_fib_mode')
                    print(f"[FIB Panel] Function object: {activate_func}")
                    print(f"[FIB Panel] Function type: {type(activate_func)}")
                    
                    # Call it
                    result = activate_func(mode)
                    
                    print(f"[FIB Panel] Step 3: Function returned: {result} (type: {type(result)})")
                    
                    if result:
                        print(f"[FIB Panel] [OK] SUCCESS: {mode} mode activated")
                        print("=" * 80)
                        return True
                    else:
                        print(f"[FIB Panel] [X] FAILED: activate_fib_mode returned False")
                else:
                    print(f"[FIB Panel] [X] FAILED: fib_plugin has no activate_fib_mode attribute")
                    print(f"[FIB Panel] Available attributes in fib_plugin:")
                    attrs = [attr for attr in dir(fib_plugin) if not attr.startswith('_')]
                    for i, attr in enumerate(attrs[:20]):  # Show first 20
                        print(f"[FIB Panel]   {i+1}. {attr}")
                    if len(attrs) > 20:
                        print(f"[FIB Panel]   ... and {len(attrs)-20} more")
                
            except ImportError as import_error:
                print(f"[FIB Panel] [X] ImportError: {import_error}")
                import traceback
                traceback.print_exc()
            except Exception as direct_error:
                print(f"[FIB Panel] [X] Exception during import/call: {direct_error}")
                import traceback
                traceback.print_exc()
            
            # PRIORITY 2: Try __main__ namespace (fallback for exec() loading)
            print(f"[FIB Panel] Step 4: Checking __main__ namespace...")
            if 'activate_fib_mode' in sys.modules['__main__'].__dict__:
                print(f"[FIB Panel] [OK] Found activate_fib_mode in __main__")
                activate_fib_mode = sys.modules['__main__'].__dict__['activate_fib_mode']
                print(f"[FIB Panel] Calling __main__.activate_fib_mode('{mode}')...")
                result = activate_fib_mode(mode)
                print(f"[FIB Panel] __main__ result: {result}")
                if result:
                    print(f"[FIB Panel] [OK] SUCCESS via __main__")
                    print("=" * 80)
                    return True
            else:
                print(f"[FIB Panel] [X] activate_fib_mode not found in __main__")
            
            # If everything failed, show error
            print(f"[FIB Panel] [X] ALL METHODS FAILED")
            print("=" * 80)
            
            FibDialogManager.warning(f"无法激活 {mode.upper()} 模式。\n\n"
                f"Failed to activate {mode.upper()} mode.\n\n"
                f"请尝试：\n"
                f"1. 使用工具栏上的 FIB 按钮\n"
                f"2. 重新加载 FIB Tool\n"
                f"3. 查看 Macro Development 控制台的错误信息\n\n"
                f"Please try:\n"
                f"1. Use the FIB buttons in the toolbar\n"
                f"2. Reload FIB Tool\n"
                f"3. Check Macro Development console for errors", "FIB Panel")
            return False
                
        except Exception as e:
            print(f"[FIB Panel] [X] FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 80)
            
            FibDialogManager.warning(f"激活模式时出错 / Error activating mode:\n\n{str(e)}", "FIB Panel Error")
            return False
    
    def activate_mode(self, mode):
        """Activate a marker creation mode"""
        # Reset all button styles
        for btn in self.mode_buttons.values():
            btn.setStyleSheet("")
        
        if self.active_mode == mode:
            # Deactivate current mode
            self.active_mode = None
            self.status_label.setText("Ready")
            # Clear any pending points when deactivating
            self.clear_pending_points()
        else:
            # Activate new mode
            self.active_mode = mode
            
            # Highlight the appropriate button
            base_mode = mode.replace('_multi', '')
            if base_mode in self.mode_buttons:
                self.mode_buttons[base_mode].setStyleSheet("background-color: lightgreen;")
            
            # Set appropriate status message (keep it short to prevent panel expansion)
            # Shorten display names for compact layout
            display_name = 'CON' if base_mode == 'connect' else base_mode.upper()
            if mode.endswith('_multi'):
                self.status_label.setText(f"{display_name}: L-add, R-end")
            else:
                self.status_label.setText(f"{display_name}: Click")
            
            # Clear any pending points when switching modes
            self.clear_pending_points()
        
        print(f"[FIB Panel] Mode: {self.active_mode}")
    
    def clear_pending_points(self):
        """Clear pending points from all plugin instances"""
        try:
            # Access global plugin instances and clear their temp_points
            if 'current_plugins' in sys.modules['__main__'].__dict__:
                current_plugins = sys.modules['__main__'].__dict__['current_plugins']
                for plugin_mode, plugin in current_plugins.items():
                    if plugin and hasattr(plugin, 'temp_points'):
                        plugin.temp_points = []
                        plugin.last_click_time = 0
                        plugin.last_click_pos = None
                        print(f"[FIB Panel] Cleared temp_points and double-click state for {plugin_mode} plugin")
        except Exception as e:
            print(f"[FIB Panel] Error clearing pending points: {e}")
    
    def on_marker_context_menu(self, position):
        """Handle right-click on marker list"""
        self.context_menu.show_context_menu(position)
    
    def on_marker_double_clicked(self, item):
        """Handle double-click on marker"""
        self.context_menu.handle_double_click(item)
    

    def on_coordinate_jump(self):
        """Jump to specified coordinates in the layout"""
        try:
            # Get text from input - handle both property and method access
            try:
                coord_text = self.coord_input.text
                if callable(coord_text):
                    coord_text = coord_text()
            except:
                coord_text = str(self.coord_input.text)
            
            coord_text = coord_text.strip()
            
            if not coord_text:
                FibDialogManager.warning("Please enter coordinates", "Coordinate Jump")
                return
            
            # Parse coordinates - support multiple formats
            # Formats: "100 100", "100,100", "(100,100)", "(100 100)", "100, 100"
            import re
            
            # Remove quotes if present
            coord_text = coord_text.strip('"\'')
            
            # Remove parentheses if present
            coord_text = coord_text.strip('()')
            
            # Try to extract two numbers
            # Match patterns like: "100 100", "100,100", "100, 100"
            pattern = r'([0-9.-]+)\s*[,\s]\s*([0-9.-]+)'
            match = re.match(pattern, coord_text)
            
            if not match:
                FibDialogManager.warning(f"Invalid coordinate format: '{coord_text}'\n\nSupported formats:\n- 100 100\n- 100,100\n- (100,100)\n- (100 100)\n- \"100,100\"", "Coordinate Jump")
                return
            
            # Extract coordinates
            try:
                x = float(match.group(1))
                y = float(match.group(2))
            except ValueError:
                FibDialogManager.warning("Invalid number format", "Coordinate Jump")
                return
            
            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view:
                FibDialogManager.warning("No active layout view", "Coordinate Jump")
                return
            
            # Zoom to coordinate with some padding
            padding = GEOMETRIC_PARAMS['coordinate_jump_padding']
            zoom_box = pya.DBox(x - padding, y - padding, x + padding, y + padding)
            
            current_view.zoom_box(zoom_box)
            
            print(f"[FIB Panel] Jumped to coordinates: ({x:.3f}, {y:.3f})")
            
            # Show brief message
            try:
                pya.MainWindow.instance().message(f"Jumped to ({x:.3f}, {y:.3f})", UI_TIMEOUTS['message_short'])
            except:
                pass
                
        except Exception as e:
            print(f"[FIB Panel] Error in coordinate jump: {e}")
            import traceback
            traceback.print_exc()
            FibDialogManager.warning(f"Error: {e}", "Coordinate Jump")
    
    def on_clear_all(self):
        """Clear all markers"""
        if self.markers_list:
            if FibDialogManager.confirm("Clear All", f"Delete all {len(self.markers_list)} markers from layout and reset counters?"):
                # Clear markers from GDS layout
                self.clear_markers_from_gds()
                
                # Clear coordinate texts
                self.clear_coordinate_texts()
                
                # Reset marker counters
                self.reset_marker_counters()
                
                # Clear panel data
                self.markers_list.clear()
                self._safe_call(self.marker_list, 'clear')
                
                # Reset smart counters
                if hasattr(self, 'smart_counter'):
                    self.smart_counter.reset_counters()
                
                print("[FIB Panel] Cleared all markers from layout and reset counters")
    
    def clear_markers_from_gds(self):
        """Clear all FIB markers from the GDS layout"""
        try:
            # Get current view and cell
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view or not current_view.active_cellview().is_valid():
                print("[FIB Panel] No active layout found")
                return
            
            cellview = current_view.active_cellview()
            cell = cellview.cell
            layout = cellview.layout()
            
            # Import config to get layer numbers
            from .config import LAYERS
            
            # Clear all FIB layers
            for layer_name, layer_num in LAYERS.items():
                try:
                    fib_layer = layout.layer(layer_num, 0)
                    cell.shapes(fib_layer).clear()
                    print(f"[FIB Panel] Cleared layer {layer_num} ({layer_name})")
                except Exception as layer_error:
                    print(f"[FIB Panel] Error clearing layer {layer_num}: {layer_error}")
            
            print("[FIB Panel] All FIB markers cleared from GDS")
            
        except Exception as e:
            print(f"[FIB Panel] Error clearing markers from GDS: {e}")
    
    def clear_coordinate_texts(self):
        """Clear all coordinate text labels"""
        try:
            # Use the global function if available
            if 'clear_coordinate_texts' in sys.modules['__main__'].__dict__:
                clear_func = sys.modules['__main__'].__dict__['clear_coordinate_texts']
                clear_func()
                print("[FIB Panel] Coordinate texts cleared via global function")
            else:
                # Fallback: clear coordinate layer directly
                main_window = pya.Application.instance().main_window()
                current_view = main_window.current_view()
                
                if current_view and current_view.active_cellview().is_valid():
                    cellview = current_view.active_cellview()
                    cell = cellview.cell
                    layout = cellview.layout()
                    
                    from .config import LAYERS
                    coord_layer = layout.layer(LAYERS['coordinates'], 0)
                    cell.shapes(coord_layer).clear()
                    print("[FIB Panel] Coordinate texts cleared directly")
                    
        except Exception as e:
            print(f"[FIB Panel] Error clearing coordinate texts: {e}")
    
    def _ask_to_open_html(self, html_filename):
        """Ask user if they want to open the HTML file in browser"""
        try:
            if FibDialogManager.confirm("HTML Report Generated", f"HTML report saved successfully!\n\n{html_filename}\n\nWould you like to open it in your browser?"):
                self._open_html_in_browser(html_filename)
                
        except Exception as e:
            print(f"[FIB Panel] Error asking to open HTML: {e}")
    
    def _open_file_explorer(self, directory):
        """Open file explorer/finder at the specified directory"""
        try:
            import subprocess
            import platform
            import os
            
            if not os.path.exists(directory):
                print(f"[FIB Panel] Directory does not exist: {directory}")
                return
            
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: Open Explorer
                subprocess.Popen(['explorer', directory])
                print(f"[FIB Panel] Opened Explorer at: {directory}")
                
            elif system == "darwin":  # macOS
                # macOS: Open Finder
                subprocess.Popen(['open', directory])
                print(f"[FIB Panel] Opened Finder at: {directory}")
                
            else:  # Linux
                # Linux: Try common file managers
                file_managers = ['xdg-open', 'nautilus', 'dolphin', 'thunar', 'nemo']
                for fm in file_managers:
                    try:
                        subprocess.Popen([fm, directory])
                        print(f"[FIB Panel] Opened {fm} at: {directory}")
                        return
                    except FileNotFoundError:
                        continue
                
                print(f"[FIB Panel] No file manager found for Linux")
                
        except Exception as e:
            print(f"[FIB Panel] Error opening file explorer: {e}")
    
    def _open_html_in_browser(self, html_filename):
        """Open HTML file in browser with priority: Edge > Chrome > IE"""
        try:
            import subprocess
            import os
            import platform
            
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: Try Edge > Chrome > IE
                browsers = [
                    # Microsoft Edge
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    # Google Chrome
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    # Internet Explorer
                    r"C:\Program Files\Internet Explorer\iexplore.exe",
                    r"C:\Program Files (x86)\Internet Explorer\iexplore.exe"
                ]
                
                for browser_path in browsers:
                    if os.path.exists(browser_path):
                        print(f"[FIB Panel] Opening HTML with: {os.path.basename(browser_path)}")
                        subprocess.Popen([browser_path, html_filename])
                        return
                
                # Fallback: Use default browser
                print("[FIB Panel] Using default browser")
                os.startfile(html_filename)
                
            elif system == "darwin":  # macOS
                # macOS: Try Edge > Chrome > Safari
                browsers = [
                    "Microsoft Edge",
                    "Google Chrome", 
                    "Safari"
                ]
                
                for browser in browsers:
                    try:
                        subprocess.run(["open", "-a", browser, html_filename], check=True)
                        print(f"[FIB Panel] Opened HTML with: {browser}")
                        return
                    except subprocess.CalledProcessError:
                        continue
                
                # Fallback: Use default browser
                print("[FIB Panel] Using default browser")
                subprocess.run(["open", html_filename])
                
            else:  # Linux
                # Linux: Try Edge > Chrome > Firefox
                browsers = [
                    "microsoft-edge",
                    "google-chrome",
                    "chromium-browser",
                    "firefox"
                ]
                
                for browser in browsers:
                    try:
                        subprocess.Popen([browser, html_filename])
                        print(f"[FIB Panel] Opened HTML with: {browser}")
                        return
                    except FileNotFoundError:
                        continue
                
                # Fallback: Use xdg-open
                print("[FIB Panel] Using default browser")
                subprocess.Popen(["xdg-open", html_filename])
                
        except Exception as e:
            print(f"[FIB Panel] Error opening HTML in browser: {e}")
            # Final fallback: Show message with file path
            FibDialogManager.info(f"Could not open browser automatically.\n\nPlease open this file manually:\n{html_filename}", "FIB Panel")
    
    def _recreate_coordinate_texts(self, marker, cell, layout):
        """Recreate coordinate text labels for a loaded marker"""
        try:
            dbu = layout.dbu
            coord_layer_num = LAYERS['coordinates']
            coord_layer = layout.layer(coord_layer_num, 0)
            
            # Get coordinates based on marker type
            coordinates = []
            
            if hasattr(marker, 'points'):
                # Multi-point marker
                coordinates = marker.points
            elif hasattr(marker, 'x1'):
                # Two-point marker (cut, connect)
                coordinates = [(marker.x1, marker.y1), (marker.x2, marker.y2)]
            elif hasattr(marker, 'x'):
                # Single-point marker (probe)
                coordinates = [(marker.x, marker.y)]
            
            # Create coordinate texts
            for x, y in coordinates:
                coord_text = f"{marker.id}:({x:.3f},{y:.3f})"
                text_x = int(x / dbu)
                text_y = int(y / dbu)
                
                text_obj = pya.Text(coord_text, pya.Trans(pya.Point(text_x, text_y)))
                cell.shapes(coord_layer).insert(text_obj)
            
            print(f"[FIB Panel] Recreated {len(coordinates)} coordinate texts for {marker.id}")
            
        except Exception as e:
            print(f"[FIB Panel] Error recreating coordinate texts: {e}")
    
    def reset_marker_counters(self):
        """Reset marker counters to start from 0"""
        try:
            # Phase 2 refactoring: Use FibGlobalState instead of sys.modules
            self.state.reset_counters()
            print("[FIB Panel] Marker counters reset via FibGlobalState")
        except Exception as e:
            print(f"[FIB Panel] Error resetting marker counters: {e}")
    
    def save_markers_to_json(self, filename):
        """Save markers to JSON file (Phase 2 refactoring: delegated to FibFileManager)"""
        return self.file_manager.save_markers_to_json(
            self.markers_list,
            filename,
            marker_notes_dict=self.marker_notes_dict,
            marker_counters=self.state.marker_counters
        )
    
    def load_markers_from_json(self, filename):
        """Load markers from JSON file (Phase 2 refactoring: using FibFileManager)"""
        try:
            # Phase 2 refactoring: Use FibFileManager to load data
            markers_data, notes_dict, counters = self.file_manager.load_markers_from_json(filename)

            if markers_data is None:
                return False

            # Clear current markers
            self.on_new_project()

            # Load centralized notes dictionary
            self.marker_notes_dict = notes_dict
            print(f"[FIB Panel] Loaded notes dict: {self.marker_notes_dict}")

            # Load marker counters into FibGlobalState
            self.state.marker_counters.update(counters)
            print(f"[FIB Panel] Loaded marker counters: {self.state.marker_counters}")
            
            # Get current view and cell for drawing
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view or not current_view.active_cellview().is_valid():
                print("[FIB Panel] No active layout found for loading markers")
                return False
            
            cellview = current_view.active_cellview()
            cell = cellview.cell
            layout = cellview.layout()
            
            # Import marker classes and drawing function
            from .markers import CutMarker, ConnectMarker, ProbeMarker
            
            # Try to import multi-point markers
            try:
                from .multipoint_markers import MultiPointCutMarker, MultiPointConnectMarker
                multipoint_available = True
            except ImportError:
                multipoint_available = False
                print("[FIB Panel] Multi-point markers not available for loading")
            
            # Load markers (using data from FibFileManager)
            loaded_count = 0
            for marker_data in markers_data:
                try:
                    marker_type = marker_data['type']
                    marker_id = marker_data['id']
                    
                    # Create marker object
                    if marker_type == 'multipoint_cut' and multipoint_available:
                        points = marker_data.get('points', [])
                        marker = MultiPointCutMarker(marker_id, points, LAYERS['cut'])
                    elif marker_type == 'multipoint_connect' and multipoint_available:
                        points = marker_data.get('points', [])
                        marker = MultiPointConnectMarker(marker_id, points, LAYERS['connect'])
                    elif marker_type == 'cut':
                        marker = CutMarker(marker_id, marker_data['x1'], marker_data['y1'], 
                                         marker_data['x2'], marker_data['y2'], 6)
                    elif marker_type == 'connect':
                        marker = ConnectMarker(marker_id, marker_data['x1'], marker_data['y1'], 
                                             marker_data['x2'], marker_data['y2'], 6)
                    elif marker_type == 'probe':
                        marker = ProbeMarker(marker_id, marker_data['x'], marker_data['y'], 6)
                    else:
                        print(f"[FIB Panel] Unknown marker type: {marker_type}")
                        continue
                    
                    # Set additional properties
                    # Try to get notes from dict first, then from marker_data
                    if marker_id in self.marker_notes_dict:
                        marker.notes = self.marker_notes_dict[marker_id]
                        print(f"[FIB Panel] Restored notes from dict for {marker_id}: '{marker.notes}'")
                    else:
                        loaded_notes = marker_data.get('notes', '')
                        # If no notes in file, set default based on marker type
                        if not loaded_notes:
                            if marker_type == 'cut' or marker_type == 'multipoint_cut':
                                loaded_notes = DEFAULT_MARKER_NOTES['cut']
                            elif marker_type == 'connect' or marker_type == 'multipoint_connect':
                                loaded_notes = DEFAULT_MARKER_NOTES['connect']
                            elif marker_type == 'probe':
                                loaded_notes = DEFAULT_MARKER_NOTES['probe']
                        marker.notes = loaded_notes
                    
                    marker.screenshots = marker_data.get('screenshots', [])
                    marker.target_layers = marker_data.get('target_layers', [])
                    
                    # Restore layer information
                    if marker_type == 'multipoint_cut' or marker_type == 'multipoint_connect':
                        # Multi-point markers
                        marker.point_layers = marker_data.get('point_layers', [])
                        print(f"[FIB Panel] Restored point_layers for {marker_id}: {marker.point_layers}")
                    elif marker_type == 'cut' or marker_type == 'connect':
                        # Two-point markers
                        marker.layer1 = marker_data.get('layer1', None)
                        marker.layer2 = marker_data.get('layer2', None)
                        print(f"[FIB Panel] Restored layer info for {marker_id}: layer1={marker.layer1}, layer2={marker.layer2}")
                    elif marker_type == 'probe':
                        # Probe markers
                        marker.target_layer = marker_data.get('target_layer', None)
                        print(f"[FIB Panel] Restored target_layer for {marker_id}: {marker.target_layer}")
                    
                    # Draw marker to GDS
                    from .config import LAYERS
                    if marker_type.startswith('multipoint_'):
                        base_type = marker_type.replace('multipoint_', '')
                        fib_layer = layout.layer(LAYERS[base_type], 0)
                    else:
                        fib_layer = layout.layer(LAYERS[marker_type], 0)
                    
                    marker.to_gds(cell, fib_layer)
                    
                    # Recreate coordinate texts for this marker
                    self._recreate_coordinate_texts(marker, cell, layout)
                    
                    # Add to panel
                    self.add_marker(marker)
                    loaded_count += 1
                    
                except Exception as marker_error:
                    print(f"[FIB Panel] Error loading marker {marker_data.get('id', 'unknown')}: {marker_error}")
                    continue
            
            print(f"[FIB Panel] Loaded {loaded_count} markers from {filename}")
            return True
            
        except Exception as e:
            print(f"[FIB Panel] Error loading from JSON: {e}")
            return False
    
    
    # Public methods for plugin integration
    def add_marker(self, marker):
        """Add a marker to the panel (called by plugin)"""
        try:
            # Check if panel is still valid
            if not hasattr(self, 'markers_list'):
                print("[FIB Panel] Panel not properly initialized, skipping marker add")
                return
            
            # Always add to markers list
            self.markers_list.append(marker)
            
            # Try to add to UI if available
            if hasattr(self, 'marker_list') and self.marker_list is not None:
                try:
                    # Check if the widget is still valid
                    _ = self.marker_list.count  # This will throw if widget is destroyed
                    
                    # Add to list widget
                    marker_class_name = marker.__class__.__name__
                    
                    # Handle multi-point markers
                    if 'MultiPoint' in marker_class_name:
                        if 'Cut' in marker_class_name:
                            marker_type = "CUT (MULTI)"
                        elif 'Connect' in marker_class_name:
                            marker_type = "CONNECT (MULTI)"
                        else:
                            marker_type = "MULTI"
                        
                        # Show complete point coordinates for multi-point markers with layer info
                        if hasattr(marker, 'points') and len(marker.points) > 0:
                            if len(marker.points) <= 3:
                                # For 3 or fewer points, show all coordinates with layer info in panel
                                point_strs = []
                                for i, p in enumerate(marker.points):
                                    layer_info = ""
                                    if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                                        layer_info = f" [{marker.point_layers[i]}]"
                                    point_strs.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
                                coords = f"{len(marker.points)} pts: " + " → ".join(point_strs)
                            else:
                                # For more than 3 points, show first 2, ..., last 1 with layer info (shorter for panel)
                                first_points = []
                                for i in range(2):
                                    p = marker.points[i]
                                    layer_info = ""
                                    if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                                        layer_info = f" [{marker.point_layers[i]}]"
                                    first_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
                                
                                # Last point
                                last_p = marker.points[-1]
                                last_layer_info = ""
                                if hasattr(marker, 'point_layers') and len(marker.point_layers) > 0 and marker.point_layers[-1]:
                                    last_layer_info = f" [{marker.point_layers[-1]}]"
                                last_point = f"({last_p[0]:.3f},{last_p[1]:.3f}){last_layer_info}"
                                
                                coords = f"{len(marker.points)} pts: " + " → ".join(first_points) + " → ... → " + last_point
                        else:
                            coords = "No points"
                    else:
                        # Regular markers
                        marker_type = marker_class_name.replace('Marker', '').upper()
                        
                        if hasattr(marker, 'x1'):  # CUT or CONNECT
                            # Get layer info for display
                            layer1_str = getattr(marker, 'layer1', None) or 'N/A'
                            layer2_str = getattr(marker, 'layer2', None) or 'N/A'
                            coords = f"({marker.x1:.3f},{marker.y1:.3f}) {layer1_str} to ({marker.x2:.3f},{marker.y2:.3f}) {layer2_str}"
                        else:  # PROBE
                            # Get layer info for display
                            target_layer_str = getattr(marker, 'target_layer', None) or 'N/A'
                            coords = f"({marker.x:.3f},{marker.y:.3f}) {target_layer_str}"
                    
                    item_text = f"{marker.id} - {marker_type} - {coords}"
                    self._safe_call(self.marker_list, 'addItem', item_text)
                    print(f"[FIB Panel] Added marker: {marker.id}")
                    
                except Exception as ui_error:
                    print(f"[FIB Panel] UI error adding marker {marker.id}: {ui_error}")
                    print(f"[FIB Panel] Marker {marker.id} added to data but not UI")
            else:
                print(f"[FIB Panel] marker_list not available, marker {marker.id} added to data only")
                
        except Exception as e:
            print(f"[FIB Panel] Error adding marker {getattr(marker, 'id', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()

    def on_markers_reordered(self, parent, start, end, destination, row):
        """Handle marker list drag-drop reordering"""
        try:
            print(f"[FIB Panel] Markers reordered: {start}-{end} to {row}")

            # Get count - handle both method and property safely
            try:
                # Try as method first
                list_count = self.marker_list.count()
            except TypeError:
                # It's a property, not a method
                list_count = self.marker_list.count

            # Rebuild markers_list from current UI order
            new_markers_list = []
            for i in range(list_count):
                item = self._safe_call(self.marker_list, 'item', i)
                marker_id = self._extract_marker_id_from_item(item)
                marker = self._find_marker_by_id_in_list(marker_id)
                if marker:
                    new_markers_list.append(marker)

            self.markers_list = new_markers_list
            print(f"[FIB Panel] List reordered: {[m.id for m in self.markers_list]}")

            try:
                pya.MainWindow.instance().message("Markers reordered", 2000)
            except:
                pass

        except Exception as e:
            print(f"[FIB Panel] Error in reorder: {e}")

    def _extract_marker_id_from_item(self, item):
        """Extract marker ID from list item text"""
        try:
            # Try to get text from item
            if hasattr(item, 'text'):
                text_attr = item.text
                if callable(text_attr):
                    text = text_attr()
                else:
                    text = text_attr
            else:
                print(f"[FIB Panel] ERROR: item has no 'text' attribute")
                return "Unknown"
            
            # Ensure text is a string
            if callable(text):
                text = text()
            text = str(text)
            
            print(f"[FIB Panel] Extracting ID from text: '{text}'")
            
            # Format: "MARKER_ID - TYPE - (coords)"
            parts = text.split(' - ')
            if parts:
                marker_id = parts[0].strip()
                print(f"[FIB Panel] Extracted marker_id: '{marker_id}'")
                return marker_id
            else:
                print(f"[FIB Panel] ERROR: Could not split text")
                return "Unknown"
                
        except Exception as e:
            print(f"[FIB Panel] ERROR in _extract_marker_id_from_item: {e}")
            import traceback
            traceback.print_exc()
            return "Unknown"

    def _find_marker_by_id_in_list(self, marker_id):
        """Find marker in markers_list by ID"""
        for marker in self.markers_list:
            if marker.id == marker_id:
                return marker
        return None

    def _check_reorder_needed(self):
        """Fallback: detect if markers were reordered"""
        try:
            # Get count - handle both method and property safely
            try:
                list_count = self.marker_list.count()
            except TypeError:
                list_count = self.marker_list.count
            
            ui_order = [self._extract_marker_id_from_item(
                self._safe_call(self.marker_list, 'item', i)
            ) for i in range(list_count)]

            data_order = [m.id for m in self.markers_list]

            if ui_order != data_order:
                self._sync_markers_to_ui_order()
        except Exception as e:
            print(f"[FIB Panel] Reorder detection error: {e}")

    def _rebuild_marker_list_ui(self):
        """Rebuild the UI list from markers_list
        
        This is more reliable than takeItem/insertItem in KLayout's Qt bindings.
        """
        try:
            print(f"[FIB Panel] Rebuilding UI list from {len(self.markers_list)} markers")
            
            # Clear the UI list
            self.marker_list.clear()
            
            # Re-add all markers in the current order
            for marker in self.markers_list:
                marker_class_name = marker.__class__.__name__
                
                # Handle multi-point markers
                if 'MultiPoint' in marker_class_name:
                    if 'Cut' in marker_class_name:
                        marker_type = "CUT (MULTI)"
                    elif 'Connect' in marker_class_name:
                        marker_type = "CONNECT (MULTI)"
                    else:
                        marker_type = "MULTI"
                    
                    # Show point coordinates for multi-point markers
                    if hasattr(marker, 'points') and len(marker.points) > 0:
                        if len(marker.points) <= 3:
                            point_strs = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points]
                            coords = " -> ".join(point_strs)
                        else:
                            first = marker.points[0]
                            last = marker.points[-1]
                            coords = f"({first[0]:.3f},{first[1]:.3f}) -> ... -> ({last[0]:.3f},{last[1]:.3f}) [{len(marker.points)} pts]"
                    else:
                        coords = "(no points)"
                else:
                    # Regular markers
                    marker_type = marker_class_name.replace('Marker', '').upper()
                    
                    if hasattr(marker, 'x1'):  # CUT or CONNECT
                        # Get layer info for display
                        layer1_str = getattr(marker, 'layer1', None) or 'N/A'
                        layer2_str = getattr(marker, 'layer2', None) or 'N/A'
                        coords = f"({marker.x1:.3f},{marker.y1:.3f}) {layer1_str} to ({marker.x2:.3f},{marker.y2:.3f}) {layer2_str}"
                    else:  # PROBE
                        # Get layer info for display
                        target_layer_str = getattr(marker, 'target_layer', None) or 'N/A'
                        coords = f"({marker.x:.3f},{marker.y:.3f}) {target_layer_str}"
                
                item_text = f"{marker.id} - {marker_type} - {coords}"
                self.marker_list.addItem(item_text)
                print(f"[FIB Panel] Added to UI: {item_text}")
            
            print(f"[FIB Panel] UI list rebuilt with {self.marker_list.count()} items")
            
        except Exception as e:
            print(f"[FIB Panel] Error rebuilding UI list: {e}")
            import traceback
            traceback.print_exc()
    
    def _sync_markers_to_ui_order(self):
        """Sync markers_list to match UI order"""
        try:
            # Get count - handle both method and property safely
            try:
                list_count = self.marker_list.count()
            except TypeError:
                list_count = self.marker_list.count
            
            print(f"[FIB Panel] Syncing {list_count} items from UI to markers_list")
            print(f"[FIB Panel] Current markers_list has {len(self.markers_list)} markers")
            
            new_list = []
            for i in range(list_count):
                # Access item directly without _safe_call
                # In KLayout's Qt bindings, item() should be a method
                try:
                    item = self.marker_list.item(i)
                except TypeError as te:
                    # If item is a property, try accessing it differently
                    print(f"[FIB Panel] ERROR: item({i}) not callable: {te}")
                    # Don't continue - this would lose the marker!
                    # Instead, keep the original order for this item
                    if i < len(self.markers_list):
                        new_list.append(self.markers_list[i])
                        print(f"[FIB Panel] Kept original marker at index {i}: {self.markers_list[i].id}")
                    continue
                
                if item is None:
                    print(f"[FIB Panel] ERROR: item at index {i} is None")
                    # Don't continue - this would lose the marker!
                    if i < len(self.markers_list):
                        new_list.append(self.markers_list[i])
                        print(f"[FIB Panel] Kept original marker at index {i}: {self.markers_list[i].id}")
                    continue
                    
                marker_id = self._extract_marker_id_from_item(item)
                print(f"[FIB Panel] Item {i}: extracted marker_id = '{marker_id}'")
                
                marker = self._find_marker_by_id_in_list(marker_id)
                if marker:
                    new_list.append(marker)
                    print(f"[FIB Panel] Item {i}: found and added marker '{marker.id}'")
                else:
                    print(f"[FIB Panel] ERROR: Item {i}: marker '{marker_id}' not found in markers_list!")
                    # This is a serious error - marker ID doesn't match any marker

            print(f"[FIB Panel] Sync complete: {len(new_list)} markers in new_list")
            print(f"[FIB Panel] New order: {[m.id for m in new_list]}")
            
            # Only update if we didn't lose any markers
            if len(new_list) == len(self.markers_list):
                self.markers_list = new_list
                print(f"[FIB Panel] markers_list updated successfully")
            else:
                print(f"[FIB Panel] ERROR: Sync would lose markers! Keeping original order.")
                print(f"[FIB Panel] Original: {len(self.markers_list)}, New: {len(new_list)}")
                
        except Exception as e:
            print(f"[FIB Panel] Sync error: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_call(self, obj, method_name, *args):
        """Safely call a method that might be a property in some Qt versions
        
        This handles KLayout's Qt bindings where some methods might be properties.
        """
        try:
            attr = getattr(obj, method_name)
            
            # Check if it's callable
            if callable(attr):
                # It's a method, call it with args
                return attr(*args)
            else:
                # It's a property, return its value (should have no args)
                if len(args) > 0:
                    print(f"[FIB Panel] Warning: {method_name} is a property but args were provided: {args}")
                return attr
                
        except Exception as e:
            print(f"[FIB Panel] Error in _safe_call({method_name}, {args}): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def on_move_marker_up(self):
        """Move selected marker(s) up in the list"""
        try:
            # Get all selected rows
            selected_items = self.marker_list.selectedItems()
            if not selected_items:
                print(f"[FIB Panel] No markers selected")
                return
            
            # Get row indices for selected items
            selected_rows = []
            for item in selected_items:
                try:
                    row = self.marker_list.row(item)
                    selected_rows.append(row)
                except:
                    pass
            
            # Sort rows in ascending order
            selected_rows.sort()
            
            print(f"[FIB Panel] Move up: selected rows = {selected_rows}")
            
            # Check if any selected row is already at top
            if not selected_rows or selected_rows[0] <= 0:
                print(f"[FIB Panel] Cannot move up: first selected item already at top")
                return
            
            # Move each selected marker up by swapping with the one above
            # Process from top to bottom to avoid conflicts
            for row in selected_rows:
                if row > 0:
                    self.markers_list[row], self.markers_list[row - 1] = \
                        self.markers_list[row - 1], self.markers_list[row]
            
            print(f"[FIB Panel] New order: {[m.id for m in self.markers_list]}")
            
            # Rebuild the UI list
            self._rebuild_marker_list_ui()
            
            # Restore selection at new positions
            for row in selected_rows:
                if row > 0:
                    try:
                        item = self.marker_list.item(row - 1)
                        if item:
                            item.setSelected(True)
                    except:
                        pass
            
            print(f"[FIB Panel] Moved {len(selected_rows)} marker(s) up")
            
        except Exception as e:
            print(f"[FIB Panel] Error moving markers up: {e}")
            import traceback
            traceback.print_exc()
    
    def on_move_marker_down(self):
        """Move selected marker(s) down in the list"""
        try:
            # Get all selected rows
            selected_items = self.marker_list.selectedItems()
            if not selected_items:
                print(f"[FIB Panel] No markers selected")
                return
            
            # Get row indices for selected items
            selected_rows = []
            for item in selected_items:
                try:
                    row = self.marker_list.row(item)
                    selected_rows.append(row)
                except:
                    pass
            
            # Sort rows in descending order (process from bottom to top)
            selected_rows.sort(reverse=True)
            
            # Get list count
            try:
                list_count = self.marker_list.count()
            except TypeError:
                list_count = self.marker_list.count
            
            print(f"[FIB Panel] Move down: selected rows = {selected_rows}, list_count = {list_count}")
            
            # Check if any selected row is already at bottom
            if not selected_rows or selected_rows[0] >= list_count - 1:
                print(f"[FIB Panel] Cannot move down: last selected item already at bottom")
                return
            
            # Move each selected marker down by swapping with the one below
            # Process from bottom to top to avoid conflicts
            for row in selected_rows:
                if row < len(self.markers_list) - 1:
                    self.markers_list[row], self.markers_list[row + 1] = \
                        self.markers_list[row + 1], self.markers_list[row]
            
            print(f"[FIB Panel] New order: {[m.id for m in self.markers_list]}")
            
            # Rebuild the UI list
            self._rebuild_marker_list_ui()
            
            # Restore selection at new positions
            for row in selected_rows:
                if row < list_count - 1:
                    try:
                        item = self.marker_list.item(row + 1)
                        if item:
                            item.setSelected(True)
                    except:
                        pass
            
            print(f"[FIB Panel] Moved {len(selected_rows)} marker(s) down")
            
        except Exception as e:
            print(f"[FIB Panel] Error moving markers down: {e}")
            import traceback
            traceback.print_exc()


# Global panel instance
fib_panel_instance = None

def create_fib_panel():
    """Create and show the FIB panel"""
    global fib_panel_instance
    
    try:
        main_window = pya.Application.instance().main_window()
        
        # Create panel if it doesn't exist or if it was destroyed
        if fib_panel_instance is None or not is_panel_valid(fib_panel_instance):
            fib_panel_instance = FIBPanel(main_window)
            # Keep a strong reference to prevent garbage collection
            main_window._fib_panel_ref = fib_panel_instance
        
        # Add to main window
        main_window.addDockWidget(pya.Qt.RightDockWidgetArea, fib_panel_instance)
        fib_panel_instance.show()
        
        print("[FIB Panel] Created and docked successfully")
        return fib_panel_instance
        
    except Exception as e:
        print(f"[FIB Panel] Error creating panel: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_fib_panel():
    """Get the current FIB panel instance"""
    global fib_panel_instance
    
    # Check if panel is still valid
    if fib_panel_instance and is_panel_valid(fib_panel_instance):
        return fib_panel_instance
    else:
        print("[FIB Panel] Panel invalid, returning None")
        return None

def is_panel_valid(panel):
    """Check if panel is still valid and not destroyed"""
    try:
        if panel is None:
            return False
        # Try to access a basic property to check if object is still valid
        _ = panel.isVisible()
        return True
    except:
        return False

# Auto-create panel when module is loaded
if __name__ == "__main__":
    create_fib_panel()