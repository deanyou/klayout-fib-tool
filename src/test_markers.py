"""
Simple test script for markers

Run this in KLayout's Macro Development window to test marker creation.
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import pya
from markers import CutMarker, ConnectMarker, ProbeMarker
from storage import save_markers, load_markers
from config import LAYERS


def test_markers():
    """Test marker creation and serialization"""
    
    print("Testing FIB Tool Markers...")
    
    # Create test markers
    markers = [
        CutMarker("CUT_0", 100.0, 200.0, "down", 6),
        ConnectMarker("CONNECT_0", 150.0, 250.0, 180.0, 280.0, 6),
        ProbeMarker("PROBE_0", 300.0, 400.0, 6),
    ]
    
    # Test XML serialization
    print("\n1. Testing XML serialization...")
    for marker in markers:
        xml = marker.to_xml()
        print(f"  {marker.id}: {xml}")
    
    # Test save/load
    print("\n2. Testing save/load...")
    test_file = "/tmp/test_fib.xml"
    success = save_markers(markers, test_file, "test_lib", "test_cell")
    print(f"  Save: {'✓' if success else '✗'}")
    
    loaded_markers, lib, cell = load_markers(test_file)
    print(f"  Load: {'✓' if len(loaded_markers) == 3 else '✗'}")
    print(f"  Library: {lib}, Cell: {cell}")
    
    # Test GDS drawing (requires active layout)
    print("\n3. Testing GDS drawing...")
    view = pya.Application.instance().main_window().current_view()
    
    if view and view.active_cellview().is_valid():
        cellview = view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # Create FIB layers
        cut_layer = layout.layer(LAYERS['cut'], 0)
        connect_layer = layout.layer(LAYERS['connect'], 0)
        probe_layer = layout.layer(LAYERS['probe'], 0)
        
        # Draw markers
        markers[0].to_gds(cell, cut_layer)
        markers[1].to_gds(cell, connect_layer)
        markers[2].to_gds(cell, probe_layer)
        
        print("  GDS drawing: ✓")
        print("  Check layers 200-202 in your layout")
    else:
        print("  GDS drawing: ✗ (no active layout)")
    
    print("\nTest complete!")


if __name__ == "__main__":
    test_markers()
