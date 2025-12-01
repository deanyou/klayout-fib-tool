"""
FIB Tool Plugin

Core plugin logic. Handles mouse events and coordinates between UI and data.
Keep it simple - no state machines, just direct mode handling.
"""

import pya
from markers import CutMarker, ConnectMarker, ProbeMarker
from storage import save_markers, load_markers, draw_markers_to_gds
from report import generate_report
from config import LAYERS
from ui import FIBToolDialog


class FIBPlugin(pya.Plugin):
    """
    FIB Tool Plugin
    
    Handles mouse events to create markers on the layout.
    """
    
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.markers = []
        self.mode = None  # 'cut', 'connect', 'probe', or None
        self.temp_point = None  # For multi-click operations
        self.marker_counter = {'cut': 0, 'connect': 0, 'probe': 0}
        
        # UI dialog
        self.dialog = None
        
        # Current cell and layout
        self.cell = None
        self.layout = None
    
    def show_dialog(self):
        """Show the FIB tool dialog"""
        if self.dialog is None:
            self.dialog = FIBToolDialog(self.view, self)
        self.dialog.show()
    
    def activate_mode(self, mode):
        """Activate a marker creation mode"""
        self.mode = mode
        self.temp_point = None
        self.grab_mouse()  # Start capturing mouse events
    
    def deactivate_mode(self):
        """Deactivate current mode"""
        self.mode = None
        self.temp_point = None
        self.ungrab_mouse()
    
    def mouse_click_event(self, p, buttons, prio):
        """Handle mouse click events"""
        if self.mode is None:
            return False
        
        # Get current cell
        if not self._update_current_cell():
            return False
        
        # Convert point to microns
        dbu = self.layout.dbu
        x = p.x * dbu
        y = p.y * dbu
        
        # Handle different modes
        if self.mode == 'cut':
            self._handle_cut_click(x, y)
        elif self.mode == 'connect':
            self._handle_connect_click(x, y)
        elif self.mode == 'probe':
            self._handle_probe_click(x, y)
        
        return False  # Continue event propagation
    
    def _handle_cut_click(self, x, y):
        """Handle cut marker creation (2 clicks)"""
        if self.temp_point is None:
            # First click - store position
            self.temp_point = (x, y)
        else:
            # Second click - determine direction and create marker
            x1, y1 = self.temp_point
            direction = self._calculate_direction(x1, y1, x, y)
            
            # Get target layer at this position
            layer = self._get_layer_at_position(x1, y1)
            
            # Create marker
            marker_id = f"CUT_{self.marker_counter['cut']}"
            self.marker_counter['cut'] += 1
            
            marker = CutMarker(marker_id, x1, y1, direction, layer)
            self.markers.append(marker)
            
            # Draw to GDS
            fib_layer = self.layout.layer(LAYERS['cut'], 0)
            marker.to_gds(self.cell, fib_layer)
            
            # Update UI
            if self.dialog:
                self.dialog.add_marker(marker)
            
            # Reset for next marker
            self.temp_point = None
            self.deactivate_mode()
    
    def _handle_connect_click(self, x, y):
        """Handle connect marker creation (2 clicks)"""
        if self.temp_point is None:
            # First click - store start point
            self.temp_point = (x, y)
        else:
            # Second click - create marker
            x1, y1 = self.temp_point
            
            # Get target layer
            layer = self._get_layer_at_position(x1, y1)
            
            # Create marker
            marker_id = f"CONNECT_{self.marker_counter['connect']}"
            self.marker_counter['connect'] += 1
            
            marker = ConnectMarker(marker_id, x1, y1, x, y, layer)
            self.markers.append(marker)
            
            # Draw to GDS
            fib_layer = self.layout.layer(LAYERS['connect'], 0)
            marker.to_gds(self.cell, fib_layer)
            
            # Update UI
            if self.dialog:
                self.dialog.add_marker(marker)
            
            # Reset
            self.temp_point = None
            self.deactivate_mode()
    
    def _handle_probe_click(self, x, y):
        """Handle probe marker creation (1 click)"""
        # Get target layer
        layer = self._get_layer_at_position(x, y)
        
        # Create marker
        marker_id = f"PROBE_{self.marker_counter['probe']}"
        self.marker_counter['probe'] += 1
        
        marker = ProbeMarker(marker_id, x, y, layer)
        self.markers.append(marker)
        
        # Draw to GDS
        fib_layer = self.layout.layer(LAYERS['probe'], 0)
        marker.to_gds(self.cell, fib_layer)
        
        # Update UI
        if self.dialog:
            self.dialog.add_marker(marker)
        
        # Reset
        self.deactivate_mode()
    
    def _update_current_cell(self):
        """Update current cell and layout references"""
        cellview = self.view.active_cellview()
        if cellview.is_valid():
            self.cell = cellview.cell
            self.layout = cellview.layout()
            return True
        return False
    
    def _calculate_direction(self, x1, y1, x2, y2):
        """Calculate direction from two points"""
        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'up' if dy > 0 else 'down'
    
    def _get_layer_at_position(self, x, y):
        """
        Get layer number at position.
        
        For MVP, just return a default layer.
        In v1.1, we can query actual layers under cursor.
        """
        return 6  # Default metal layer
    
    def delete_marker(self, marker_id):
        """Delete marker by ID"""
        # Find and remove marker
        self.markers = [m for m in self.markers if m.id != marker_id]
        
        # Redraw all markers (simple approach for MVP)
        self._redraw_all_markers()
    
    def _redraw_all_markers(self):
        """Clear and redraw all markers"""
        if not self._update_current_cell():
            return
        
        # Clear FIB layers
        for layer_num in LAYERS.values():
            layer = self.layout.layer(layer_num, 0)
            self.cell.shapes(layer).clear()
        
        # Redraw all markers
        draw_markers_to_gds(self.markers, self.cell, LAYERS)
    
    def save_markers(self, filename):
        """Save markers to XML file"""
        if not self._update_current_cell():
            return False
        
        library = self.layout.top_cells()[0].name if self.layout.top_cells() else ''
        cell_name = self.cell.name if self.cell else ''
        
        return save_markers(self.markers, filename, library, cell_name)
    
    def load_markers(self, filename):
        """Load markers from XML file"""
        markers, library, cell = load_markers(filename)
        
        if not markers:
            return False
        
        # Replace current markers
        self.markers = markers
        
        # Update counters
        for marker in markers:
            marker_type = marker.__class__.__name__.lower().replace('marker', '')
            # Extract number from ID (e.g., "CUT_5" -> 5)
            try:
                num = int(marker.id.split('_')[1])
                self.marker_counter[marker_type] = max(self.marker_counter[marker_type], num + 1)
            except (IndexError, ValueError):
                pass
        
        # Redraw
        self._redraw_all_markers()
        
        return True
    
    def generate_report(self, filename):
        """Generate HTML report"""
        if not self.markers:
            return False
        
        if not self._update_current_cell():
            return False
        
        library = self.layout.top_cells()[0].name if self.layout.top_cells() else ''
        cell_name = self.cell.name if self.cell else ''
        
        return generate_report(self.markers, library, cell_name, filename, self.view)
