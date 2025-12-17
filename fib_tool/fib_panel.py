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
from markers import CutMarker, ConnectMarker, ProbeMarker
from config import LAYERS, GEOMETRIC_PARAMS, UI_TIMEOUTS, DEFAULT_MARKER_NOTES
from marker_menu import MarkerContextMenu
from smart_counter import SmartCounter
from file_dialog_helper import FileDialogHelper

class FIBPanel(pya.QDockWidget):
    """Main FIB Panel - Dockable widget for KLayout"""
    
    def __init__(self, parent=None):
        super().__init__("FIB Panel", parent)
        self.markers_list = []  # Global marker list
        self.active_mode = None
        self.marker_notes_dict = {}  # Centralized notes storage: marker_id -> notes
        
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
            
            # Title with compact styling
            title = pya.QLabel("FIB Tool Panel")
            title.setStyleSheet("font-weight: bold; font-size: 12px; margin: 0px; padding: 1px;")  # Smaller font and minimal padding
            self.main_layout.addWidget(title)
            
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
            
            # Second row: Export PDF
            btn_layout2 = pya.QHBoxLayout()
            
            btn_export_pdf = pya.QPushButton("Export PDF")
            btn_export_pdf.clicked.connect(self.on_export_pdf)
            
            btn_layout2.addWidget(btn_export_pdf)
            
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
            widget_min_width = 75  # Adjusted to 75 to comfortably fit "Connect" text
            
            # Cut button with explicit styling
            self.btn_cut = pya.QPushButton("Cut")
            self.btn_cut.setFixedWidth(widget_min_width)  # Fixed width for consistency
            self.btn_cut.setFixedHeight(widget_height)
            self.btn_cut.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
            
            # Cut mode combo with identical styling
            self.cut_mode_combo = pya.QComboBox()
            self.cut_mode_combo.addItem("2 Points")
            self.cut_mode_combo.addItem("Multi Points")
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
            self.connect_mode_combo.addItem("Multi Points")
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
            self.marker_list.setContextMenuPolicy(pya.Qt.CustomContextMenu)
            self.marker_list.customContextMenuRequested.connect(self.on_marker_context_menu)
            self.marker_list.itemDoubleClicked.connect(self.on_marker_double_clicked)
            # Remove maximum height constraint to allow expansion

            # Enable drag-drop reordering
            self.marker_list.setDragEnabled(True)
            self.marker_list.setAcceptDrops(True)
            self.marker_list.setDropIndicatorShown(True)
            self.marker_list.setDragDropMode(pya.QAbstractItemView.InternalMove)
            self.marker_list.setDefaultDropAction(pya.Qt.MoveAction)

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
                pya.MessageBox.info("FIB Panel", "New project created", pya.MessageBox.Ok)
                return

            # Show confirmation dialog with save option
            marker_count = len(self.markers_list)

            # Create custom dialog with three buttons
            result = pya.MessageBox.warning(
                "New Project",
                f"You have {marker_count} marker(s) in the current project.\n\n"
                f"Do you want to save before clearing?",
                pya.MessageBox.Yes | pya.MessageBox.No | pya.MessageBox.Cancel
            )

            if result == pya.MessageBox.Cancel:
                print("[FIB Panel] New project cancelled by user")
                return

            if result == pya.MessageBox.Yes:
                # User wants to save first
                print("[FIB Panel] User chose to save before clearing")

                # Trigger save dialog
                try:
                    from file_dialog_helper import FileDialogHelper
                    filename = FileDialogHelper.get_save_filename(self)

                    if filename:
                        # Save markers
                        success = self.save_markers_to_json(filename)

                        if not success:
                            # Save failed, ask if user wants to continue anyway
                            retry_result = pya.MessageBox.warning(
                                "Save Failed",
                                f"Failed to save markers.\n\n"
                                f"Do you still want to clear the project?",
                                pya.MessageBox.Yes | pya.MessageBox.No
                            )

                            if retry_result == pya.MessageBox.No:
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
                        retry_result = pya.MessageBox.warning(
                            "Save Cancelled",
                            f"Save cancelled.\n\n"
                            f"Do you still want to clear the project without saving?",
                            pya.MessageBox.Yes | pya.MessageBox.No
                        )

                        if retry_result == pya.MessageBox.No:
                            print("[FIB Panel] New project cancelled after save cancellation")
                            return

                except Exception as save_error:
                    print(f"[FIB Panel] Error during save: {save_error}")

                    # Ask if user wants to continue despite error
                    retry_result = pya.MessageBox.warning(
                        "Save Error",
                        f"Error during save: {save_error}\n\n"
                        f"Do you still want to clear the project?",
                        pya.MessageBox.Yes | pya.MessageBox.No
                    )

                    if retry_result == pya.MessageBox.No:
                        print("[FIB Panel] New project cancelled after save error")
                        return

            # Clear project (both "No" and "Yes after save" paths reach here)
            self._clear_project_internal()

            pya.MessageBox.info("FIB Panel", "New project created", pya.MessageBox.Ok)
            print(f"[FIB Panel] New project created, cleared {marker_count} markers")

        except Exception as e:
            print(f"[FIB Panel] Error in on_new_project: {e}")
            import traceback
            traceback.print_exc()
            pya.MessageBox.warning("FIB Panel", f"Error creating new project: {e}", pya.MessageBox.Ok)

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
            self.marker_list.clear()

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
        result = pya.MessageBox.question(
            "FIB Panel", "Close current project?", 
            pya.MessageBox.Yes | pya.MessageBox.No
        )
        if result == pya.MessageBox.Yes:
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
                    pya.MessageBox.info("FIB Panel", f"Project saved as {basename} with {len(self.markers_list)} markers", pya.MessageBox.Ok)
                else:
                    pya.MessageBox.warning("FIB Panel", "Failed to save project", pya.MessageBox.Ok)
            else:
                # User cancelled or error, try auto-save as fallback
                try:
                    from simple_save_load import simple_save_project
                    saved_filename = simple_save_project(self)
                    if saved_filename:
                        basename = os.path.basename(saved_filename)
                        pya.MessageBox.info("FIB Panel", f"Project auto-saved as {basename} with {len(self.markers_list)} markers", pya.MessageBox.Ok)
                except Exception as fallback_error:
                    print(f"[FIB Panel] Fallback save error: {fallback_error}")
                    pya.MessageBox.warning("FIB Panel", "Save failed. Check console for details.", pya.MessageBox.Ok)
                    
        except Exception as e:
            print(f"[FIB Panel] Error in save project: {e}")
            pya.MessageBox.warning("FIB Panel", f"Error saving project: {e}", pya.MessageBox.Ok)
    
    def on_load_project(self):
        """Handle Load project"""
        try:
            # Use better file dialog
            filename = FileDialogHelper.get_load_filename(self)
            
            if filename:
                success = self.load_markers_from_json(filename)
                if success:
                    basename = os.path.basename(filename)
                    pya.MessageBox.info("FIB Panel", f"Project '{basename}' loaded successfully with {len(self.markers_list)} markers", pya.MessageBox.Ok)
                else:
                    pya.MessageBox.warning("FIB Panel", "Failed to load project", pya.MessageBox.Ok)
            else:
                print("[FIB Panel] Load cancelled by user")
                
        except Exception as e:
            print(f"[FIB Panel] Error in load project: {e}")
            pya.MessageBox.warning("FIB Panel", f"Error loading project: {e}", pya.MessageBox.Ok)
    
    def on_export_pdf(self):
        """Handle Export PDF"""
        try:
            if not self.markers_list:
                pya.MessageBox.warning("FIB Panel", "No markers to export. Create some markers first.", pya.MessageBox.Ok)
                return
            
            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view or not current_view.active_cellview().is_valid():
                pya.MessageBox.warning("FIB Panel", "No active layout view found", pya.MessageBox.Ok)
                return
            
            # Ask for filename
            home_dir = os.path.expanduser("~")
            default_filename = os.path.join(home_dir, "fib_markers_report.pdf")
            
            # Use Qt file dialog
            file_dialog = pya.QFileDialog()
            filename = file_dialog.getSaveFileName(self, "Export PDF Report", default_filename, "PDF Files (*.pdf)")
            
            # Handle different return types
            if isinstance(filename, tuple):
                filename = filename[0] if filename[0] else None
            
            if not filename:
                print("[FIB Panel] Export PDF cancelled by user")
                return
            
            # Ensure .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            print(f"[FIB Panel] Exporting PDF to: {filename}")
            
            # Export to PDF
            success = self.export_markers_to_pdf(filename, current_view)
            
            if success:
                basename = os.path.basename(filename)
                pya.MessageBox.info("FIB Panel", f"PDF report exported successfully:\n{basename}\n\n{len(self.markers_list)} markers included", pya.MessageBox.Ok)
            else:
                pya.MessageBox.warning("FIB Panel", "Failed to export PDF. Check console for details.", pya.MessageBox.Ok)
                
        except Exception as e:
            print(f"[FIB Panel] Error in export PDF: {e}")
            import traceback
            traceback.print_exc()
            pya.MessageBox.warning("FIB Panel", f"Error exporting PDF: {e}", pya.MessageBox.Ok)
    
    def on_cut_clicked(self):
        """Handle Cut button - activate toolbar plugin"""
        try:
            # Get selected mode from dropdown
            current_text = self.cut_mode_combo.currentText
            if callable(current_text):
                is_multipoint = current_text() == "Multi Points"
            else:
                is_multipoint = current_text == "Multi Points"
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
                is_multipoint = current_text() == "Multi Points"
            else:
                is_multipoint = current_text == "Multi Points"
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
                is_multipoint = current_text() == "Multi Points"
            else:
                is_multipoint = current_text == "Multi Points"

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
                is_multipoint = current_text() == "Multi Points"
            else:
                is_multipoint = current_text == "Multi Points"

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
        try:
            # Try to use the global function from fib_plugin
            if 'activate_fib_mode' in sys.modules['__main__'].__dict__:
                activate_fib_mode = sys.modules['__main__'].__dict__['activate_fib_mode']
                result = activate_fib_mode(mode)
                print(f"[FIB Panel] Activation result for {mode}: {result}")
                if result:
                    return True
            
            # If global function failed, try direct approach
            print(f"[FIB Panel] Trying direct plugin activation for {mode}")
            
            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view:
                pya.MessageBox.warning("FIB Panel", "No active layout view found", pya.MessageBox.Ok)
                return False
            
            # Import the plugin module to access plugin classes
            try:
                import fib_plugin
                
                # Create a plugin instance
                plugin = fib_plugin.FIBToolPlugin(None)
                plugin.mode = mode
                
                # Activate the plugin
                plugin.activated()
                
                print(f"[FIB Panel] Successfully activated {mode} mode directly")
                return True
                
            except Exception as direct_error:
                print(f"[FIB Panel] Direct activation failed: {direct_error}")
                
                # Last resort: show helpful message
                pya.MessageBox.info("FIB Panel", 
                    f"Panel button activated {mode.upper()} mode.\n"
                    f"Now click on the layout to create {mode} markers.\n\n"
                    f"If this doesn't work, try clicking the '{mode.upper()}' button in the toolbar.",
                    pya.MessageBox.Ok)
                return True  # Return True since we showed the instruction
                
        except Exception as e:
            print(f"[FIB Panel] Error activating plugin {mode}: {e}")
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
            if mode.endswith('_multi'):
                self.status_label.setText(f"{base_mode.upper()} Multi: L-click add, R-click finish")
            else:
                self.status_label.setText(f"{mode.upper()}: Click to add")
            
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
                pya.MessageBox.warning("Coordinate Jump", "Please enter coordinates", pya.MessageBox.Ok)
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
                pya.MessageBox.warning(
                    "Coordinate Jump", 
                    f"Invalid coordinate format: '{coord_text}'\n\nSupported formats:\n- 100 100\n- 100,100\n- (100,100)\n- (100 100)\n- \"100,100\"",
                    pya.MessageBox.Ok
                )
                return
            
            # Extract coordinates
            try:
                x = float(match.group(1))
                y = float(match.group(2))
            except ValueError:
                pya.MessageBox.warning("Coordinate Jump", "Invalid number format", pya.MessageBox.Ok)
                return
            
            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view:
                pya.MessageBox.warning("Coordinate Jump", "No active layout view", pya.MessageBox.Ok)
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
            pya.MessageBox.warning("Coordinate Jump", f"Error: {e}", pya.MessageBox.Ok)
    
    def on_clear_all(self):
        """Clear all markers"""
        if self.markers_list:
            result = pya.MessageBox.question(
                "Clear All",
                f"Delete all {len(self.markers_list)} markers from layout and reset counters?",
                pya.MessageBox.Yes | pya.MessageBox.No
            )
            if result == pya.MessageBox.Yes:
                # Clear markers from GDS layout
                self.clear_markers_from_gds()
                
                # Clear coordinate texts
                self.clear_coordinate_texts()
                
                # Reset marker counters
                self.reset_marker_counters()
                
                # Clear panel data
                self.markers_list.clear()
                self.marker_list.clear()
                
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
            from config import LAYERS
            
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
                    
                    from config import LAYERS
                    coord_layer = layout.layer(LAYERS['coordinates'], 0)
                    cell.shapes(coord_layer).clear()
                    print("[FIB Panel] Coordinate texts cleared directly")
                    
        except Exception as e:
            print(f"[FIB Panel] Error clearing coordinate texts: {e}")
    
    def reset_marker_counters(self):
        """Reset marker counters to start from 0"""
        try:
            # Access the global marker counter from fib_plugin
            if 'marker_counter' in sys.modules['__main__'].__dict__:
                marker_counter = sys.modules['__main__'].__dict__['marker_counter']
                marker_counter['cut'] = 0
                marker_counter['connect'] = 0
                marker_counter['probe'] = 0
                print("[FIB Panel] Marker counters reset via global variable")
            else:
                # Try to import and reset directly
                try:
                    import fib_plugin
                    if hasattr(fib_plugin, 'marker_counter'):
                        fib_plugin.marker_counter['cut'] = 0
                        fib_plugin.marker_counter['connect'] = 0
                        fib_plugin.marker_counter['probe'] = 0
                        print("[FIB Panel] Marker counters reset via module import")
                except Exception as import_error:
                    print(f"[FIB Panel] Could not reset counters via import: {import_error}")
                    
        except Exception as e:
            print(f"[FIB Panel] Error resetting marker counters: {e}")
    
    def save_markers_to_json(self, filename):
        """Save markers to JSON file"""
        try:
            import json
            import os
            
            # Ensure we save to a writable location
            if not os.path.isabs(filename):
                # If relative path, save to user's home directory
                home_dir = os.path.expanduser("~")
                filename = os.path.join(home_dir, filename)
                print(f"[FIB Panel] Saving to home directory: {filename}")
            
            # Prepare marker data
            markers_data = []
            for marker in self.markers_list:
                marker_class_name = marker.__class__.__name__
                
                # Handle multi-point markers
                if 'MultiPoint' in marker_class_name:
                    if 'Cut' in marker_class_name:
                        marker_type = 'multipoint_cut'
                    elif 'Connect' in marker_class_name:
                        marker_type = 'multipoint_connect'
                    else:
                        marker_type = 'multipoint'
                    
                    marker_dict = {
                        'id': marker.id,
                        'type': marker_type,
                        'points': marker.points if hasattr(marker, 'points') else [],
                        'notes': getattr(marker, 'notes', ''),
                        'screenshots': getattr(marker, 'screenshots', []),
                        'target_layers': getattr(marker, 'target_layers', [])
                    }
                else:
                    # Regular markers
                    marker_dict = {
                        'id': marker.id,
                        'type': marker_class_name.replace('Marker', '').lower(),
                        'notes': getattr(marker, 'notes', ''),
                        'screenshots': getattr(marker, 'screenshots', []),
                        'target_layers': getattr(marker, 'target_layers', [])
                    }
                    
                    # Add coordinates based on marker type
                    if hasattr(marker, 'x1'):  # CUT or CONNECT
                        marker_dict['x1'] = marker.x1
                        marker_dict['y1'] = marker.y1
                        marker_dict['x2'] = marker.x2
                        marker_dict['y2'] = marker.y2
                    else:  # PROBE
                        marker_dict['x'] = marker.x
                        marker_dict['y'] = marker.y
                
                markers_data.append(marker_dict)
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump({
                    'version': '1.0',
                    'markers': markers_data,
                    'marker_notes_dict': self.marker_notes_dict,  # Save centralized notes dict
                    'marker_counters': {
                        'cut': sys.modules['__main__'].__dict__.get('marker_counter', {}).get('cut', 0),
                        'connect': sys.modules['__main__'].__dict__.get('marker_counter', {}).get('connect', 0),
                        'probe': sys.modules['__main__'].__dict__.get('marker_counter', {}).get('probe', 0)
                    }
                }, f, indent=2)
            
            print(f"[FIB Panel] Saved {len(markers_data)} markers to {filename}")
            return True
            
        except Exception as e:
            print(f"[FIB Panel] Error saving to JSON: {e}")
            return False
    
    def load_markers_from_json(self, filename):
        """Load markers from JSON file"""
        try:
            import json
            import os
            
            # Handle relative paths - look in home directory
            if not os.path.isabs(filename):
                home_dir = os.path.expanduser("~")
                full_path = os.path.join(home_dir, filename)
                if os.path.exists(full_path):
                    filename = full_path
                    print(f"[FIB Panel] Loading from home directory: {filename}")
                elif not os.path.exists(filename):
                    print(f"[FIB Panel] File not found in current dir, trying home: {full_path}")
                    filename = full_path
            
            # Load from file
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear current markers
            self.on_new_project()
            
            # Load centralized notes dictionary
            if 'marker_notes_dict' in data:
                self.marker_notes_dict = data['marker_notes_dict']
                print(f"[FIB Panel] Loaded notes dict: {self.marker_notes_dict}")
            else:
                self.marker_notes_dict = {}
            
            # Load marker counters
            if 'marker_counters' in data:
                counters = data['marker_counters']
                if 'marker_counter' in sys.modules['__main__'].__dict__:
                    global_counter = sys.modules['__main__'].__dict__['marker_counter']
                    global_counter['cut'] = counters.get('cut', 0)
                    global_counter['connect'] = counters.get('connect', 0)
                    global_counter['probe'] = counters.get('probe', 0)
            
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
            from markers import CutMarker, ConnectMarker, ProbeMarker
            
            # Try to import multi-point markers
            try:
                from multipoint_markers import MultiPointCutMarker, MultiPointConnectMarker
                multipoint_available = True
            except ImportError:
                multipoint_available = False
                print("[FIB Panel] Multi-point markers not available for loading")
            
            # Load markers
            loaded_count = 0
            for marker_data in data.get('markers', []):
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
                    
                    # Draw marker to GDS
                    from config import LAYERS
                    if marker_type.startswith('multipoint_'):
                        base_type = marker_type.replace('multipoint_', '')
                        fib_layer = layout.layer(LAYERS[base_type], 0)
                    else:
                        fib_layer = layout.layer(LAYERS[marker_type], 0)
                    
                    marker.to_gds(cell, fib_layer)
                    
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
    
    def export_markers_to_pdf(self, filename, view):
        """Export markers to PDF report with screenshots"""
        try:
            import os
            from screenshot_export import (
                export_markers_with_screenshots,
                generate_html_report_with_screenshots
            )
            
            # Get output directory
            output_dir = os.path.dirname(filename)
            if not output_dir:
                output_dir = os.path.expanduser("~")
            
            print(f"[FIB Panel] Starting export with screenshots...")
            print(f"[FIB Panel] Output directory: {output_dir}")
            
            # Generate screenshots for all markers
            screenshots_dict = export_markers_with_screenshots(
                self.markers_list, 
                view, 
                output_dir
            )
            
            print(f"[FIB Panel] Screenshots generated: {len(screenshots_dict)} markers")
            
            # Generate HTML report with screenshots
            html_filename = filename.replace('.pdf', '.html')
            success = generate_html_report_with_screenshots(
                self.markers_list,
                screenshots_dict,
                html_filename
            )
            
            if not success:
                print(f"[FIB Panel] Failed to generate HTML report")
                return False
            
            print(f"[FIB Panel] HTML report saved to: {html_filename}")
            
            # Try to convert to PDF using available tools
            pdf_created = False
            
            # Method 1: Try using wkhtmltopdf (if installed)
            try:
                import subprocess
                result = subprocess.run(['wkhtmltopdf', '--version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print("[FIB Panel] Using wkhtmltopdf for PDF conversion")
                    subprocess.run(['wkhtmltopdf', html_filename, filename], 
                                 check=True, timeout=30)
                    pdf_created = True
            except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                print(f"[FIB Panel] wkhtmltopdf not available: {e}")
            except Exception as wk_error:
                print(f"[FIB Panel] wkhtmltopdf error: {wk_error}")
            
            # Method 2: Try using weasyprint (if installed)
            if not pdf_created:
                try:
                    from weasyprint import HTML
                    print("[FIB Panel] Using weasyprint for PDF conversion")
                    HTML(html_filename).write_pdf(filename)
                    pdf_created = True
                except ImportError:
                    print("[FIB Panel] weasyprint not available")
                except Exception as weasy_error:
                    print(f"[FIB Panel] weasyprint error: {weasy_error}")
            
            # If PDF conversion failed, just keep the HTML
            if not pdf_created:
                print(f"[FIB Panel] PDF conversion tools not available. HTML report saved instead.")
                pya.MessageBox.info("FIB Panel", 
                    f"PDF conversion tools not installed.\n\n"
                    f"HTML report with screenshots saved to:\n{html_filename}\n\n"
                    f"To enable PDF export, install:\n"
                    f"  pip install weasyprint\n"
                    f"or install wkhtmltopdf",
                    pya.MessageBox.Ok)
                return True
            
            print(f"[FIB Panel] PDF report created: {filename}")
            return True
            
        except Exception as e:
            print(f"[FIB Panel] Error exporting to PDF: {e}")
            import traceback
            traceback.print_exc()
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
                        
                        # Show complete point coordinates for multi-point markers
                        if hasattr(marker, 'points') and len(marker.points) > 0:
                            if len(marker.points) <= 3:
                                # For 3 or fewer points, show all coordinates in panel
                                point_strs = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points]
                                coords = f"{len(marker.points)} pts: " + " → ".join(point_strs)
                            else:
                                # For more than 3 points, show first 2, ..., last 1 (shorter for panel)
                                first_points = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points[:2]]
                                last_point = f"({marker.points[-1][0]:.3f},{marker.points[-1][1]:.3f})"
                                coords = f"{len(marker.points)} pts: " + " → ".join(first_points) + " → ... → " + last_point
                        else:
                            coords = "No points"
                    else:
                        # Regular markers
                        marker_type = marker_class_name.replace('Marker', '').upper()
                        
                        if hasattr(marker, 'x1'):  # CUT or CONNECT
                            coords = f"({marker.x1:.3f},{marker.y1:.3f}) to ({marker.x2:.3f},{marker.y2:.3f})"
                        else:  # PROBE
                            coords = f"({marker.x:.3f},{marker.y:.3f})"
                    
                    item_text = f"{marker.id} - {marker_type} - {coords}"
                    self.marker_list.addItem(item_text)
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

            # Rebuild markers_list from current UI order
            new_markers_list = []
            for i in range(self.marker_list.count()):
                item = self.marker_list.item(i)
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
            text = item.text() if callable(item.text) else item.text
            if callable(text):
                text = text()
            # Format: "MARKER_ID - TYPE - (coords)"
            parts = text.split(' - ')
            return parts[0].strip() if parts else "Unknown"
        except:
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
            ui_order = [self._extract_marker_id_from_item(
                self.marker_list.item(i)
            ) for i in range(self.marker_list.count())]

            data_order = [m.id for m in self.markers_list]

            if ui_order != data_order:
                self._sync_markers_to_ui_order()
        except Exception as e:
            print(f"[FIB Panel] Reorder detection error: {e}")

    def _sync_markers_to_ui_order(self):
        """Sync markers_list to match UI order"""
        try:
            new_list = []
            for i in range(self.marker_list.count()):
                marker_id = self._extract_marker_id_from_item(
                    self.marker_list.item(i)
                )
                marker = self._find_marker_by_id_in_list(marker_id)
                if marker:
                    new_list.append(marker)

            self.markers_list = new_list
            print(f"[FIB Panel] Synced to UI order")
        except Exception as e:
            print(f"[FIB Panel] Sync error: {e}")


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