#!/usr/bin/env python3
"""
Marker Context Menu - Right-click menu functionality for FIB markers
Handles zoom, copy, rename, and delete operations
"""

import sys
import os
import pya

class MarkerContextMenu:
    """Context menu handler for FIB markers"""
    
    def __init__(self, panel):
        self.panel = panel
        self.current_item = None
    
    def show_context_menu(self, position):
        """Show context menu at the given position"""
        try:
            # Get the item at the position
            item = self.panel.marker_list.itemAt(position)
            if not item:
                return
            
            self.current_item = item
            
            # Create menu
            menu = pya.QMenu()
            
            action_fit = menu.addAction("Zoom to Fit")
            action_copy = menu.addAction("Copy Coordinates")
            action_rename = menu.addAction("Rename Marker")
            action_delete = menu.addAction("Delete Marker")
            
            # Execute menu and get selected action
            global_pos = self.panel.marker_list.mapToGlobal(position)
            selected_action = menu.exec_(global_pos)
            
            # Handle the selected action
            if selected_action == action_fit:
                self.zoom_to_marker()
            elif selected_action == action_copy:
                self.copy_coordinates()
            elif selected_action == action_rename:
                self.rename_marker()
            elif selected_action == action_delete:
                self.delete_marker()
                
        except Exception as e:
            print(f"[Marker Menu] Error in context menu: {e}")
            import traceback
            traceback.print_exc()
    
    def get_item_text(self, item):
        """Safely get text from QListWidgetItem"""
        try:
            # Try different ways to get the text
            if hasattr(item, 'text') and callable(item.text):
                return item.text()
            elif hasattr(item, 'text'):
                return str(item.text)
            elif hasattr(item, 'data'):
                return str(item.data(0))  # Qt.DisplayRole = 0
            else:
                return str(item)
        except Exception as e:
            print(f"[Marker Menu] Error getting item text: {e}")
            return "Unknown"
    
    def get_marker_id_from_item(self, item):
        """Extract marker ID from list item"""
        try:
            text = self.get_item_text(item)
            # Format is: "MARKER_ID - TYPE - (coordinates)"
            parts = text.split(' - ')
            if len(parts) >= 1:
                return parts[0].strip()
            return text.strip()
        except Exception as e:
            print(f"[Marker Menu] Error extracting marker ID: {e}")
            return "Unknown"
    
    def find_marker_by_id(self, marker_id):
        """Find marker object by ID"""
        for marker in self.panel.markers_list:
            if marker.id == marker_id:
                return marker
        return None
    
    def zoom_to_marker(self):
        """Zoom view to fit the selected marker"""
        if not self.current_item:
            return
        
        try:
            marker_id = self.get_marker_id_from_item(self.current_item)
            marker = self.find_marker_by_id(marker_id)
            
            if not marker:
                pya.MessageBox.warning("Marker Menu", f"Marker {marker_id} not found", pya.MessageBox.Ok)
                return
            
            # Get current view
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view:
                pya.MessageBox.warning("Marker Menu", "No active layout view", pya.MessageBox.Ok)
                return
            
            # Calculate marker bounds
            if hasattr(marker, 'x1'):  # CUT or CONNECT
                min_x = min(marker.x1, marker.x2)
                max_x = max(marker.x1, marker.x2)
                min_y = min(marker.y1, marker.y2)
                max_y = max(marker.y1, marker.y2)
                
                # Add some padding
                padding = 5.0  # microns
                min_x -= padding
                max_x += padding
                min_y -= padding
                max_y += padding
            else:  # PROBE
                padding = 5.0  # microns
                min_x = marker.x - padding
                max_x = marker.x + padding
                min_y = marker.y - padding
                max_y = marker.y + padding
            
            # Create box and fit view
            cellview = current_view.active_cellview()
            if cellview.is_valid():
                # Create box in microns
                box = pya.DBox(min_x, min_y, max_x, max_y)
                
                # Fit view to box
                current_view.zoom_box(box)
                
                print(f"[Marker Menu] Zoomed to marker {marker_id}")
                
                # Show brief message
                try:
                    pya.MainWindow.instance().message(f"Zoomed to {marker_id}", 2000)
                except:
                    pass
            
        except Exception as e:
            print(f"[Marker Menu] Error zooming to marker: {e}")
            pya.MessageBox.warning("Marker Menu", f"Error zooming to marker: {e}", pya.MessageBox.Ok)
    
    def copy_coordinates(self):
        """Copy marker coordinates to clipboard"""
        if not self.current_item:
            return
        
        try:
            marker_id = self.get_marker_id_from_item(self.current_item)
            marker = self.find_marker_by_id(marker_id)
            
            if not marker:
                return
            
            # Format coordinates
            if hasattr(marker, 'x1'):  # CUT or CONNECT
                coords_text = f"{marker_id}: ({marker.x1:.3f},{marker.y1:.3f}) to ({marker.x2:.3f},{marker.y2:.3f})"
            else:  # PROBE
                coords_text = f"{marker_id}: ({marker.x:.3f},{marker.y:.3f})"
            
            # Copy to clipboard
            try:
                clipboard = pya.QApplication.clipboard()
                clipboard.setText(coords_text)
                pya.MessageBox.info("Marker Menu", f"Coordinates copied:\n{coords_text}", pya.MessageBox.Ok)
                print(f"[Marker Menu] Copied coordinates: {coords_text}")
            except Exception as clipboard_error:
                print(f"[Marker Menu] Clipboard error: {clipboard_error}")
                # Fallback: just show the coordinates
                pya.MessageBox.info("Marker Menu", f"Coordinates:\n{coords_text}", pya.MessageBox.Ok)
                
        except Exception as e:
            print(f"[Marker Menu] Error copying coordinates: {e}")
    
    def rename_marker(self):
        """Rename the selected marker"""
        if not self.current_item:
            return
        
        try:
            marker_id = self.get_marker_id_from_item(self.current_item)
            
            # Get new name from user
            try:
                result = pya.QInputDialog.getText(
                    self.panel, "Rename Marker",
                    "Enter new name:",
                    pya.QLineEdit.Normal,
                    marker_id
                )
                
                # Handle different return formats
                if isinstance(result, tuple) and len(result) == 2:
                    new_name, ok = result
                elif isinstance(result, tuple) and len(result) > 2:
                    new_name, ok = result[0], result[1]
                else:
                    # Fallback: assume it's just the text
                    new_name = str(result) if result else ""
                    ok = bool(new_name)
                    
            except Exception as dialog_error:
                print(f"[Marker Menu] Dialog error: {dialog_error}")
                # Fallback: use a simple approach
                new_name = f"{marker_id}_renamed"
                ok = True
            
            if ok and new_name and new_name != marker_id:
                # Update marker object
                marker = self.find_marker_by_id(marker_id)
                if marker:
                    old_id = marker.id
                    marker.id = new_name
                    
                    # Refresh the entire marker list to avoid Qt text setting issues
                    self.refresh_marker_list()
                    
                    # Reset smart counters after rename
                    if hasattr(self.panel, 'smart_counter'):
                        self.panel.smart_counter.reset_counters()
                    
                    print(f"[Marker Menu] Renamed: {old_id} -> {new_name}")
                    
                    # Show success message
                    try:
                        pya.MainWindow.instance().message(f"Renamed to {new_name}", 2000)
                    except:
                        pass
                
        except Exception as e:
            print(f"[Marker Menu] Error renaming marker: {e}")
    
    def delete_marker(self):
        """Delete the selected marker"""
        if not self.current_item:
            return
        
        try:
            marker_id = self.get_marker_id_from_item(self.current_item)
            
            # Confirm deletion
            result = pya.MessageBox.question(
                "Delete Marker",
                f"Are you sure you want to delete {marker_id}?\n\nThis will remove it from the panel list.\n(Use 'Clear All' to remove from GDS layout)",
                pya.MessageBox.Yes | pya.MessageBox.No
            )
            
            if result == pya.MessageBox.Yes:
                # Remove from list widget
                try:
                    row = self.panel.marker_list.row(self.current_item)
                    self.panel.marker_list.takeItem(row)
                except Exception as remove_error:
                    print(f"[Marker Menu] Error removing from list: {remove_error}")
                
                # Remove from markers list
                self.panel.markers_list = [m for m in self.panel.markers_list if m.id != marker_id]
                
                # Reset smart counters after deletion
                if hasattr(self.panel, 'smart_counter'):
                    self.panel.smart_counter.reset_counters()
                
                print(f"[Marker Menu] Deleted marker: {marker_id}")
                
                # Show brief message
                try:
                    pya.MainWindow.instance().message(f"Deleted {marker_id}", 2000)
                except:
                    pass
                
        except Exception as e:
            print(f"[Marker Menu] Error deleting marker: {e}")
    
    def handle_double_click(self, item):
        """Handle double-click on marker (zoom to fit)"""
        self.current_item = item
        self.zoom_to_marker()
    
    def refresh_marker_list(self):
        """Refresh the marker list display"""
        try:
            # Clear the current list
            self.panel.marker_list.clear()
            
            # Re-add all markers
            for marker in self.panel.markers_list:
                marker_type = marker.__class__.__name__.replace('Marker', '').upper()
                
                if hasattr(marker, 'x1'):  # CUT or CONNECT
                    coords = f"({marker.x1:.2f},{marker.y1:.2f}) to ({marker.x2:.2f},{marker.y2:.2f})"
                else:  # PROBE
                    coords = f"({marker.x:.2f},{marker.y:.2f})"
                
                item_text = f"{marker.id} - {marker_type} - {coords}"
                self.panel.marker_list.addItem(item_text)
            
            print(f"[Marker Menu] Refreshed marker list with {len(self.panel.markers_list)} items")
            
        except Exception as e:
            print(f"[Marker Menu] Error refreshing marker list: {e}")