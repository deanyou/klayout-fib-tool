#!/usr/bin/env python3
"""
FIB Tool Plugin - Mouse-based marker creation
This is the pure Python version extracted from fib_tool.lym

Run in KLayout Macro Development console:
    import sys; sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/src')
    exec(open('/Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py', encoding='utf-8').read())
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

# FIB Tool - Version 3.0
# This version uses KLayout's Plugin system for mouse handling

# Global marker counter
marker_counter = {
    'cut': 0,
    'connect': 0,
    'probe': 0
}

# Marker creation functions
def create_cut_marker(x1, y1, x2, y2, target_layers=None):
    """Create a CUT marker connecting two points"""
    global marker_counter
    
    print(f"[DEBUG] create_cut_marker called with: x1={x1}, y1={y1}, x2={x2}, y2={y2}, layers={target_layers}")
    
    # Create marker ID with layer information (if available)
    layer_suffix = ""
    if target_layers and len(target_layers) > 0:
        if len(target_layers) == 1:
            layer_suffix = f"_L{target_layers[0]}"
        else:
            layers_str = "_".join(target_layers[:2])
            layer_suffix = f"_L{layers_str}"
    
    marker_id = f"CUT_{marker_counter['cut']}{layer_suffix}"
    marker_counter['cut'] += 1
    
    marker = CutMarker(marker_id, x1, y1, x2, y2, 6)
    marker.target_layers = target_layers or []  # Store layer info in marker
    print(f"[DEBUG] Created marker: {marker_id} from ({x1}, {y1}) to ({x2}, {y2}) on layers {target_layers}")
    return marker

def create_connect_marker(x1, y1, x2, y2, target_layers=None):
    """Create a CONNECT marker"""
    global marker_counter
    
    # Create marker ID with layer information
    layer_suffix = ""
    if target_layers and len(target_layers) > 0:
        if len(target_layers) == 1:
            layer_suffix = f"_L{target_layers[0]}"
        else:
            layers_str = "_".join(target_layers[:2])
            layer_suffix = f"_L{layers_str}"
    
    marker_id = f"CONNECT_{marker_counter['connect']}{layer_suffix}"
    marker_counter['connect'] += 1
    
    marker = ConnectMarker(marker_id, x1, y1, x2, y2, 6)
    marker.target_layers = target_layers or []
    return marker

def create_probe_marker(x, y, target_layers=None):
    """Create a PROBE marker"""
    global marker_counter
    
    # Create marker ID with layer information
    layer_suffix = ""
    if target_layers and len(target_layers) > 0:
        if len(target_layers) == 1:
            layer_suffix = f"_L{target_layers[0]}"
        else:
            layers_str = "_".join(target_layers[:2])
            layer_suffix = f"_L{layers_str}"
    
    marker_id = f"PROBE_{marker_counter['probe']}{layer_suffix}"
    marker_counter['probe'] += 1
    
    marker = ProbeMarker(marker_id, x, y, 6)
    marker.target_layers = target_layers or []
    return marker

# Drawing function
def draw_marker(marker, cell, layout):
    """Draw marker to GDS and show message"""
    # Get FIB layer based on marker type
    marker_type = marker.__class__.__name__.lower().replace('marker', '')
    fib_layer = layout.layer(LAYERS[marker_type], 0)
    
    # Draw marker
    marker.to_gds(cell, fib_layer)
    
    # Show message
    pya.MainWindow.instance().message(f"Created {marker.id}", 2000)
    print(f"[FIB] Created {marker.id}")
    return True

# FIB Tool Plugin class
class FIBToolPlugin(pya.Plugin):
    """FIB Tool Plugin - Handles mouse events for marker creation"""
    
    def __init__(self, manager):
        super(FIBToolPlugin, self).__init__()
        self.manager = manager
        self.mode = None  # 'cut', 'connect', 'probe'
        self.temp_points = []
        print(f"[FIB Plugin] Initialized")
    
    def activated(self):
        """Called when plugin is activated"""
        print(f"[FIB Plugin] Activated, mode: {self.mode}")
        
        if self.mode == 'cut':
            pya.MainWindow.instance().message("CUT mode: Click twice (position + direction)", 10000)
        elif self.mode == 'connect':
            pya.MainWindow.instance().message("CONNECT mode: Click twice (start + end)", 10000)
        elif self.mode == 'probe':
            pya.MainWindow.instance().message("PROBE mode: Click once", 10000)
    
    def deactivated(self):
        """Called when plugin is deactivated"""
        print(f"[FIB Plugin] Deactivated, mode: {self.mode}")
        self.mode = None
        self.temp_points = []
    
    def mouse_click_event(self, p, buttons, prio):
        """Handle mouse click events"""
        print(f"[FIB Plugin] Mouse click: p={p}, buttons={buttons}, prio={prio}, mode={self.mode}, points={self.temp_points}")
        
        if not prio or self.mode is None:
            return False
        
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
        
        # TODO: Tap functionality to find layers at this position
        # Currently disabled for debugging - will implement proper tap detection later
        target_layers = []  # Temporarily disabled
        # target_layers = self._get_layers_at_position(view, p)
        print(f"[DEBUG] Position ({x:.3f}, {y:.3f}) - Tap detection temporarily disabled")
        
        # Store the point with layer information
        point_info = {
            'x': x,
            'y': y,
            'layers': target_layers
        }
        self.temp_points.append(point_info)
        print(f"[DEBUG] Stored points: {self.temp_points}")
        
        # Add coordinate text at click position
        self._add_coordinate_text(view, x, y)
        
        # Handle different modes
        if self.mode == 'cut':
            if len(self.temp_points) == 2:
                print(f"[DEBUG] Creating CUT marker with points: {self.temp_points}")
                # Use layers from first click point
                target_layer_info = self.temp_points[0]['layers']
                marker = create_cut_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'], 
                    self.temp_points[1]['x'], self.temp_points[1]['y'],
                    target_layer_info
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif self.mode == 'connect':
            if len(self.temp_points) == 2:
                target_layer_info = self.temp_points[0]['layers']
                marker = create_connect_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'], 
                    self.temp_points[1]['x'], self.temp_points[1]['y'],
                    target_layer_info
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif self.mode == 'probe':
            if len(self.temp_points) == 1:
                target_layer_info = self.temp_points[0]['layers']
                marker = create_probe_marker(
                    self.temp_points[0]['x'], self.temp_points[0]['y'],
                    target_layer_info
                )
                draw_marker(marker, cell, layout)
                self.temp_points = []
        
        return True
    
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
    
    def _add_coordinate_text(self, view, x, y):
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
            coord_text = f"({x:.2f},{y:.2f})"
            
            # For text placement, we need to convert to database units
            # If x, y are already in microns, divide by dbu
            # If x, y are in database units, use directly
            # Based on the coordinate values, they seem to be in microns, so divide by dbu
            text_x = int(x / dbu)
            text_y = int(y / dbu)
            
            print(f"[DEBUG] Text placement: x={x:.2f}μm / dbu={dbu} = {text_x} DB units")
            
            # Create text object at the click position
            text_obj = pya.Text(coord_text, pya.Trans(pya.Point(text_x, text_y)))
            
            # Get coordinate text layer
            coord_layer_num = LAYERS['coordinates']
            coord_layer = layout.layer(coord_layer_num, 0)
            
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
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'cut'
        return plugin

class FIBConnectPluginFactory(pya.PluginFactory):
    """Factory for CONNECT mode plugin"""
    
    def __init__(self):
        super(FIBConnectPluginFactory, self).__init__()
        self.register(-998, "fib_connect", "FIB Connect")
    
    def create_plugin(self, manager, root, view):
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'connect'
        return plugin

class FIBProbePluginFactory(pya.PluginFactory):
    """Factory for PROBE mode plugin"""
    
    def __init__(self):
        super(FIBProbePluginFactory, self).__init__()
        self.register(-997, "fib_probe", "FIB Probe")
    
    def create_plugin(self, manager, root, view):
        plugin = FIBToolPlugin(manager)
        plugin.mode = 'probe'
        return plugin

# Create and register all plugin factories
# This will add buttons to the toolbar automatically
print("=== FIB Tool Initialization ===")
try:
    # Create factory instances
    cut_factory = FIBCutPluginFactory()
    connect_factory = FIBConnectPluginFactory()
    probe_factory = FIBProbePluginFactory()
    
    # Store as class attributes to prevent garbage collection
    FIBCutPluginFactory.instance = cut_factory
    FIBConnectPluginFactory.instance = connect_factory
    FIBProbePluginFactory.instance = probe_factory
    
    print("✓ Plugin factories created successfully")
    print("✓ Three buttons added to toolbar: FIB Cut, FIB Connect, FIB Probe")
    print("✓ Each button activates a different FIB marker mode")
except Exception as e:
    print(f"✗ Error initializing plugin factories: {e}")

# Print usage instructions
print("\n=== FIB Tool Usage ===")
print("Version: 3.0")
print("Layers: CUT=317, CONNECT=318, PROBE=319, COORDINATES=319")
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
print("- ✓ Fixed 0.2um line width for all markers")
print("- ✓ PROBE markers are circular (0.5um radius)")
print("- ✓ Markers use layers: 317 (CUT), 318 (CONNECT), 319 (PROBE)")
print("- ✓ Coordinate texts on layer 319 (same as PROBE)")
print("- 🚧 Automatic layer detection (under development)")
print("- ✓ Sequential marker naming (CUT_0, CONNECT_1, PROBE_2)")
print("- ✓ Coordinate text at each click position")
print("- ✓ Clear status messages for each mode")
print("- ✓ Detailed debug output in Macro Development console")
print()
print("=== Tips ===")
print("- Each mode stays active until you click the button again")
print("- Check Macro Development console for debug messages")
print("- Adjust view zoom to see markers clearly")
print("- Use Layer Panel to adjust marker visibility")
print()
print("FIB Tool loaded successfully! Use toolbar buttons to get started.")

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
        
        # Clear coordinate layer
        coord_layer = layout.layer(LAYERS['coordinates'], 0)
        cell.shapes(coord_layer).clear()
        
        print("[DEBUG] Cleared all coordinate texts")
        pya.Application.instance().main_window().message("Coordinate texts cleared", 2000)
        
    except Exception as e:
        print(f"[DEBUG] Error clearing coordinate texts: {e}")

# Add function to global namespace
sys.modules['__main__'].clear_coordinate_texts = clear_coordinate_texts

print("\n=== Additional Functions ===")
print("clear_coordinate_texts() - Clear all coordinate text labels (Layer 319)")
