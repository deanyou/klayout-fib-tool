#!/usr/bin/env python3
"""
FIB Tool Plugin - Mouse-based marker creation

This plugin can be loaded in two ways:

1. Via SALT Package (recommended for production):
   - Automatically loaded by klayout_package.py
   - Install via Salt Package Manager

2. Via exec() (for development/testing):
   import sys; sys.path.insert(0, '/path/to/klayout-fib-tool/fib_tool')
   exec(open('/path/to/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())

Version: 1.0.0
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
from .layer_manager import ensure_fib_layers, get_layer_info_summary, verify_layers_exist

# Import layer tap functionality
try:
    from .layer_tap import get_layer_at_point_with_selection, format_layer_for_display
    LAYER_TAP_AVAILABLE = True
    print("[FIB Plugin] Layer tap functionality available")
except ImportError as e:
    LAYER_TAP_AVAILABLE = False
    print(f"[FIB Plugin] Layer tap not available: {e}")

# Global flag to prevent double initialization
# This is important when the plugin is loaded both via SALT and exec()
_FIB_PLUGIN_FACTORIES_CREATED = False


def get_or_create_layer(layout, layer_num, datatype=0, layer_name=None):
    """
    Get layer index, create if it doesn't exist.
    
    Args:
        layout: pya.Layout object
        layer_num: Layer number
        datatype: Datatype (default 0)
        layer_name: Optional layer name
    
    Returns:
        int: Layer index
    """
    # First try to find existing layer
    for layer_info in layout.layer_infos():
        if layer_info.layer == layer_num and layer_info.datatype == datatype:
            return layout.layer(layer_info)
    
    # Layer doesn't exist, create it
    if layer_name is None:
        layer_name = f"Layer_{layer_num}"
    
    new_layer_info = pya.LayerInfo(layer_num, datatype, layer_name)
    layer_index = layout.insert_layer(new_layer_info)
    print(f"[FIB] Created layer {layer_num}/{datatype} ({layer_name}) with index {layer_index}")
    
    return layer_index

# FIB Tool - Version 3.0
# This version uses KLayout's Plugin system for mouse handling

# Global marker counter
marker_counter = {
    'cut': 0,
    'connect': 0,
    'probe': 0
}

# Global variables to store plugin instances for panel access
current_plugins = {
    'cut': None,
    'connect': None,
    'probe': None
}

# Global active plugin reference
active_plugin = None
current_mode = None

# Panel availability flag (import delayed to avoid circular dependency)
PANEL_AVAILABLE = True

def get_fib_panel():
    """Get FIB panel instance (lazy import to avoid circular dependency)"""
    try:
        from .fib_panel import get_fib_panel as _get_fib_panel
        return _get_fib_panel()
    except ImportError:
        global PANEL_AVAILABLE
        PANEL_AVAILABLE = False
        return None

# Import multi-point marker classes
try:
    from .multipoint_markers import (
        MultiPointCutMarker, MultiPointConnectMarker,
        create_multipoint_cut_marker, create_multipoint_connect_marker
    )
    MULTIPOINT_AVAILABLE = True
    print("[FIB Plugin] Multi-point markers available")
except ImportError:
    MULTIPOINT_AVAILABLE = False
    print("[FIB Plugin] Multi-point markers not available")

# Marker creation functions
def _get_next_marker_number(marker_type):
    """Get next available marker number using smart counter with fallback"""
    global marker_counter

    try:
        if PANEL_AVAILABLE:
            panel = get_fib_panel()
            if panel and hasattr(panel, 'smart_counter'):
                return panel.smart_counter.get_next_number(marker_type)
        return marker_counter[marker_type]
    except (AttributeError, KeyError, TypeError) as e:
        print(f"[FIB] Smart counter error: {e}, using fallback")
        return marker_counter[marker_type]


def _create_marker_internal(marker_type, marker_class, *args, **kwargs):
    """Internal unified marker creation function

    Args:
        marker_type: 'cut', 'connect', or 'probe'
        marker_class: CutMarker, ConnectMarker, or ProbeMarker class
        *args, **kwargs: Arguments passed to marker class constructor
    """
    global marker_counter

    # Get next number
    next_number = _get_next_marker_number(marker_type)
    marker_id = f"{marker_type.upper()}_{next_number}"

    # Update global counter
    marker_counter[marker_type] = max(marker_counter[marker_type], next_number + 1)

    # Create marker
    marker = marker_class(marker_id, *args, **kwargs)
    marker.notes = DEFAULT_MARKER_NOTES[marker_type]
    marker.screenshots = []

    # Notify panel
    if PANEL_AVAILABLE:
        try:
            panel = get_fib_panel()
            if panel:
                panel.add_marker(marker)
        except Exception as e:
            print(f"[FIB Plugin] Error notifying panel for {marker_type.upper()} marker: {e}")

    return marker


def create_cut_marker(x1, y1, x2, y2, layer1=None, layer2=None):
    """Create a CUT marker connecting two points

    Args:
        x1, y1: First point coordinates (microns)
        x2, y2: Second point coordinates (microns)
        layer1: Layer info string for point 1 (e.g., "M1" or "1/0")
        layer2: Layer info string for point 2 (e.g., "M2" or "2/0")
    """
    print(f"[DEBUG] create_cut_marker called with: x1={x1}, y1={y1}, x2={x2}, y2={y2}, layer1={layer1}, layer2={layer2}")
    marker = _create_marker_internal('cut', CutMarker, x1, y1, x2, y2, 6, layer1=layer1, layer2=layer2)
    print(f"[DEBUG] Created marker: {marker.id} from ({x1}, {y1}) [{layer1 or 'N/A'}] to ({x2}, {y2}) [{layer2 or 'N/A'}]")
    return marker

def create_connect_marker(x1, y1, x2, y2, layer1=None, layer2=None):
    """Create a CONNECT marker

    Args:
        x1, y1: First point coordinates (microns)
        x2, y2: Second point coordinates (microns)
        layer1: Layer info string for point 1 (e.g., "M1" or "1/0")
        layer2: Layer info string for point 2 (e.g., "M2" or "2/0")
    """
    marker = _create_marker_internal('connect', ConnectMarker, x1, y1, x2, y2, 6, layer1=layer1, layer2=layer2)
    print(f"[DEBUG] Created marker: {marker.id} from ({x1}, {y1}) [{layer1 or 'N/A'}] to ({x2}, {y2}) [{layer2 or 'N/A'}]")
    return marker

def create_probe_marker(x, y, target_layer=None):
    """Create a PROBE marker

    Args:
        x, y: Probe point coordinates (microns)
        target_layer: Layer info string at probe point (e.g., "M1" or "1/0")
    """
    marker = _create_marker_internal('probe', ProbeMarker, x, y, 6, target_layer=target_layer)
    print(f"[DEBUG] Created marker: {marker.id} at ({x}, {y}) [{target_layer or 'N/A'}]")
    return marker

# Drawing function
def draw_marker(marker, cell, layout):
    """Draw marker to GDS and show message"""
    # Get FIB layer based on marker type
    marker_class_name = marker.__class__.__name__.lower()
    
    # Handle multi-point markers
    if 'multipoint' in marker_class_name:
        if 'cut' in marker_class_name:
            layer_key = 'cut'
        elif 'connect' in marker_class_name:
            layer_key = 'connect'
        else:
            layer_key = 'cut'  # fallback
    else:
        # Regular markers
        layer_key = marker_class_name.replace('marker', '')
    
    # Get or create the FIB layer
    layer_names = {'cut': 'FIB_CUT', 'connect': 'FIB_CONNECT', 'probe': 'FIB_PROBE'}
    layer_name = layer_names.get(layer_key, f'FIB_{layer_key.upper()}')
    fib_layer = get_or_create_layer(layout, LAYERS[layer_key], 0, layer_name)
    
    # Draw marker
    marker.to_gds(cell, fib_layer)
    
    # Update coordinate texts to include marker ID
    update_coordinate_texts_with_marker_id(marker, cell, layout)
    
    # Show message
    try:
        if hasattr(marker, 'points') and len(marker.points) > 2:
            pya.MainWindow.instance().message(f"Created {marker.id} ({len(marker.points)} points)", UI_TIMEOUTS['message_short'])
        else:
            pya.MainWindow.instance().message(f"Created {marker.id}", UI_TIMEOUTS['message_short'])
    except Exception as msg_error:
        print(f"[FIB] Message error: {msg_error}")
        print(f"[FIB] Created {marker.id}")
    print(f"[FIB] Created {marker.id}")
    return True

def update_coordinate_texts_with_marker_id(marker, cell, layout):
    """Update coordinate texts to include marker ID"""
    try:
        # Get or create coordinate layer
        coord_layer_num = LAYERS['coordinates']
        coord_layer = get_or_create_layer(layout, coord_layer_num, 0, 'FIB_COORDINATES')
        dbu = layout.dbu
        
        # Get marker coordinates
        if hasattr(marker, 'points'):  # Multi-point markers
            coordinates = marker.points
        elif hasattr(marker, 'x1'):  # CUT or CONNECT markers
            coordinates = [(marker.x1, marker.y1), (marker.x2, marker.y2)]
        else:  # PROBE marker
            coordinates = [(marker.x, marker.y)]
        
        updated_count = 0
        
        # Update coordinate texts near these positions
        for coord_x, coord_y in coordinates:
            # Convert to database units for search
            search_x = int(coord_x / dbu)
            search_y = int(coord_y / dbu)
            
            # Create search region - larger radius to ensure we find the text
            search_radius = int(GEOMETRIC_PARAMS['search_radius'] / dbu)
            search_box = pya.Box(
                search_x - search_radius, search_y - search_radius,
                search_x + search_radius, search_y + search_radius
            )
            
            # Find and update coordinate texts
            shapes_to_remove = []
            shapes_to_add = []
            
            for shape in cell.shapes(coord_layer).each_overlapping(search_box):
                if shape.is_text():
                    text_obj = shape.text
                    text_string = text_obj.string
                    
                    # Check if this is a coordinate text for this position
                    expected_coord = f"({coord_x:.2f},{coord_y:.2f})"
                    
                    # More flexible matching - check if coordinates are close enough
                    # Extract coordinates from text using regex
                    import re
                    coord_pattern = r'\(([0-9.-]+),([0-9.-]+)\)'
                    match = re.search(coord_pattern, text_string)
                    
                    is_matching_coord = False
                    if match:
                        try:
                            text_x = float(match.group(1))
                            text_y = float(match.group(2))
                            # Check if coordinates are close
                            if abs(text_x - coord_x) < GEOMETRIC_PARAMS['coordinate_precision'] and abs(text_y - coord_y) < GEOMETRIC_PARAMS['coordinate_precision']:
                                is_matching_coord = True
                        except ValueError:
                            pass
                    
                    # Look for coordinate text that matches this position and doesn't already have marker ID
                    if (is_matching_coord and 
                        not text_string.startswith(marker.id) and 
                        not ":" in text_string):  # Simple coordinate text without ID
                        
                        # Update the text to include marker ID - use original coordinate text with 3 decimal precision
                        original_coord = f"({text_x:.3f},{text_y:.3f})"
                        new_text_string = f"{marker.id}:{original_coord}"
                        
                        # Mark for replacement
                        shapes_to_remove.append(shape)
                        new_text_obj = pya.Text(new_text_string, text_obj.trans)
                        shapes_to_add.append(new_text_obj)
                        
                        print(f"[FIB] Updated coordinate text: '{text_string}' -> '{new_text_string}'")
                        updated_count += 1
            
            # Apply changes
            for shape in shapes_to_remove:
                cell.shapes(coord_layer).erase(shape)
            
            for text_obj in shapes_to_add:
                cell.shapes(coord_layer).insert(text_obj)
        
        print(f"[FIB] Updated {updated_count} coordinate texts with marker ID {marker.id}")
                
    except Exception as e:
        print(f"[FIB] Error updating coordinate texts: {e}")
        import traceback
        traceback.print_exc()

# FIB Tool Plugin class
class FIBToolPlugin(pya.Plugin):
    """FIB Tool Plugin - Handles mouse events for marker creation"""
    
    def __init__(self, manager):
        super(FIBToolPlugin, self).__init__()
        self.manager = manager
        self.mode = None  # 'cut', 'connect', 'probe', 'cut_multi', 'connect_multi'
        self.temp_points = []
        self.is_multipoint_mode = False
        self.last_click_time = 0
        self.last_click_pos = None
        self.double_click_threshold = UI_TIMEOUTS['double_click']
        self.double_click_distance = GEOMETRIC_PARAMS['double_click_distance']
        print(f"[FIB Plugin] Initialized")
    
    def activated(self):
        """Called when plugin is activated"""
        global current_mode, active_plugin
        
        print(f"[FIB Plugin] Activated, mode: {self.mode}")
        
        # Set global state
        current_mode = self.mode
        active_plugin = self
        
        # Determine if this is a multi-point mode
        self.is_multipoint_mode = self.mode.endswith('_multi')
        
        try:
            if self.mode == 'cut':
                pya.MainWindow.instance().message("CUT mode: Click twice (position + direction)", UI_TIMEOUTS['message_long'])
            elif self.mode == 'cut_multi':
                pya.MainWindow.instance().message("CUT multi-point mode: Left-click to add points, right-click to finish", UI_TIMEOUTS['message_long'])
            elif self.mode == 'connect':
                pya.MainWindow.instance().message("CONNECT mode: Click twice (start + end)", UI_TIMEOUTS['message_long'])
            elif self.mode == 'connect_multi':
                pya.MainWindow.instance().message("CONNECT multi-point mode: Left-click to add points, right-click to finish", UI_TIMEOUTS['message_long'])
            elif self.mode == 'probe':
                pya.MainWindow.instance().message("PROBE mode: Click once", UI_TIMEOUTS['message_long'])
        except Exception as msg_error:
            print(f"[FIB Plugin] Message error in activated(): {msg_error}")
    
    def deactivated(self):
        """Called when plugin is deactivated"""
        global current_mode, active_plugin
        
        print(f"[FIB Plugin] Deactivated, mode: {self.mode}")
        
        # Clear global state only if this plugin was active
        if active_plugin == self:
            current_mode = None
            active_plugin = None
        
        # Reset all state
        self.temp_points = []
        self.last_click_time = 0
        self.last_click_pos = None
    
    def mouse_click_event(self, p, buttons, prio):
        """Handle mouse click events"""
        global current_mode, active_plugin
        
        # Check for right-click to finish multi-point mode
        if buttons & pya.ButtonState.RightButton:
            return self._handle_right_click_finish(p, buttons, prio)
        
        # Handle left-click
        if not (buttons & pya.ButtonState.LeftButton):
            return False
        
        # Determine which mode to use
        if current_mode:
            # Panel activation - use global mode, but only if this plugin matches
            base_mode = current_mode.replace('_multi', '')
            plugin_base_mode = self.mode.replace('_multi', '')
            if plugin_base_mode != base_mode:
                return False
            effective_mode = current_mode
        else:
            # Toolbar activation - use plugin's own mode
            if not prio or not self.mode:
                return False
            effective_mode = self.mode
        
        print(f"[FIB Plugin] Mouse click: plugin_mode={self.mode}, global_mode={current_mode}, effective_mode={effective_mode}, prio={prio}")
        
        # Use effective mode for this event
        working_mode = effective_mode
        
        # Get current view and cell
        view = pya.Application.instance().main_window().current_view()
        if not view or not view.active_cellview().is_valid():
            return False
        
        cellview = view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # p.x and p.y are already in the correct units (microns)
        x = p.x
        y = p.y
        

        
        # Detect layer at click position using layer tap functionality
        detected_layer = None
        if LAYER_TAP_AVAILABLE:
            try:
                point_label = f"Point {len(self.temp_points) + 1}"
                # Use default search radius from config (don't override it)
                detected_layer = get_layer_at_point_with_selection(x, y, position_label=point_label)
                if detected_layer:
                    layer_str = format_layer_for_display(detected_layer)
                    print(f"[DEBUG] Position ({x:.3f}, {y:.3f}) - Detected layer: {layer_str}")
                else:
                    print(f"[DEBUG] Position ({x:.3f}, {y:.3f}) - No layer detected (N/A)")
            except Exception as tap_error:
                print(f"[DEBUG] Layer tap error: {tap_error}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DEBUG] Position ({x:.3f}, {y:.3f}) - Layer tap not available")
        
        # Store the point with layer information
        point_info = {
            'x': x,
            'y': y,
            'layer': format_layer_for_display(detected_layer) if LAYER_TAP_AVAILABLE else None
        }
        self.temp_points.append(point_info)
        print(f"[DEBUG] Stored points: {len(self.temp_points)} total")
        
        # Add coordinate text at click position (will be updated with marker ID later)
        self._add_coordinate_text(view, x, y)
        
        # Handle different modes
        if working_mode == 'cut':
            if len(self.temp_points) == 2:
                print(f"[DEBUG] Creating CUT marker with points: {self.temp_points}")
                # Get layer info for each point
                layer1 = self.temp_points[0].get('layer')
                layer2 = self.temp_points[1].get('layer')
                marker = create_cut_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'], 
                    self.temp_points[1]['x'], self.temp_points[1]['y'],
                    layer1=layer1, layer2=layer2
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif working_mode == 'cut_multi':
            # Multi-point cut mode - collect points until right-click
            if len(self.temp_points) >= 2:
                try:
                    pya.MainWindow.instance().message(f"Cut path: {len(self.temp_points)} points. Right-click to finish.", UI_TIMEOUTS['message_medium'])
                except Exception:
                    pass  # Message display is non-critical
        elif working_mode == 'connect':
            if len(self.temp_points) == 2:
                # Get layer info for each point
                layer1 = self.temp_points[0].get('layer')
                layer2 = self.temp_points[1].get('layer')
                marker = create_connect_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'], 
                    self.temp_points[1]['x'], self.temp_points[1]['y'],
                    layer1=layer1, layer2=layer2
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif working_mode == 'connect_multi':
            # Multi-point connect mode - collect points until right-click
            if len(self.temp_points) >= 2:
                try:
                    pya.MainWindow.instance().message(f"Connect path: {len(self.temp_points)} points. Right-click to finish.", UI_TIMEOUTS['message_medium'])
                except Exception:
                    pass  # Message display is non-critical
        elif working_mode == 'probe':
            if len(self.temp_points) == 1:
                # Get layer info for probe point
                target_layer = self.temp_points[0].get('layer')
                marker = create_probe_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'],
                    target_layer=target_layer
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        return True
    
    def _handle_right_click_finish(self, p, buttons, prio):
        """Handle right-click to finish multi-point input"""
        global current_mode
        
        # Determine which mode to use
        if current_mode:
            base_mode = current_mode.replace('_multi', '')
            plugin_base_mode = self.mode.replace('_multi', '')
            if plugin_base_mode != base_mode:
                return False
            effective_mode = current_mode
        else:
            if not prio or not self.mode:
                return False
            effective_mode = self.mode
        
        print(f"[DEBUG] Right-click detected in mode: {effective_mode}")
        
        # Only handle right-click in multi-point modes
        if not effective_mode.endswith('_multi'):
            print(f"[DEBUG] Not in multi-point mode, ignoring right-click")
            return False
        
        # Get current view and cell
        view = pya.Application.instance().main_window().current_view()
        if not view or not view.active_cellview().is_valid():
            return False
        
        cellview = view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # Check if we have enough points
        if len(self.temp_points) < 2:
            print(f"[DEBUG] Not enough points: {len(self.temp_points)} < 2")
            try:
                pya.MainWindow.instance().message("Need at least 2 points. Continue clicking with left button.", UI_TIMEOUTS['message_medium'])
            except Exception:
                pass  # Message display is non-critical
            return True
        
        print(f"[DEBUG] Right-click: Finishing {effective_mode} with {len(self.temp_points)} points")
        print(f"[DEBUG] MULTIPOINT_AVAILABLE = {MULTIPOINT_AVAILABLE}")
        
        # Create multi-point marker
        if effective_mode == 'cut_multi':
            if MULTIPOINT_AVAILABLE:
                print(f"[DEBUG] Creating multi-point CUT marker...")
                self._create_multipoint_cut_marker(cell, layout)
            else:
                print(f"[DEBUG] ERROR: MULTIPOINT_AVAILABLE is False!")
        elif effective_mode == 'connect_multi':
            if MULTIPOINT_AVAILABLE:
                print(f"[DEBUG] Creating multi-point CONNECT marker...")
                self._create_multipoint_connect_marker(cell, layout)
            else:
                print(f"[DEBUG] ERROR: MULTIPOINT_AVAILABLE is False!")
        
        return True
    
    def _create_multipoint_cut_marker(self, cell, layout):
        """Create a multi-point cut marker"""
        try:
            print(f"[DEBUG] _create_multipoint_cut_marker called with {len(self.temp_points)} points")
            
            # Use smart counter to get next available number
            if PANEL_AVAILABLE:
                panel = get_fib_panel()
                if panel and hasattr(panel, 'smart_counter'):
                    next_number = panel.smart_counter.get_next_number('cut')
                else:
                    next_number = marker_counter['cut']
            else:
                next_number = marker_counter['cut']
            
            # Create marker ID
            marker_id = f"CUT_{next_number}"
            print(f"[DEBUG] Marker ID: {marker_id}")
            
            # Update global counter
            marker_counter['cut'] = max(marker_counter['cut'], next_number + 1)
            
            # Extract points and layer info for each point
            points = [(point['x'], point['y']) for point in self.temp_points]
            point_layers = [point.get('layer', 'N/A') for point in self.temp_points]
            
            print(f"[DEBUG] Points to create marker: {points}")
            print(f"[DEBUG] Point layers: {point_layers}")
            
            # Create multi-point marker with layer info
            marker = create_multipoint_cut_marker(marker_id, points, point_layers)
            print(f"[DEBUG] Marker object created: {marker}")
            
            # Draw marker
            draw_marker(marker, cell, layout)
            print(f"[DEBUG] Marker drawn to GDS")
            
            # Clear temp points
            self.temp_points = []
            
            print(f"[DEBUG] [OK] Successfully created multi-point cut marker {marker_id} with {len(points)} points")
            
        except Exception as e:
            print(f"[DEBUG] [X] Error creating multi-point cut marker: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_multipoint_connect_marker(self, cell, layout):
        """Create a multi-point connect marker"""
        try:
            # Use smart counter to get next available number
            if PANEL_AVAILABLE:
                panel = get_fib_panel()
                if panel and hasattr(panel, 'smart_counter'):
                    next_number = panel.smart_counter.get_next_number('connect')
                else:
                    next_number = marker_counter['connect']
            else:
                next_number = marker_counter['connect']
            
            # Create marker ID
            marker_id = f"CONNECT_{next_number}"
            
            # Update global counter
            marker_counter['connect'] = max(marker_counter['connect'], next_number + 1)
            
            # Extract points and layer info for each point
            points = [(point['x'], point['y']) for point in self.temp_points]
            point_layers = [point.get('layer', 'N/A') for point in self.temp_points]
            
            # Create multi-point marker with layer info
            marker = create_multipoint_connect_marker(marker_id, points, point_layers)
            
            # Draw marker
            draw_marker(marker, cell, layout)
            
            # Clear temp points
            self.temp_points = []
            
            print(f"[DEBUG] Created multi-point connect marker {marker_id} with {len(points)} points")
            
        except Exception as e:
            print(f"[DEBUG] Error creating multi-point connect marker: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_layers_at_position(self, view, point):
        """Use KLayout's tap functionality to find layers at the given position"""
        try:
            # Get the current cellview
            cellview = view.active_cellview()
            if not cellview.is_valid():
                print("[DEBUG] Invalid cellview")
                return []
            
            layout = cellview.layout()
            cell = cellview.cell
            
            # point.x and point.y are already in database units
            db_point = pya.Point(int(point.x), int(point.y))
            print(f"[DEBUG] Searching for layers at DB point: ({db_point.x}, {db_point.y})")
            
            # Try using KLayout's built-in selection functionality
            found_layers = []
            
            # Method 1: Use view's selection functionality
            try:
                # Create a small region around the point
                search_radius = 50  # database units
                search_region = pya.Region()
                search_box = pya.Box(db_point.x - search_radius, db_point.y - search_radius,
                                   db_point.x + search_radius, db_point.y + search_radius)
                search_region.insert(search_box)
                
                # Get all layer infos and check each one
                layer_infos = layout.layer_infos()
                print(f"[DEBUG] Checking {len(layer_infos)} layers")
                
                for layer_info in layer_infos:
                    layer_index = layout.layer(layer_info)
                    if layer_index < 0:
                        continue
                    
                    shapes = cell.shapes(layer_index)
                    if shapes.size() == 0:
                        continue
                    
                    print(f"[DEBUG] Layer {layer_info.layer}/{layer_info.datatype}: {shapes.size()} shapes")
                    
                    # Convert shapes to region and check intersection
                    layer_region = pya.Region(shapes)
                    if not layer_region.is_empty():
                        intersection = layer_region & search_region
                        if not intersection.is_empty():
                            layer_name = f"{layer_info.layer}/{layer_info.datatype}"
                            found_layers.append(layer_name)
                            print(f"[DEBUG] Found intersection on layer {layer_name}")
                
            except Exception as method1_error:
                print(f"[DEBUG] Method 1 failed: {method1_error}")
                
                # Method 2: Simple shape iteration
                layer_infos = layout.layer_infos()
                for layer_info in layer_infos:
                    try:
                        layer_index = layout.layer(layer_info)
                        if layer_index < 0:
                            continue
                        
                        shapes = cell.shapes(layer_index)
                        if shapes.size() == 0:
                            continue
                        
                        # Check each shape
                        for shape in shapes.each():
                            bbox = shape.bbox()
                            if bbox.contains(db_point):
                                layer_name = f"{layer_info.layer}/{layer_info.datatype}"
                                if layer_name not in found_layers:
                                    found_layers.append(layer_name)
                                    print(f"[DEBUG] Found shape on layer {layer_name} (bbox method)")
                                break
                    
                    except Exception as shape_error:
                        print(f"[DEBUG] Error checking shapes on layer {layer_info}: {shape_error}")
                        continue
            
            print(f"[DEBUG] Final layers found: {found_layers}")
            return found_layers
            
        except Exception as e:
            print(f"[DEBUG] Error in _get_layers_at_position: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _shape_contains_point(self, shape, point):
        """Check if a shape contains the given point"""
        try:
            # Use bounding box as the primary check (most reliable)
            bbox = shape.bbox()
            return bbox.contains(point)
        except Exception as e:
            print(f"[DEBUG] Error in _shape_contains_point: {e}")
            return False
    
    def _add_coordinate_text(self, view, x, y, marker_id=None):
        """Add coordinate text at the click position"""
        try:
            # Get current cellview
            cellview = view.active_cellview()
            if not cellview.is_valid():
                return
            
            cell = cellview.cell
            layout = cellview.layout()
            dbu = layout.dbu
            
            # x, y are in the correct units (likely microns), create display text
            # Use 3 decimal places for 0.001 precision
            if marker_id:
                coord_text = f"{marker_id}:({x:.3f},{y:.3f})"
            else:
                coord_text = f"({x:.3f},{y:.3f})"
            
            # For text placement, we need to convert to database units
            # If x, y are already in microns, divide by dbu
            # If x, y are in database units, use directly
            # Based on the coordinate values, they seem to be in microns, so divide by dbu
            text_x = int(x / dbu)
            text_y = int(y / dbu)
            
            print(f"[DEBUG] Text placement: x={x:.2f}um / dbu={dbu} = {text_x} DB units")
            
            # Create text object at the click position
            text_obj = pya.Text(coord_text, pya.Trans(pya.Point(text_x, text_y)))
            
            # Get or create coordinate text layer
            coord_layer_num = LAYERS['coordinates']
            coord_layer = get_or_create_layer(layout, coord_layer_num, 0, 'FIB_COORDINATES')
            
            # Insert text into the layout
            cell.shapes(coord_layer).insert(text_obj)
            
            print(f"[DEBUG] Added coordinate text '{coord_text}' at DB position ({text_x}, {text_y})")
            
        except Exception as e:
            print(f"[DEBUG] Error adding coordinate text: {e}")

# Plugin Factories for each mode
class FIBCutPluginFactory(pya.PluginFactory):
    """Factory for CUT mode plugin"""
    
    def __init__(self):
        super(FIBCutPluginFactory, self).__init__()
        self.register(-999, "fib_cut", "FIB Cut")
    
    def create_plugin(self, manager, root, view):
        global current_plugins
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'cut'
        # Store plugin instance for panel access
        current_plugins['cut'] = plugin
        return plugin

class FIBConnectPluginFactory(pya.PluginFactory):
    """Factory for CONNECT mode plugin"""
    
    def __init__(self):
        super(FIBConnectPluginFactory, self).__init__()
        self.register(-998, "fib_connect", "FIB Connect")
    
    def create_plugin(self, manager, root, view):
        global current_plugins
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'connect'
        # Store plugin instance for panel access
        current_plugins['connect'] = plugin
        return plugin

class FIBProbePluginFactory(pya.PluginFactory):
    """Factory for PROBE mode plugin"""
    
    def __init__(self):
        super(FIBProbePluginFactory, self).__init__()
        self.register(-997, "fib_probe", "FIB Probe")
    
    def create_plugin(self, manager, root, view):
        global current_plugins
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'probe'
        # Store plugin instance for panel access
        current_plugins['probe'] = plugin
        return plugin

# Create and register all plugin factories
# This will add buttons to the toolbar automatically
# Protected against double initialization

if not _FIB_PLUGIN_FACTORIES_CREATED:
    print("=== FIB Tool Initialization ===")
    
    # Check and create FIB layers if needed
    print("\n=== Layer Check ===")
    try:
        layer_check_result = ensure_fib_layers()
        if layer_check_result:
            print("[OK] FIB layers verified/created successfully")
            print(get_layer_info_summary())
        else:
            print("[!] Layer check completed with warnings (check console for details)")
    except Exception as layer_error:
        print(f"[!] Layer check error: {layer_error}")
        print("  Plugin will continue, but layers may need manual creation")
    
    print("\n=== Plugin Registration ===")
    try:
        # Create factory instances
        cut_factory = FIBCutPluginFactory()
        connect_factory = FIBConnectPluginFactory()
        probe_factory = FIBProbePluginFactory()
        
        # Store as class attributes to prevent garbage collection
        FIBCutPluginFactory.instance = cut_factory
        FIBConnectPluginFactory.instance = connect_factory
        FIBProbePluginFactory.instance = probe_factory
        
        print("[OK] Plugin factories created successfully")
        print("[OK] Three buttons added to toolbar: FIB Cut, FIB Connect, FIB Probe")
        print("[OK] Each button activates a different FIB marker mode")
        
        # Mark as created
        _FIB_PLUGIN_FACTORIES_CREATED = True
        
    except Exception as e:
        print(f"[X] Error initializing plugin factories: {e}")
else:
    print("[FIB Plugin] Factories already created, skipping initialization...")

# Print usage instructions
print("\n=== FIB Tool Usage ===")
print("Version: 3.0")
print("Layers: CUT=337, CONNECT=338, PROBE=339, COORDINATES=339")
print("Line width: 0.2um")
print("PROBE marker: Circle (radius: 0.5um)")
print()
print("=== How to Use ===")
print("1. Open a GDS file")
print("2. Click one of the FIB Tool buttons in the toolbar:")
print("   - FIB Cut: Create CUT markers")
print("   - FIB Connect: Create CONNECT markers")
print("   - FIB Probe: Create PROBE markers")
print("3. Click on the layout to create markers:")
print("   - CUT: Click twice (start + end points)")
print("   - CONNECT: Click twice (start + end)")
print("   - PROBE: Click once for each marker")
print("4. Each click will also add coordinate text at that position")
print("5. Click the same button again to deactivate the mode")
print()
print("=== Features ===")
print("- [OK] Fixed 0.2um line width for all markers")
print("- [OK] PROBE markers are circular (0.5um radius)")
print("- [OK] Markers use layers: 337 (CUT), 338 (CONNECT), 339 (PROBE)")
print("- [OK] Coordinate texts on layer 339 (same as PROBE)")
print("- [WIP] Automatic layer detection (under development)")
print("- [OK] Sequential marker naming (CUT_0, CONNECT_1, PROBE_2)")
print("- [OK] Coordinate text at each click position")
print("- [OK] Clear status messages for each mode")
print("- [OK] Detailed debug output in Macro Development console")
print()
print("=== Tips ===")
print("- Each mode stays active until you click the button again")
print("- Check Macro Development console for debug messages")
print("- Adjust view zoom to see markers clearly")
print("- Use Layer Panel to adjust marker visibility")
print()
print("FIB Tool loaded successfully! Use toolbar buttons or FIB Panel to get started.")

# Utility function to clear coordinate texts
def clear_coordinate_texts():
    """Clear all coordinate text labels from the layout"""
    try:
        # Get current view and cell
        view = pya.Application.instance().main_window().current_view()
        if not view or not view.active_cellview().is_valid():
            print("[DEBUG] No active layout found")
            return
        
        cellview = view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # Get or create coordinate layer, then clear it
        coord_layer = get_or_create_layer(layout, LAYERS['coordinates'], 0, 'FIB_COORDINATES')
        cell.shapes(coord_layer).clear()
        
        print("[DEBUG] Cleared all coordinate texts")
        pya.Application.instance().main_window().message("Coordinate texts cleared", UI_TIMEOUTS['message_short'])
        
    except Exception as e:
        print(f"[DEBUG] Error clearing coordinate texts: {e}")

# Add functions and variables to global namespace
sys.modules['__main__'].clear_coordinate_texts = clear_coordinate_texts
sys.modules['__main__'].marker_counter = marker_counter
sys.modules['__main__'].current_plugins = current_plugins

# Global function for panel to activate plugin modes
def activate_fib_mode(mode):
    """Activate FIB plugin mode from panel"""
    global active_plugin, current_mode
    
    print("=" * 80)
    print(f"[FIB Plugin] activate_fib_mode() called with mode='{mode}'")
    print("=" * 80)
    
    try:
        print(f"[FIB Plugin] Step 1: Getting main window and view...")
        
        # Get the main window and current view
        main_window = pya.Application.instance().main_window()
        current_view = main_window.current_view()
        
        print(f"[FIB Plugin] main_window: {main_window}")
        print(f"[FIB Plugin] current_view: {current_view}")
        
        if not current_view:
            print(f"[FIB Plugin] [X] No active layout view found")
            pya.MessageBox.warning("FIB Tool", "No active layout view found", pya.MessageBox.Ok)
            return False
        
        print(f"[FIB Plugin] [OK] Active view found")
        
        print(f"[FIB Plugin] Step 2: Clearing temp points from all plugins...")
        # Clear temp_points and double-click state from all plugins when switching modes
        for plugin_mode, plugin in current_plugins.items():
            if plugin and hasattr(plugin, 'temp_points'):
                plugin.temp_points = []
                plugin.last_click_time = 0
                plugin.last_click_pos = None
                print(f"[FIB Plugin]   Cleared {plugin_mode} plugin state")
        
        print(f"[FIB Plugin] Step 3: Setting global mode to '{mode}'")
        # Set global mode
        current_mode = mode
        
        # Get base mode for plugin lookup (remove _multi suffix)
        base_mode = mode.replace('_multi', '')
        print(f"[FIB Plugin] Base mode: '{base_mode}'")
        
        print(f"[FIB Plugin] Step 4: Getting or creating plugin for '{base_mode}'...")
        print(f"[FIB Plugin] current_plugins keys: {list(current_plugins.keys())}")
        print(f"[FIB Plugin] current_plugins['{base_mode}']: {current_plugins.get(base_mode, 'NOT FOUND')}")
        
        # Get or create the plugin for this base mode
        if base_mode in current_plugins and current_plugins[base_mode]:
            plugin = current_plugins[base_mode]
            print(f"[FIB Plugin] [OK] Using existing plugin: {plugin}")
        else:
            # Create a new plugin instance if needed
            print(f"[FIB Plugin] Creating new plugin instance...")
            plugin = FIBToolPlugin(None)
            plugin.mode = base_mode
            current_plugins[base_mode] = plugin
            print(f"[FIB Plugin] [OK] Created new plugin: {plugin}")
        
        # Set as active plugin
        active_plugin = plugin
        print(f"[FIB Plugin] [OK] Set active_plugin to: {active_plugin}")
        
        print(f"[FIB Plugin] Step 5: Showing activation message...")
        # Show activation message
        try:
            if mode == 'cut':
                pya.MainWindow.instance().message("CUT mode: Click twice (position + direction)", UI_TIMEOUTS['message_long'])
            elif mode == 'cut_multi':
                pya.MainWindow.instance().message("CUT multi-point mode: Left-click to add points, right-click to finish", UI_TIMEOUTS['message_long'])
            elif mode == 'connect':
                pya.MainWindow.instance().message("CONNECT mode: Click twice (start + end)", UI_TIMEOUTS['message_long'])
            elif mode == 'connect_multi':
                pya.MainWindow.instance().message("CONNECT multi-point mode: Left-click to add points, right-click to finish", UI_TIMEOUTS['message_long'])
            elif mode == 'probe':
                pya.MainWindow.instance().message("PROBE mode: Click once", UI_TIMEOUTS['message_long'])
            print(f"[FIB Plugin] [OK] Message displayed")
        except Exception as msg_error:
            print(f"[FIB Plugin] [!] Message error: {msg_error}")
        
        print(f"[FIB Plugin] [OK] SUCCESS: {mode} mode activated")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"[FIB Plugin] [X] ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return False

# Add to global namespace
sys.modules['__main__'].activate_fib_mode = activate_fib_mode

print("\n=== Additional Functions ===")
print("clear_coordinate_texts() - Clear all coordinate text labels (Layer 339)")

# Create FIB Panel (delayed import to avoid circular dependency)
print("\n=== FIB Panel Integration ===")
try:
    # Import here after activate_fib_mode is defined
    from .fib_panel import create_fib_panel
    panel = create_fib_panel()
    if panel:
        print("[OK] FIB Panel created and docked successfully")
        print("[OK] Panel includes: Project management, marker tree view, right-click menus")
        print("[OK] Panel buttons are connected to plugin system")
    else:
        print("[X] Failed to create FIB Panel")
except Exception as e:
    print(f"[X] FIB Panel error: {e}")
    import traceback
    traceback.print_exc()
    print("[OK] Plugin system still works without panel")
