#!/usr/bin/env python3
"""
Layer Tap - Detect layers at click position

This module provides functionality to detect which layers contain shapes
at a given coordinate position, similar to KLayout's tap functionality.

Strategy:
- Single layer at position: Use that layer directly
- Multiple layers overlapping: Use the layer selected in Layer Panel
- No layer found: Return None (displays as "N/A")
"""

import pya
from .config import LAYERS, GEOMETRIC_PARAMS

# Default search radius for layer detection (in microns)
# Set to 0.5 for precise detection in 0.5μm × 0.5μm area
DEFAULT_SEARCH_RADIUS = GEOMETRIC_PARAMS.get('layer_tap_radius', 0.5)

# FIB layers to exclude from detection
FIB_LAYERS = [LAYERS['cut'], LAYERS['connect'], LAYERS['probe']]


class LayerInfo:
    """Simple class to hold layer information"""
    
    def __init__(self, layer_num, datatype, name=None):
        self.layer = layer_num
        self.datatype = datatype
        self.name = name
    
    def to_string(self):
        """Return display string in format: layername:layer/datatype (e.g., M1:86/0)"""
        layer_num_str = f"{self.layer}/{self.datatype}"
        if self.name:
            return f"{self.name}:{layer_num_str}"
        return layer_num_str
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return f"LayerInfo({self.layer}/{self.datatype}, name={self.name})"
    
    def __eq__(self, other):
        if isinstance(other, LayerInfo):
            return self.layer == other.layer and self.datatype == other.datatype
        return False
    
    def __hash__(self):
        return hash((self.layer, self.datatype))


def get_layer_name_from_panel(view, layer_num, datatype):
    """
    Try to get layer name from Layer Panel.
    
    Args:
        view: Current layout view
        layer_num: Layer number
        datatype: Datatype
    
    Returns:
        Layer name string or None
    """
    try:
        for node in view.each_layer():
            if node.valid and hasattr(node, 'source'):
                source = node.source
                
                if isinstance(source, str):
                    # Parse string format
                    if '@' in source:
                        source = source.split('@')[0]
                    if ' ' in source:
                        # Format like "M1 86/0" - extract name and layer/datatype
                        parts = source.split()
                        if len(parts) >= 2:
                            name_part = parts[0]
                            layer_part = parts[-1]
                            try:
                                layer_parts = layer_part.split('/')
                                if len(layer_parts) >= 2:
                                    src_layer = int(layer_parts[0])
                                    src_datatype = int(layer_parts[1])
                                    if src_layer == layer_num and src_datatype == datatype:
                                        return name_part
                            except:
                                pass
                    else:
                        # Simple format "86/0"
                        try:
                            parts = source.split('/')
                            if len(parts) >= 2:
                                src_layer = int(parts[0])
                                src_datatype = int(parts[1])
                                if src_layer == layer_num and src_datatype == datatype:
                                    # Check if node has a name
                                    if hasattr(node, 'name') and node.name and node.name != f"{layer_num}/{datatype}":
                                        return node.name
                        except:
                            pass
        
        return None
        
    except Exception as e:
        print(f"[Layer Tap] Error getting layer name from panel: {e}")
        return None


def get_visible_layers():
    """
    Get all visible (non-hidden) layers from the Layer Panel.
    
    Returns:
        set of (layer, datatype) tuples that are visible in Layer Panel
    """
    try:
        main_window = pya.Application.instance().main_window()
        view = main_window.current_view()
        
        if view is None:
            return set()
        
        visible = set()
        
        # Iterate through all layers in the Layer Panel
        for node in view.each_layer():
            if node.valid and node.visible:  # Only include valid and visible layers
                # Parse layer info from source string
                if hasattr(node, 'source'):
                    source = node.source
                    
                    # source is a string like "86/0@1" or "86/0" or "FIB_CUT 337/0"
                    if isinstance(source, str):
                        try:
                            # Remove mask part if present
                            if '@' in source:
                                source = source.split('@')[0]
                            
                            # Handle format like "FIB_CUT 337/0" - extract the numeric part
                            if ' ' in source:
                                source = source.split()[-1]  # Take last part: "337/0"
                            
                            # Parse layer/datatype
                            parts = source.split('/')
                            if len(parts) >= 2:
                                layer_num = int(parts[0])
                                datatype = int(parts[1])
                                visible.add((layer_num, datatype))
                        except Exception as parse_error:
                            print(f"[Layer Tap] Error parsing layer source '{source}': {parse_error}")
                            continue
        
        print(f"[Layer Tap] Visible layers in panel: {len(visible)} layers - {visible}")
        return visible
        
    except Exception as e:
        print(f"[Layer Tap] Error getting visible layers: {e}")
        import traceback
        traceback.print_exc()
        return set()


