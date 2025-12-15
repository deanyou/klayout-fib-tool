#!/usr/bin/env python3
"""
Cleanup orphaned marker geometry and texts
"""

import sys
import os
import pya

# Add the current directory to Python path
script_dir = '/Users/dean/Documents/git/klayout-fib-tool/src'
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def cleanup_orphaned_markers():
    """Clean up marker geometry and texts that are no longer in the panel"""
    try:
        # Get FIB panel and current markers
        from fib_panel import get_fib_panel
        panel = get_fib_panel()
        
        if not panel:
            print("No FIB panel found")
            return False
        
        # Get current view and layout
        main_window = pya.Application.instance().main_window()
        current_view = main_window.current_view()
        
        if not current_view or not current_view.active_cellview().is_valid():
            print("No active layout found")
            return False
        
        cellview = current_view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # Get list of current marker IDs
        current_marker_ids = [marker.id for marker in panel.markers_list]
        print(f"Current markers in panel: {current_marker_ids}")
        
        # Find and delete orphaned texts
        orphaned_texts = 0
        
        for layer_info in layout.layer_infos():
            layer_index = layout.layer(layer_info)
            if layer_index < 0:
                continue
            
            shapes = cell.shapes(layer_index)
            shapes_to_remove = []
            
            for shape in shapes.each():
                if shape.is_text():
                    text_obj = shape.text
                    text_string = text_obj.string
                    
                    # Check if this text belongs to a marker that no longer exists
                    is_orphaned = False
                    
                    # Look for marker ID patterns in the text
                    for marker_type in ['CUT_', 'CONNECT_', 'PROBE_']:
                        if marker_type in text_string:
                            # Extract potential marker ID
                            parts = text_string.split(':')
                            if len(parts) > 0:
                                potential_id = parts[0]
                                if potential_id not in current_marker_ids:
                                    is_orphaned = True
                                    print(f"Found orphaned text: '{text_string}' (ID: {potential_id})")
                                    break
                    
                    if is_orphaned:
                        shapes_to_remove.append(shape)
            
            # Remove orphaned texts
            for shape in shapes_to_remove:
                shapes.erase(shape)
                orphaned_texts += 1
        
        print(f"✓ Cleaned up {orphaned_texts} orphaned texts")
        
        # Optionally clean up FIB layers (more aggressive)
        print("\nFIB Layer Cleanup (optional):")
        print("To clean ALL geometry on FIB layers, use: cleanup_all_fib_geometry()")
        
        if orphaned_texts > 0:
            pya.MessageBox.info("Cleanup", f"Cleaned up {orphaned_texts} orphaned texts", pya.MessageBox.Ok)
        else:
            pya.MessageBox.info("Cleanup", "No orphaned texts found", pya.MessageBox.Ok)
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_all_fib_geometry():
    """Clean up ALL geometry on FIB layers (aggressive cleanup)"""
    try:
        # Get current view and layout
        main_window = pya.Application.instance().main_window()
        current_view = main_window.current_view()
        
        if not current_view or not current_view.active_cellview().is_valid():
            print("No active layout found")
            return False
        
        cellview = current_view.active_cellview()
        cell = cellview.cell
        layout = cellview.layout()
        
        # Confirm aggressive cleanup
        result = pya.MessageBox.question(
            "Aggressive Cleanup",
            "This will delete ALL geometry on FIB layers (317, 318, 319).\n\nAre you sure?",
            pya.MessageBox.Yes | pya.MessageBox.No
        )
        
        if result != pya.MessageBox.Yes:
            return False
        
        from config import LAYERS
        
        total_deleted = 0
        for layer_name, layer_num in LAYERS.items():
            try:
                fib_layer = layout.layer(layer_num, 0)
                shapes = cell.shapes(fib_layer)
                count = shapes.size()
                shapes.clear()
                total_deleted += count
                print(f"Cleared layer {layer_num} ({layer_name}): {count} shapes")
            except Exception as layer_error:
                print(f"Error clearing layer {layer_num}: {layer_error}")
        
        print(f"✓ Aggressive cleanup completed: {total_deleted} shapes deleted")
        pya.MessageBox.info("Aggressive Cleanup", f"Deleted {total_deleted} shapes from FIB layers", pya.MessageBox.Ok)
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Cleanup Tools ===")
    print("cleanup_orphaned_markers()  # Clean orphaned texts")
    print("cleanup_all_fib_geometry()  # Clean ALL FIB geometry (aggressive)")
    
    # Run smart cleanup
    cleanup_orphaned_markers()