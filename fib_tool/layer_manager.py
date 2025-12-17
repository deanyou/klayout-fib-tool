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


def insert_fib_layer_views_to_panel(current_view, layout):
    """
    Insert FIB layer views into Layer Panel using KLayout's proper Layer Views API.
    
    This is the correct way according to KLayout documentation.
    """
    try:
        print("[Layer Manager] Inserting FIB layer views to Layer Panel...")
        
        # FIB layer definitions with colors
        fib_layers = {
            317: {'name': 'FIB_CUT', 'color': 0xFF0000},      # Red
            318: {'name': 'FIB_CONNECT', 'color': 0x00FF00},  # Green  
            319: {'name': 'FIB_PROBE', 'color': 0x0000FF}     # Blue
        }
        
        # Try to get layer list from view
        layer_list = None
        
        # Method 1: Try as property
        if hasattr(current_view, 'layer_list'):
            try:
                layer_list = current_view.layer_list
                print("[Layer Manager] ✓ Got layer_list as property")
            except Exception as prop_error:
                print(f"[Layer Manager] layer_list property failed: {prop_error}")
        
        # Method 2: Try as method
        if not layer_list and hasattr(current_view, 'layer_list'):
            try:
                layer_list = current_view.layer_list()
                print("[Layer Manager] ✓ Got layer_list as method")
            except Exception as method_error:
                print(f"[Layer Manager] layer_list() method failed: {method_error}")
        
        if not layer_list:
            print("[Layer Manager] ✗ Could not access layer list - using fallback")
            return False
        
        # Check existing layers
        existing_layers = set()
        try:
            count = layer_list.count() if hasattr(layer_list, 'count') else 0
            print(f"[Layer Manager] Current layer list has {count} entries")
            
            for i in range(count):
                try:
                    layer_props = layer_list.layer_props(i)
                    if (layer_props.source_layer in fib_layers and 
                        layer_props.source_datatype == 0):
                        existing_layers.add(layer_props.source_layer)
                        print(f"[Layer Manager] Layer {layer_props.source_layer}/0 already exists")
                except:
                    continue
                    
        except Exception as check_error:
            print(f"[Layer Manager] Error checking existing layers: {check_error}")
        
        # Insert missing FIB layers
        layers_added = 0
        
        for layer_num, layer_info in fib_layers.items():
            if layer_num not in existing_layers:
                try:
                    # Create layer properties
                    layer_props = pya.LayerProperties()
                    layer_props.source_layer = layer_num
                    layer_props.source_datatype = 0
                    layer_props.name = layer_info['name']
                    
                    # Set visual properties
                    layer_props.fill_color = layer_info['color']
                    layer_props.frame_color = layer_info['color']
                    layer_props.dither_pattern = 0  # Solid fill
                    layer_props.line_style = 0      # Solid line
                    layer_props.width = 1           # Line width
                    layer_props.marked = True       # Visible
                    layer_props.valid = True        # Valid
                    layer_props.visible = True      # Visible
                    
                    # Insert layer view
                    if hasattr(layer_list, 'insert_layer'):
                        layer_list.insert_layer(layer_props)
                        print(f"[Layer Manager] ✓ Inserted layer view: {layer_info['name']} (Layer {layer_num}/0)")
                        layers_added += 1
                    else:
                        print(f"[Layer Manager] ✗ layer_list has no insert_layer method")
                        return False
                        
                except Exception as insert_error:
                    print(f"[Layer Manager] ✗ Failed to insert layer {layer_num}: {insert_error}")
        
        print(f"[Layer Manager] Layer views insertion complete: {layers_added} new views added")
        return layers_added > 0 or len(existing_layers) > 0
        
    except Exception as e:
        print(f"[Layer Manager] Error in insert_fib_layer_views_to_panel: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_layers_to_layer_panel(current_view, layout):
    """
    Add FIB layers to the Layer Panel so they are visible in the UI.
    
    Args:
        current_view: Current layout view
        layout: Layout object
    """
    try:
        print("[Layer Manager] Adding layers to Layer Panel...")
        
        # In KLayout, we need to access the layer list through different methods
        # Let's try multiple approaches to find the correct API
        
        layer_names = {
            'cut': 'FIB_CUT',
            'connect': 'FIB_CONNECT', 
            'probe': 'FIB_PROBE',
            'coordinates': 'FIB_COORDINATES'
        }
        
        # Method 1: Try to get layer properties from the view
        try:
            # Check if view has layer properties methods
            if hasattr(current_view, 'get_layer_properties'):
                print("[Layer Manager] Using get_layer_properties method")
                # This method might exist in some KLayout versions
                pass
            elif hasattr(current_view, 'layer_properties'):
                print("[Layer Manager] Using layer_properties method")
                # This method might exist in some KLayout versions
                pass
            else:
                print("[Layer Manager] No direct layer properties access found")
        except Exception as method_error:
            print(f"[Layer Manager] Method check error: {method_error}")
        
        # Method 2: Try to add layers by creating shapes on them
        # This will force KLayout to recognize the layers
        print("[Layer Manager] Creating placeholder shapes to register layers...")
        
        cellview = current_view.active_cellview()
        if cellview.is_valid():
            cell = cellview.cell
            
            for layer_key, layer_num in LAYERS.items():
                if layer_key == 'coordinates':
                    continue
                    
                layer_name = layer_names.get(layer_key, f'FIB_{layer_key.upper()}')
                
                # Get or create the layer index
                layer_info = pya.LayerInfo(layer_num, 0, layer_name)
                layer_index = layout.layer(layer_info)
                
                # Create a tiny invisible shape to register the layer
                # This forces KLayout to add the layer to the layer panel
                shapes = cell.shapes(layer_index)
                
                # Create a very small box at origin that won't interfere with real data
                tiny_box = pya.Box(0, 0, 1, 1)  # 1 DBU x 1 DBU box
                shapes.insert(tiny_box)
                
                print(f"[Layer Manager] ✓ Registered layer {layer_num}/0 ({layer_name}) with placeholder shape")
        
        # Method 3: Try to refresh the view to update layer panel
        try:
            if hasattr(current_view, 'update_content'):
                current_view.update_content()
                print("[Layer Manager] Updated view content")
            elif hasattr(current_view, 'refresh'):
                current_view.refresh()
                print("[Layer Manager] Refreshed view")
        except Exception as refresh_error:
            print(f"[Layer Manager] Refresh error: {refresh_error}")
        
        print("[Layer Manager] Layer Panel registration complete")
        print("[Layer Manager] Note: Layers should now appear in the Layer Panel")
        print("[Layer Manager] If layers don't appear, try: View -> Redraw or F5")
        
    except Exception as e:
        print(f"[Layer Manager] Error adding layers to Layer Panel: {e}")
        import traceback
        traceback.print_exc()


def create_practical_layer_markers(current_view, layout):
    """
    Create practical, visible markers to ensure FIB layers appear in Layer Panel.
    
    This is a reliable fallback when Layer Views API is not available.
    """
    try:
        print("[Layer Manager] Creating practical layer markers...")
        
        cellview = current_view.active_cellview()
        if not cellview.is_valid():
            print("[Layer Manager] No valid cellview for marker creation")
            return
        
        cell = cellview.cell
        
        # FIB layer definitions with better visibility
        fib_layers = {
            317: {'name': 'FIB_CUT', 'description': 'FIB cutting paths'},
            318: {'name': 'FIB_CONNECT', 'description': 'FIB connection paths'},
            319: {'name': 'FIB_PROBE', 'description': 'FIB probe points'}
        }
        
        # Create visible markers spread horizontally
        for layer_key, layer_num in LAYERS.items():
            if layer_key == 'coordinates':
                continue
                
            layer_info = fib_layers.get(layer_num, {'name': f'FIB_{layer_key.upper()}', 'description': f'FIB {layer_key} layer'})
            
            # Create layer with descriptive name
            layer_info_obj = pya.LayerInfo(layer_num, 0, layer_info['name'])
            layer_index = layout.layer(layer_info_obj)
            shapes = cell.shapes(layer_index)
            
            # Calculate marker position (X from 0 onwards, Y below 0)
            marker_x = (layer_num - 317) * 5000  # X: 0, 5000, 10000 (0μm, 5μm, 10μm)
            marker_y = -5000  # Y: -5μm (below 0)
            
            # Create a visible marker box (2μm x 2μm)
            marker_size = 2000  # 2μm
            marker_box = pya.Box(marker_x, marker_y, marker_x + marker_size, marker_y + marker_size)
            shapes.insert(marker_box)
            
            # Create descriptive text (place text below the marker)
            text_content = f"{layer_info['name']}\nLayer {layer_num}\n{layer_info['description']}"
            text_obj = pya.Text(text_content, marker_x, marker_y - 1500)  # Text 1.5μm below marker
            text_obj.size = 300  # Readable size
            shapes.insert(text_obj)
            
            print(f"[Layer Manager] ✓ Created practical marker for {layer_info['name']} at ({marker_x/1000:.1f}, {marker_y/1000:.1f})")
        
        # Force refresh
        try:
            current_view.zoom_fit()
            main_window = pya.Application.instance().main_window()
            main_window.redraw()
        except:
            pass
        
        print("[Layer Manager] Practical layer markers created")
        print("[Layer Manager] Markers are visible at coordinates (0,0), (5,0), (10,0)")
        print("[Layer Manager] If layers don't appear in Layer Panel, try View → Redraw (F5)")
        
    except Exception as e:
        print(f"[Layer Manager] Error creating practical markers: {e}")
        import traceback
        traceback.print_exc()


def create_layer_identification_markers(current_view, layout):
    """
    Create identification markers on FIB layers to ensure they appear in Layer Panel.
    
    This is the most reliable way to make layers visible in KLayout's Layer Panel.
    """
    try:
        print("[Layer Manager] Creating layer identification markers...")
        
        cellview = current_view.active_cellview()
        if not cellview.is_valid():
            print("[Layer Manager] No valid cellview for marker creation")
            return
        
        cell = cellview.cell
        
        layer_names = {
            'cut': 'FIB_CUT',
            'connect': 'FIB_CONNECT', 
            'probe': 'FIB_PROBE'
        }
        
        # Create small text markers (X from 0 onwards, Y below 0)
        for layer_key, layer_num in LAYERS.items():
            if layer_key == 'coordinates':
                continue
                
            layer_name = layer_names.get(layer_key, f'FIB_{layer_key.upper()}')
            
            # Calculate marker position (X from 0 onwards, Y below 0)
            marker_x = (layer_num - 317) * 3000  # X: 0, 3000, 6000 (0μm, 3μm, 6μm)
            marker_y = -8000  # Y: -8μm (below the main markers)
            
            # Get the layer index
            layer_info = pya.LayerInfo(layer_num, 0, layer_name)
            layer_index = layout.layer(layer_info)
            
            # Create shapes collection for this layer
            shapes = cell.shapes(layer_index)
            
            # Create a small identification text
            text_string = f"FIB_{layer_key.upper()}_LAYER"
            text_obj = pya.Text(text_string, marker_x, marker_y)
            text_obj.size = 200  # Readable size
            
            # Insert the text
            shapes.insert(text_obj)
            
            print(f"[Layer Manager] ✓ Created identification marker for layer {layer_num}/0 ({layer_name}) at ({marker_x/1000:.1f}, {marker_y/1000:.1f})")
        
        # Force layer panel refresh by triggering a layout change event
        force_layer_panel_refresh(current_view, layout)
        
        print("[Layer Manager] Layer identification markers created")
        print("[Layer Manager] Note: Small text markers created at (-1000, -1000) area")
        print("[Layer Manager] These markers ensure layers appear in Layer Panel")
        
    except Exception as e:
        print(f"[Layer Manager] Error creating identification markers: {e}")
        import traceback
        traceback.print_exc()


def force_layer_panel_refresh(current_view, layout):
    """
    Force Layer Panel to refresh using safe, reliable methods.
    
    This focuses on the most reliable refresh methods to avoid Qt binding issues.
    """
    try:
        print("[Layer Manager] Forcing Layer Panel refresh (safe mode)...")
        
        # Get main window
        main_window = pya.Application.instance().main_window()
        
        # Method 1: Basic refresh operations (most reliable)
        safe_refresh_methods = [
            ('zoom_fit', lambda: current_view.zoom_fit()),
            ('clear_selection', lambda: current_view.clear_selection()),
            ('main_window.redraw', lambda: main_window.redraw()),
        ]
        
        for method_name, method_func in safe_refresh_methods:
            try:
                method_func()
                print(f"[Layer Manager] ✓ {method_name}() succeeded")
            except Exception as method_error:
                print(f"[Layer Manager] ✗ {method_name}() failed: {method_error}")
        
        # Method 2: Advanced refresh (if available)
        advanced_refresh_methods = [
            ('current_view.update_content', lambda: getattr(current_view, 'update_content', lambda: None)()),
            ('current_view.refresh', lambda: getattr(current_view, 'refresh', lambda: None)()),
            ('main_window.update', lambda: getattr(main_window, 'update', lambda: None)()),
        ]
        
        for method_name, method_func in advanced_refresh_methods:
            try:
                method_func()
                print(f"[Layer Manager] ○ {method_name}() called")
            except Exception as method_error:
                print(f"[Layer Manager] ✗ {method_name}() failed: {method_error}")
        
        # Method 3: Force layer recognition with temporary geometry
        try:
            cellview = current_view.active_cellview()
            if cellview.is_valid():
                cell = cellview.cell
                
                # Create a temporary shape on each FIB layer to force recognition
                from config import LAYERS
                for layer_key, layer_num in LAYERS.items():
                    if layer_key == 'coordinates':
                        continue
                    
                    layer_info = pya.LayerInfo(layer_num, 0, f'FIB_{layer_key.upper()}')
                    layer_index = layout.layer(layer_info)
                    shapes = cell.shapes(layer_index)
                    
                    # Create and immediately delete a tiny shape
                    temp_box = pya.Box(0, 0, 1, 1)
                    temp_shape = shapes.insert(temp_box)
                    shapes.erase(temp_shape)
                
                print("[Layer Manager] ✓ Forced layer recognition with temporary shapes")
                
        except Exception as temp_error:
            print(f"[Layer Manager] Temporary shape method failed: {temp_error}")
        
        # Method 4: Final redraw
        try:
            main_window.redraw()
            print("[Layer Manager] ✓ Final redraw completed")
        except Exception as final_error:
            print(f"[Layer Manager] Final redraw failed: {final_error}")
        
        print("[Layer Manager] Safe refresh completed")
        
    except Exception as e:
        print(f"[Layer Manager] Error in force_layer_panel_refresh: {e}")
        import traceback
        traceback.print_exc()


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
        
        # Try Layer Views API first
        success = insert_fib_layer_views_to_panel(current_view, layout)
        
        if not success:
            print("[Layer Manager] Layer Views API not available, using practical solution")
            # Fallback: Create visible markers to ensure layer recognition
            create_practical_layer_markers(current_view, layout)
        
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


def test_layer_creation():
    """
    Test function to verify layer creation works correctly.
    Run this in KLayout's Macro Development console.
    """
    try:
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
        print("\nExisting layers in layout:")
        for layer_info in layout.layer_infos():
            print(f"  Layer {layer_info.layer}/{layer_info.datatype}: {layer_info.name}")
        
        # Note: Layer Panel access is limited in KLayout's Python API
        print(f"\nNote: Layer Panel contents cannot be easily queried via Python API")
        
        # Run layer creation
        print("\n" + "=" * 60)
        print("RUNNING LAYER CREATION")
        print("=" * 60)
        
        success = ensure_fib_layers()
        
        print(f"\nTotal layers after: {len(layout.layer_infos())}")
        print(f"Note: Check the Layer Panel manually to see if FIB layers appeared")
        
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
            
            exists = verification.get(layer_num, False)
            status = "✓ EXISTS" if exists else "✗ MISSING"
            print(f"  {layer_key.upper():12s} (Layer {layer_num}/0): {status}")
            
            if not exists:
                all_good = False
        
        print("\n" + "=" * 60)
        if all_good:
            print("✓ ALL FIB LAYERS ARE READY")
            print("✓ Check the Layer Panel - FIB layers should be visible")
        else:
            print("✗ SOME LAYERS FAILED - CHECK ERRORS ABOVE")
        print("=" * 60)
        
        return all_good
        
    except Exception as e:
        print(f"✗ ERROR in test: {e}")
        import traceback
        traceback.print_exc()
        return False


# Convenience function for manual testing
def test():
    """Shortcut function for testing"""
    return test_layer_creation()