#!/usr/bin/env python3
"""
Layer Tap - Detect layers at click position

This module provides functionality to detect which layers contain shapes
at a given coordinate position, similar to KLayout's tap functionality.
"""

import pya
from config import LAYERS, GEOMETRIC_PARAMS

# Default search radius for layer detection (in microns)
# Can be overridden by GEOMETRIC_PARAMS['layer_tap_radius'] in config.py
DEFAULT_SEARCH_RADIUS = GEOMETRIC_PARAMS.get('layer_tap_radius', 0.01)  # 0.01 μm as requested by user

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


def get_layers_at_point(x, y, search_radius=None):
    """
    Get all layers that have shapes at the given coordinate.
    
    Args:
        x: X coordinate in microns
        y: Y coordinate in microns
        search_radius: Search radius in microns (default: 0.01)
    
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
        
        print(f"[Layer Tap] Searching at ({x:.3f}, {y:.3f}) μm, radius={search_radius} μm")
        
        found_layers = []
        
        # Iterate through all layers
        for layer_info in layout.layer_infos():
            layer_index = layout.layer(layer_info)
            if layer_index < 0:
                continue
            
            # Skip FIB layers
            if layer_info.layer in FIB_LAYERS:
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
                found_layer = LayerInfo(layer_info.layer, layer_info.datatype, layer_name)
                found_layers.append(found_layer)
                print(f"[Layer Tap] Found layer: {found_layer}")
        
        print(f"[Layer Tap] Total layers found: {len(found_layers)}")
        return found_layers
        
    except Exception as e:
        print(f"[Layer Tap] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def select_layer_dialog(layers, position_label=""):
    """
    Show a dialog for user to select a layer from multiple options.
    
    Args:
        layers: List of LayerInfo objects
        position_label: Optional label for the position (e.g., "Point 1")
    
    Returns:
        Selected LayerInfo or None if cancelled
    """
    if not layers:
        return None
    
    if len(layers) == 1:
        return layers[0]
    
    try:
        # Build selection list
        items = [layer.to_string() for layer in layers]
        
        # Show selection dialog
        title = "Select Layer"
        if position_label:
            title = f"Select Layer - {position_label}"
        
        result = pya.QInputDialog.getItem(
            None,
            title,
            f"Multiple layers found at this position.\nPlease select one:",
            items,
            0,  # Default selection
            False  # Not editable
        )
        
        # Handle different return formats
        if isinstance(result, tuple) and len(result) >= 2:
            selected_text, ok = result[0], result[1]
        else:
            selected_text = str(result) if result else ""
            ok = bool(selected_text)
        
        if ok and selected_text:
            # Find the matching layer
            for layer in layers:
                if layer.to_string() == selected_text:
                    print(f"[Layer Tap] User selected: {layer}")
                    return layer
        
        print("[Layer Tap] User cancelled selection")
        return None
        
    except Exception as e:
        print(f"[Layer Tap] Error in selection dialog: {e}")
        # Fallback: return first layer
        return layers[0] if layers else None


def get_layer_at_point_with_selection(x, y, search_radius=None, position_label=""):
    """
    Get layer at point, showing selection dialog if multiple layers found.
    
    Args:
        x: X coordinate in microns
        y: Y coordinate in microns
        search_radius: Search radius in microns
        position_label: Label for the position (e.g., "Point 1")
    
    Returns:
        LayerInfo or None
    """
    layers = get_layers_at_point(x, y, search_radius)
    
    if not layers:
        print(f"[Layer Tap] No layers found at ({x:.3f}, {y:.3f})")
        return None
    
    if len(layers) == 1:
        return layers[0]
    
    # Multiple layers - let user select
    return select_layer_dialog(layers, position_label)


def format_layer_for_display(layer_info):
    """
    Format layer info for display in UI.
    
    Args:
        layer_info: LayerInfo object or None
    
    Returns:
        String for display (e.g., "M1" or "1/0" or "N/A")
    """
    if layer_info is None:
        return "N/A"
    return layer_info.to_string()
