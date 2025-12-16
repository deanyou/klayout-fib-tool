#!/usr/bin/env python3
"""
Layer Manager for FIB Tool

Automatically detects and creates required layers if they don't exist.
"""

import pya
from config import LAYERS


def check_and_create_layers(layout):
    """
    Check if FIB layers exist in the layout, create them if they don't.
    
    Args:
        layout: pya.Layout object
    
    Returns:
        dict: Status of each layer (existed or created)
    """
    layer_status = {}
    
    try:
        print("[Layer Manager] Checking FIB layers...")
        print(f"[Layer Manager] Layout has {len(layout.layer_infos())} existing layers")
        
        # Layer names for better identification
        layer_names = {
            'cut': 'FIB_CUT',
            'connect': 'FIB_CONNECT',
            'probe': 'FIB_PROBE',
            'coordinates': 'FIB_COORDINATES'
        }
        
        for layer_key, layer_num in LAYERS.items():
            # Skip duplicate check for coordinates (same as probe)
            if layer_key == 'coordinates':
                continue
            
            layer_name = layer_names.get(layer_key, f'FIB_{layer_key.upper()}')
            
            # Check if layer exists by searching through existing layers
            layer_exists = False
            existing_layer_index = -1
            
            # Method 1: Check if layer number already exists
            for layer_info in layout.layer_infos():
                if layer_info.layer == layer_num and layer_info.datatype == 0:
                    layer_exists = True
                    existing_layer_index = layout.layer(layer_info)
                    print(f"[Layer Manager] ✓ Layer {layer_num}/0 already exists (name: {layer_info.name})")
                    layer_status[layer_key] = 'existed'
                    break
            
            # If layer doesn't exist, create it
            if not layer_exists:
                try:
                    # Create new layer info
                    new_layer_info = pya.LayerInfo(layer_num, 0, layer_name)
                    
                    # Insert the layer into the layout
                    new_layer_index = layout.insert_layer(new_layer_info)
                    
                    layer_status[layer_key] = 'created'
                    print(f"[Layer Manager] ✓ Created layer {layer_num}/0 ({layer_name}) with index {new_layer_index}")
                    
                except Exception as create_error:
                    print(f"[Layer Manager] ✗ Failed to create layer {layer_num}/0: {create_error}")
                    layer_status[layer_key] = 'failed'
        
        print(f"[Layer Manager] Layer check complete: {len(layer_status)} layers verified")
        return layer_status
        
    except Exception as e:
        print(f"[Layer Manager] Error checking/creating layers: {e}")
        import traceback
        traceback.print_exc()
        return {}


def ensure_fib_layers():
    """
    Ensure FIB layers exist in the current layout.
    Called when the plugin is loaded or when a new layout is opened.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current view and layout
        main_window = pya.Application.instance().main_window()
        current_view = main_window.current_view()
        
        if not current_view:
            print("[Layer Manager] No active view found")
            return False
        
        cellview = current_view.active_cellview()
        if not cellview.is_valid():
            print("[Layer Manager] No valid cellview found")
            return False
        
        layout = cellview.layout()
        
        # Check and create layers
        layer_status = check_and_create_layers(layout)
        
        # Verify that layers were actually created
        verification = verify_layers_exist(layout)
        
        # Show summary message
        created_count = sum(1 for status in layer_status.values() if status == 'created')
        existed_count = sum(1 for status in layer_status.values() if status == 'existed')
        failed_count = sum(1 for status in layer_status.values() if status == 'failed')
        
        # Check verification results
        missing_layers = [num for num, exists in verification.items() if not exists]
        
        if missing_layers:
            print(f"[Layer Manager] ⚠ WARNING: {len(missing_layers)} layer(s) still missing after creation attempt: {missing_layers}")
        
        if created_count > 0:
            message = f"FIB Tool: Created {created_count} new layer(s), {existed_count} layer(s) already existed"
            if failed_count > 0:
                message += f", {failed_count} failed"
            print(f"[Layer Manager] {message}")
            try:
                pya.MainWindow.instance().message(message, 3000)
            except:
                pass
        else:
            print(f"[Layer Manager] All {existed_count} FIB layers already exist")
        
        return len(missing_layers) == 0
        
    except Exception as e:
        print(f"[Layer Manager] Error in ensure_fib_layers: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_layer_info_summary():
    """
    Get a summary of FIB layer information.
    
    Returns:
        str: Formatted summary of layer information
    """
    try:
        summary = "FIB Tool Layers:\n"
        summary += "-" * 40 + "\n"
        
        layer_names = {
            'cut': 'FIB_CUT',
            'connect': 'FIB_CONNECT',
            'probe': 'FIB_PROBE',
        }
        
        for layer_key, layer_num in LAYERS.items():
            if layer_key == 'coordinates':
                continue
            layer_name = layer_names.get(layer_key, layer_key.upper())
            summary += f"  {layer_name:20s} : Layer {layer_num}/0\n"
        
        summary += "-" * 40
        return summary
        
    except Exception as e:
        return f"Error getting layer info: {e}"


def verify_layers_exist(layout):
    """
    Verify that all FIB layers actually exist in the layout.
    
    Args:
        layout: pya.Layout object
    
    Returns:
        dict: Layer number -> exists (bool)
    """
    verification = {}
    
    try:
        print("[Layer Manager] Verifying layer existence...")
        
        for layer_key, layer_num in LAYERS.items():
            if layer_key == 'coordinates':
                continue
            
            # Check if we can get a valid layer index
            found = False
            for layer_info in layout.layer_infos():
                if layer_info.layer == layer_num and layer_info.datatype == 0:
                    found = True
                    layer_index = layout.layer(layer_info)
                    print(f"[Layer Manager]   Layer {layer_num}/0: EXISTS (index={layer_index}, name={layer_info.name})")
                    break
            
            if not found:
                print(f"[Layer Manager]   Layer {layer_num}/0: NOT FOUND")
            
            verification[layer_num] = found
        
        return verification
        
    except Exception as e:
        print(f"[Layer Manager] Error verifying layers: {e}")
        return {}


# Auto-check layers when module is imported
if __name__ != "__main__":
    # Only auto-check if we're being imported (not run as script)
    try:
        # Delay the check slightly to ensure KLayout is fully initialized
        import sys
        if 'pya' in sys.modules:
            # We're in KLayout environment
            pass  # Don't auto-check on import, let the plugin call it explicitly
    except:
        pass