def get_layers_at_point(x, y, search_radius=None):
    """
    Get all visible layers that have shapes at the given coordinate.
    
    Only searches layers that are visible (not hidden) in the Layer Panel.
    
    Args:
        x: X coordinate in microns
        y: Y coordinate in microns
        search_radius: Search radius in microns (default: 1.0)
    
    Returns:
        list of LayerInfo objects found at the position
    """
    if search_radius is None:
        search_radius = DEFAULT_SEARCH_RADIUS
    
    try:
        # Get current view and layout
        main_window = pya.Application.instance().main_window()
        current_view = main_window.current_view()
        
        if not current_view or not current_view.active_cellview().is_valid():
            print("[Layer Tap] No active layout view")
            return []
        
        cellview = current_view.active_cellview()
        layout = cellview.layout()
        cell = cellview.cell
        dbu = layout.dbu
        
        # Get visible layers from Layer Panel
        visible_layers = get_visible_layers()
        
        # Convert to database units
        db_x = int(x / dbu)
        db_y = int(y / dbu)
        db_radius = int(search_radius / dbu)
        
        # Ensure minimum search radius of 1 database unit
        if db_radius < 1:
            db_radius = 1
        
        # Create search box
        search_box = pya.Box(
            db_x - db_radius,
            db_y - db_radius,
            db_x + db_radius,
            db_y + db_radius
        )
        
        print(f"[Layer Tap] Searching at ({x:.3f}, {y:.3f}) um, radius={search_radius} um")
        print(f"[Layer Tap] DB units: point=({db_x}, {db_y}), radius={db_radius}, box={search_box}")
        
        found_layers = []
        
        # Iterate through all layers
        for layer_info in layout.layer_infos():
            layer_index = layout.layer(layer_info)
            if layer_index < 0:
                continue
            
            # Skip FIB layers
            if layer_info.layer in FIB_LAYERS:
                continue
            
            # Skip hidden layers (not visible in Layer Panel)
            if (layer_info.layer, layer_info.datatype) not in visible_layers:
                continue
            
            # Check if any shapes touch the search box
            shapes = cell.shapes(layer_index)
            if shapes.size() == 0:
                continue
            
            # Use each_touching for efficient search
            has_shape = False
            for shape in shapes.each_touching(search_box):
                has_shape = True
                break
            
            if has_shape:
                # Get layer name if available
                layer_name = layer_info.name if layer_info.name else None
                print(f"[Layer Tap] Layer {layer_info.layer}/{layer_info.datatype}: name='{layer_info.name}', type={type(layer_info.name)}")
                
                # Try to get layer name from Layer Panel if not available in layout
                if not layer_name:
                    layer_name = get_layer_name_from_panel(current_view, layer_info.layer, layer_info.datatype)
                    if layer_name:
                        print(f"[Layer Tap] Got name from panel: '{layer_name}'")
                
                found_layer = LayerInfo(layer_info.layer, layer_info.datatype, layer_name)
                found_layers.append(found_layer)
                print(f"[Layer Tap] Found layer: {found_layer}")
        
        print(f"[Layer Tap] Total visible layers found: {len(found_layers)}")
        return found_layers
        
    except Exception as e:
        print(f"[Layer Tap] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_selected_layer_from_panel():
    """
    Get the currently selected layer from KLayout's Layer Panel.
    
    Only returns the layer if it is visible (not hidden).
    
    Uses view.current_layer which returns a LayerPropertiesIterator.
    We need to call current() to get the actual LayerPropertiesNode.
    
    Returns:
        LayerInfo or None if no layer is selected or if the layer is hidden
    """
    try:
        main_window = pya.Application.instance().main_window()
        view = main_window.current_view()
        
        if view is None:
            print("[Layer Tap] No current view")
            return None
        
        # Get the currently selected layer iterator from Layer Panel
        layer_iter = view.current_layer
        
        print(f"[Layer Tap] current_layer: {layer_iter}, type: {type(layer_iter)}")
        
        # Check if a layer is selected
        if layer_iter.is_null():
            print("[Layer Tap] No layer selected in Layer Panel (is_null)")
            return None
        
        # Get the actual layer properties node
        node = layer_iter.current()
        
        print(f"[Layer Tap] layer node: {node}, type: {type(node)}")
        
        # Check if the layer is visible
        if hasattr(node, 'visible') and not node.visible:
            print(f"[Layer Tap] Selected layer is hidden (not visible), ignoring")
            return None
        
        # Check if the layer is valid
        if hasattr(node, 'valid') and not node.valid:
            print(f"[Layer Tap] Selected layer is not valid, ignoring")
            return None
        
        # Extract layer information from the node's source
        if hasattr(node, 'source'):
            source = node.source
            print(f"[Layer Tap] source: {source}, type: {type(source)}")
            
            # Check if source is a string (layer/datatype@mask format) or an object
            if isinstance(source, str):
                # Parse string format like "86/0@1" or "86/0" or "FIB_CUT 337/0"
                print(f"[Layer Tap] source is string, parsing: {source}")
                try:
                    # Remove mask part if present (e.g., "86/0@1" -> "86/0")
                    if '@' in source:
                        source = source.split('@')[0]
                    
                    # Handle format like "FIB_CUT 337/0" - extract the numeric part
                    if ' ' in source:
                        source = source.split()[-1]  # Take last part: "337/0"
                    
                    # Parse layer/datatype
                    parts = source.split('/')
                    if len(parts) >= 2:
                        layer_num = int(parts[0])
                        datatype = int(parts[1])
                    else:
                        print(f"[Layer Tap] Cannot parse source string: {source}")
                        return None
                except Exception as parse_error:
                    print(f"[Layer Tap] Error parsing source string '{source}': {parse_error}")
                    return None
            elif hasattr(source, 'layer') and hasattr(source, 'datatype'):
                # source is a LayerInfo object
                layer_num = source.layer
                datatype = source.datatype
            else:
                print(f"[Layer Tap] Unknown source type: {type(source)}")
                return None
            
            layer_name = node.name if hasattr(node, 'name') and node.name else None
            
            # Try to get better layer name if current name is just the layer/datatype
            if not layer_name or layer_name == f"{layer_num}/{datatype}":
                better_name = get_layer_name_from_panel(view, layer_num, datatype)
                if better_name:
                    layer_name = better_name
            
            print(f"[Layer Tap] Layer Panel selection: layer={layer_num}, datatype={datatype}, name={layer_name}, visible=True")
            
            # Skip FIB layers
            if layer_num in FIB_LAYERS:
                print(f"[Layer Tap] Skipping FIB layer {layer_num}")
                return None
            
            layer_info = LayerInfo(layer_num, datatype, layer_name)
            print(f"[Layer Tap] Successfully got Layer Panel selection: {layer_info}")
            return layer_info
        else:
            print("[Layer Tap] Node has no source attribute")
            return None
        
    except Exception as e:
        print(f"[Layer Tap] Error getting selected layer from panel: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_layer_at_point_with_selection(x, y, search_radius=None, position_label=""):
    """
    Get layer at point with smart selection strategy.
    
    Strategy:
    1. Search for layers at the click position
    2. If single layer found: use it directly
    3. If multiple layers found: use the layer selected in Layer Panel
    4. If no layers found: try to use Layer Panel selection as fallback
    
    Args:
        x: X coordinate in microns
        y: Y coordinate in microns
        search_radius: Search radius in microns
        position_label: Label for the position (e.g., "Point 1")
    
    Returns:
        LayerInfo or None
    """
    # Step 1: Search for layers at the position
    layers = get_layers_at_point(x, y, search_radius)
    
    # Case 1: No layers found at position - try Layer Panel as fallback
    if not layers:
        print(f"[Layer Tap] No layers found at ({x:.3f}, {y:.3f})")
        print(f"[Layer Tap] Trying Layer Panel selection as fallback...")
        selected_layer = get_selected_layer_from_panel()
        if selected_layer:
            print(f"[Layer Tap] Using Layer Panel selection: {selected_layer}")
            return selected_layer
        print(f"[Layer Tap] No Layer Panel selection either, returning None")
        return None
    
    # Case 2: Single layer found - use it directly
    if len(layers) == 1:
        print(f"[Layer Tap] Single layer at ({x:.3f}, {y:.3f}): {layers[0]}")
        return layers[0]
    
    # Case 3: Multiple layers found - use Layer Panel selection
    print(f"[Layer Tap] Multiple layers ({len(layers)}) at ({x:.3f}, {y:.3f})")
    layer_names = [l.to_string() for l in layers]
    print(f"[Layer Tap] Overlapping layers: {layer_names}")
    
    # Try to get the selected layer from Layer Panel
    selected_layer = get_selected_layer_from_panel()
    
    if selected_layer:
        # Check if the selected layer is among the found layers
        for layer in layers:
            if layer.layer == selected_layer.layer and layer.datatype == selected_layer.datatype:
                print(f"[Layer Tap] Using Layer Panel selection (matched): {selected_layer}")
                return selected_layer
        
        # Selected layer is not at this position, but still use it
        # (user explicitly selected it, so respect their choice)
        print(f"[Layer Tap] Layer Panel selection {selected_layer} not at position, but using it anyway")
        return selected_layer
    
    # No layer selected in panel - use the first found layer as fallback
    print(f"[Layer Tap] No Layer Panel selection, using first found: {layers[0]}")
    return layers[0]


def format_layer_for_display(layer_info):
    """
    Format layer info for display in UI.
    
    Args:
        layer_info: LayerInfo object or None
    
    Returns:
        String for display (e.g., "M1:86/0" or "N/A")
    """
    if layer_info is None:
        return "N/A"
    return layer_info.to_string()
