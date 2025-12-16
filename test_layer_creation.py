#!/usr/bin/env python3
"""
Test script to verify FIB layer auto-creation

Run this in KLayout's Macro Development console to test layer creation.
"""

import sys
import os

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import pya
from config import LAYERS
from layer_manager import check_and_create_layers, verify_layers_exist

def test_layer_creation():
    """Test FIB layer creation"""
    print("=" * 60)
    print("FIB LAYER CREATION TEST")
    print("=" * 60)
    
    # Get current view and layout
    main_window = pya.Application.instance().main_window()
    current_view = main_window.current_view()
    
    if not current_view:
        print("✗ No active view found. Please open a GDS file first.")
        return False
    
    cellview = current_view.active_cellview()
    if not cellview.is_valid():
        print("✗ No valid cellview found. Please open a GDS file first.")
        return False
    
    layout = cellview.layout()
    
    print(f"\nCurrent layout: {cellview.name}")
    print(f"Total layers before: {len(layout.layer_infos())}")
    
    # List existing layers
    print("\nExisting layers:")
    for layer_info in layout.layer_infos():
        print(f"  Layer {layer_info.layer}/{layer_info.datatype}: {layer_info.name}")
    
    # Check which FIB layers exist
    print("\n" + "=" * 60)
    print("CHECKING FIB LAYERS")
    print("=" * 60)
    
    fib_layers_before = {}
    for layer_key, layer_num in LAYERS.items():
        if layer_key == 'coordinates':
            continue
        
        exists = False
        for layer_info in layout.layer_infos():
            if layer_info.layer == layer_num and layer_info.datatype == 0:
                exists = True
                break
        
        fib_layers_before[layer_key] = exists
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {layer_key.upper():12s} (Layer {layer_num}/0): {status}")
    
    # Run layer creation
    print("\n" + "=" * 60)
    print("RUNNING LAYER CREATION")
    print("=" * 60)
    
    layer_status = check_and_create_layers(layout)
    
    print(f"\nTotal layers after: {len(layout.layer_infos())}")
    
    # Verify layers were created
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    verification = verify_layers_exist(layout)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_good = True
    for layer_key, layer_num in LAYERS.items():
        if layer_key == 'coordinates':
            continue
        
        before = fib_layers_before.get(layer_key, False)
        after = verification.get(layer_num, False)
        
        if before and after:
            status = "✓ Already existed"
        elif not before and after:
            status = "✓ Created successfully"
        elif not before and not after:
            status = "✗ FAILED to create"
            all_good = False
        else:
            status = "? Unknown state"
            all_good = False
        
        print(f"  {layer_key.upper():12s} (Layer {layer_num}/0): {status}")
    
    print("\n" + "=" * 60)
    if all_good:
        print("✓ ALL FIB LAYERS ARE READY")
    else:
        print("✗ SOME LAYERS FAILED - CHECK ERRORS ABOVE")
    print("=" * 60)
    
    return all_good

# Run the test
if __name__ == "__main__":
    test_layer_creation()
