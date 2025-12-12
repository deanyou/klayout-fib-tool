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
def create_cut_marker(x1, y1, x2, y2):
    """Create a CUT marker connecting two points"""
    global marker_counter
    
    print(f"[DEBUG] create_cut_marker called with: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    
    # Create marker with both points
    marker_id = f"CUT_{marker_counter['cut']}"
    marker_counter['cut'] += 1
    
    marker = CutMarker(marker_id, x1, y1, x2, y2, 6)
    print(f"[DEBUG] Created marker: {marker_id} from ({x1}, {y1}) to ({x2}, {y2})")
    return marker

def create_connect_marker(x1, y1, x2, y2):
    """Create a CONNECT marker"""
    global marker_counter
    
    marker_id = f"CONNECT_{marker_counter['connect']}"
    marker_counter['connect'] += 1
    
    marker = ConnectMarker(marker_id, x1, y1, x2, y2, 6)
    return marker

def create_probe_marker(x, y):
    """Create a PROBE marker"""
    global marker_counter
    
    marker_id = f"PROBE_{marker_counter['probe']}"
    marker_counter['probe'] += 1
    
    marker = ProbeMarker(marker_id, x, y, 6)
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
        
        # Test both interpretations
        print(f"[DEBUG] Raw point: p.x={p.x}, p.y={p.y}")
        print(f"[DEBUG] DBU: {layout.dbu}")
        
        # Method 1: Assume p.x/p.y are in database units
        x_method1 = p.x * layout.dbu
        y_method1 = p.y * layout.dbu
        print(f"[DEBUG] Method 1 (DB->microns): x={x_method1}, y={y_method1}")
        
        # Method 2: Assume p.x/p.y are already in microns
        x_method2 = p.x
        y_method2 = p.y
        print(f"[DEBUG] Method 2 (direct): x={x_method2}, y={y_method2}")
        
        # Use method 2 for now (assume p.x/p.y are already in correct units)
        x = x_method2
        y = y_method2
        
        # Store the point in microns
        self.temp_points.append((x, y))
        print(f"[DEBUG] Stored points (microns): {self.temp_points}")
        
        # Handle different modes
        if self.mode == 'cut':
            if len(self.temp_points) == 2:
                print(f"[DEBUG] Creating CUT marker with points: {self.temp_points}")
                marker = create_cut_marker(self.temp_points[0][0], self.temp_points[0][1], 
                                         self.temp_points[1][0], self.temp_points[1][1])
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif self.mode == 'connect':
            if len(self.temp_points) == 2:
                marker = create_connect_marker(self.temp_points[0][0], self.temp_points[0][1], 
                                            self.temp_points[1][0], self.temp_points[1][1])
                draw_marker(marker, cell, layout)
                self.temp_points = []
        elif self.mode == 'probe':
            if len(self.temp_points) == 1:
                marker = create_probe_marker(self.temp_points[0][0], self.temp_points[0][1])
                draw_marker(marker, cell, layout)
                self.temp_points = []
        
        return True

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
print("Layers: CUT=317, CONNECT=318, PROBE=319")
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
print("   - CUT: Click twice (position + direction)")
print("   - CONNECT: Click twice (start + end)")
print("   - PROBE: Click once for each marker")
print("4. Click the same button again to deactivate the mode")
print()
print("=== Features ===")
print("- ✓ Fixed 0.2um line width for all markers")
print("- ✓ PROBE markers are circular (0.5um radius)")
print("- ✓ Markers use layers: 317 (CUT), 318 (CONNECT), 319 (PROBE)")
print("- ✓ Clear status messages for each mode")
print("- ✓ Detailed debug output in Macro Development console")
print("- ✓ Easy-to-use toolbar buttons")
print()
print("=== Tips ===")
print("- Each mode stays active until you click the button again")
print("- Check Macro Development console for debug messages")
print("- Adjust view zoom to see markers clearly")
print("- Use Layer Panel to adjust marker visibility")
print()
print("FIB Tool loaded successfully! Use toolbar buttons to get started.")
