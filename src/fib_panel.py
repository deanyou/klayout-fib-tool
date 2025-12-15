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
from config import LAYERS

class FIBPanel(pya.QDockWidget):
    """Main FIB Panel - Dockable widget for KLayout"""
    
    def __init__(self, parent=None):
        super().__init__("FIB Panel", parent)
        self.markers_list = []  # Global marker list
        self.active_mode = None
        
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
            # Main container
            self.container = pya.QWidget()
            self.main_layout = pya.QVBoxLayout(self.container)
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.main_layout.setSpacing(5)
            
            # Title
            title = pya.QLabel("FIB Tool Panel")
            title.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.main_layout.addWidget(title)
            
            # Project management section
            self.create_project_section()
            
            # Marker creation section
            self.create_marker_section()
            
            # Marker list section
            self.create_marker_list_section()
            
            # Set the widget
            self.setWidget(self.container)
            self.setMinimumWidth(250)
            
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
            
            # Buttons row
            btn_layout = pya.QHBoxLayout()
            
            btn_new = pya.QPushButton("New")
            btn_close = pya.QPushButton("Close")
            btn_save = pya.QPushButton("Save")
            
            btn_new.clicked.connect(self.on_new_project)
            btn_close.clicked.connect(self.on_close_project)
            btn_save.clicked.connect(self.on_save_project)
            
            btn_layout.addWidget(btn_new)
            btn_layout.addWidget(btn_close)
            btn_layout.addWidget(btn_save)
            
            group_layout.addLayout(btn_layout)
            self.main_layout.addWidget(group)
            
        except Exception as e:
            print(f"[FIB Panel] Error creating project section: {e}")
    
    def create_marker_section(self):
        """Create marker creation section"""
        try:
            group = pya.QGroupBox("Add Markers")
            group_layout = pya.QVBoxLayout(group)
            
            # Buttons row
            btn_layout = pya.QHBoxLayout()
            
            self.btn_cut = pya.QPushButton("Cut")
            self.btn_connect = pya.QPushButton("Connect")
            self.btn_probe = pya.QPushButton("Probe")
            
            self.btn_cut.clicked.connect(self.on_cut_clicked)
            self.btn_connect.clicked.connect(self.on_connect_clicked)
            self.btn_probe.clicked.connect(self.on_probe_clicked)
            
            btn_layout.addWidget(self.btn_cut)
            btn_layout.addWidget(self.btn_connect)
            btn_layout.addWidget(self.btn_probe)
            
            group_layout.addLayout(btn_layout)
            
            # Status label
            self.status_label = pya.QLabel("Ready")
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
    
    def create_marker_list_section(self):
        """Create marker list section"""
        try:
            group = pya.QGroupBox("Markers")
            group_layout = pya.QVBoxLayout(group)
            
            # Simple list widget instead of tree
            self.marker_list = pya.QListWidget()
            self.marker_list.setContextMenuPolicy(pya.Qt.CustomContextMenu)
            self.marker_list.customContextMenuRequested.connect(self.on_marker_context_menu)
            self.marker_list.itemDoubleClicked.connect(self.on_marker_double_clicked)
            
            group_layout.addWidget(self.marker_list)
            
            # Clear button
            btn_clear = pya.QPushButton("Clear All")
            btn_clear.clicked.connect(self.on_clear_all)
            group_layout.addWidget(btn_clear)
            
            self.main_layout.addWidget(group)
            
        except Exception as e:
            print(f"[FIB Panel] Error creating marker list section: {e}")
            # Create minimal fallback
            self.marker_list = None
    
    # Event handlers
    def on_new_project(self):
        """Handle New project"""
        self.markers_list.clear()
        self.marker_list.clear()
        pya.MessageBox.info("FIB Panel", "New project created", pya.MessageBox.Ok)
    
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
        pya.MessageBox.info("FIB Panel", f"Project saved with {len(self.markers_list)} markers", pya.MessageBox.Ok)
    
    def on_cut_clicked(self):
        """Handle Cut button - activate toolbar plugin"""
        self.activate_toolbar_plugin('cut')
        self.activate_mode('cut')
    
    def on_connect_clicked(self):
        """Handle Connect button - activate toolbar plugin"""
        self.activate_toolbar_plugin('connect')
        self.activate_mode('connect')
    
    def on_probe_clicked(self):
        """Handle Probe button - activate toolbar plugin"""
        self.activate_toolbar_plugin('probe')
        self.activate_mode('probe')
    
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
            self.mode_buttons[mode].setStyleSheet("background-color: lightgreen;")
            self.status_label.setText(f"{mode.upper()} mode active - Click on layout")
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
                        print(f"[FIB Panel] Cleared temp_points for {plugin_mode} plugin")
        except Exception as e:
            print(f"[FIB Panel] Error clearing pending points: {e}")
    
    def on_marker_context_menu(self, position):
        """Handle right-click on marker list"""
        item = self.marker_list.itemAt(position)
        if not item:
            return
        
        menu = pya.QMenu()
        
        action_fit = menu.addAction("Fit to Marker")
        action_delete = menu.addAction("Delete Marker")
        action_rename = menu.addAction("Rename Marker")
        
        action_fit.triggered.connect(lambda: self.fit_to_marker(item))
        action_delete.triggered.connect(lambda: self.delete_marker(item))
        action_rename.triggered.connect(lambda: self.rename_marker(item))
        
        menu.exec_(self.marker_list.viewport().mapToGlobal(position))
    
    def on_marker_double_clicked(self, item):
        """Handle double-click on marker"""
        self.fit_to_marker(item)
    
    def fit_to_marker(self, item):
        """Fit view to marker"""
        marker_id = item.text().split(' - ')[0]
        pya.MessageBox.info("FIB Panel", f"Fit to {marker_id} (not implemented yet)", pya.MessageBox.Ok)
    
    def delete_marker(self, item):
        """Delete marker"""
        marker_id = item.text().split(' - ')[0]
        result = pya.MessageBox.question(
            "Delete Marker",
            f"Are you sure you want to delete {marker_id}?",
            pya.MessageBox.Yes | pya.MessageBox.No
        )
        if result == pya.MessageBox.Yes:
            # Remove from list widget
            row = self.marker_list.row(item)
            self.marker_list.takeItem(row)
            
            # Remove from markers list
            self.markers_list = [m for m in self.markers_list if m.id != marker_id]
            
            print(f"[FIB Panel] Deleted marker: {marker_id}")
    
    def rename_marker(self, item):
        """Rename marker"""
        old_name = item.text().split(' - ')[0]
        new_name, ok = pya.QInputDialog.getText(
            self, "Rename Marker",
            "Enter new name:",
            pya.QLineEdit.Normal,
            old_name
        )
        if ok and new_name and new_name != old_name:
            # Update display
            old_text = item.text()
            new_text = old_text.replace(old_name, new_name, 1)
            item.setText(new_text)
            
            # Update marker object
            for marker in self.markers_list:
                if marker.id == old_name:
                    marker.id = new_name
                    break
            
            print(f"[FIB Panel] Renamed: {old_name} -> {new_name}")
    
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
                    marker_type = marker.__class__.__name__.replace('Marker', '').upper()
                    
                    if hasattr(marker, 'x1'):  # CUT or CONNECT
                        coords = f"({marker.x1:.2f},{marker.y1:.2f}) to ({marker.x2:.2f},{marker.y2:.2f})"
                    else:  # PROBE
                        coords = f"({marker.x:.2f},{marker.y:.2f})"
                    
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