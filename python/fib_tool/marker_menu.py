#!/usr/bin/env python3
"""
Marker Context Menu - Right-click menu functionality for FIB markers
Handles zoom, copy, rename, and delete operations
"""

import sys
import os
import pya
from .config import GEOMETRIC_PARAMS, UI_TIMEOUTS, DEFAULT_MARKER_NOTES

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
            
            # Get all selected items to determine menu options
            selected_items = self.panel.marker_list.selectedItems()
            selected_count = len(selected_items)
            
            # Create menu
            menu = pya.QMenu()
            
            # Single-selection actions (only available when one item is selected)
            if selected_count == 1:
                action_notes = menu.addAction("Add Notes")
                action_fit = menu.addAction("Zoom to Fit")
                action_copy = menu.addAction("Copy Coordinates")
                action_rename = menu.addAction("Rename Marker")
                
                # Add separator
                menu.addSeparator()
                
                # Add move up/down actions
                action_move_up = menu.addAction("↑ Move Up")
                action_move_down = menu.addAction("↓ Move Down")
            else:
                # Multi-selection: disable single-item actions
                action_notes = None
                action_fit = None
                action_copy = None
                action_rename = None
                action_move_up = None
                action_move_down = None
                
                # Add info about selection
                info_action = menu.addAction(f"{selected_count} markers selected")
                info_action.setEnabled(False)  # Make it non-clickable
            
            # Add separator
            menu.addSeparator()
            
            # Delete action (available for both single and multi-selection)
            if selected_count == 1:
                action_delete = menu.addAction("Delete Marker")
            else:
                action_delete = menu.addAction(f"Delete {selected_count} Markers")
            
            # Execute menu and get selected action
            global_pos = self.panel.marker_list.mapToGlobal(position)
            selected_action = menu.exec_(global_pos)
            
            # Handle the selected action
            if selected_count == 1:
                if selected_action == action_fit:
                    self.zoom_to_marker()
                elif selected_action == action_copy:
                    self.copy_coordinates()
                elif selected_action == action_notes:
                    self.add_notes()
                elif selected_action == action_rename:
                    self.rename_marker()
                elif selected_action == action_move_up:
                    self.move_marker_up()
                elif selected_action == action_move_down:
                    self.move_marker_down()
            
            # Delete action works for both single and multi-selection
            if selected_action == action_delete:
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
    
    def zoom_to_marker(self, detail_zoom=False):
        """Zoom view to fit the selected marker
        
        Args:
            detail_zoom (bool): If True, use minimal padding for maximum detail (double-click)
        """
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
            
            # Choose padding based on zoom type
            if detail_zoom:
                padding = GEOMETRIC_PARAMS['zoom_padding_detail']  # Very close zoom for detail
                zoom_type = "detail"
            else:
                padding = GEOMETRIC_PARAMS['zoom_padding']  # Normal zoom
                zoom_type = "normal"
            
            # Calculate marker bounds
            if hasattr(marker, 'x1'):  # CUT or CONNECT
                min_x = min(marker.x1, marker.x2)
                max_x = max(marker.x1, marker.x2)
                min_y = min(marker.y1, marker.y2)
                max_y = max(marker.y1, marker.y2)

                # Add padding
                min_x -= padding
                max_x += padding
                min_y -= padding
                max_y += padding
            else:  # PROBE
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
                
                print(f"[Marker Menu] Zoomed to marker {marker_id} ({zoom_type} zoom, padding={padding}μm)")

                # Show brief message
                try:
                    if detail_zoom:
                        pya.MainWindow.instance().message(f"Detail zoom: {marker_id}", UI_TIMEOUTS['message_short'])
                    else:
                        pya.MainWindow.instance().message(f"Zoomed to {marker_id}", UI_TIMEOUTS['message_short'])
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
    
    def add_notes(self):
        """Add or edit notes for the selected marker"""
        if not self.current_item:
            return
        
        try:
            marker_id = self.get_marker_id_from_item(self.current_item)
            marker = self.find_marker_by_id(marker_id)
            
            if not marker:
                pya.MessageBox.warning("Marker Menu", f"Marker {marker_id} not found", pya.MessageBox.Ok)
                return
            
            # Get current notes
            current_notes = getattr(marker, 'notes', '')
            
            # If notes is empty, set default based on marker type
            if not current_notes:
                marker_class = marker.__class__.__name__
                if 'Cut' in marker_class:
                    current_notes = DEFAULT_MARKER_NOTES['cut']
                elif 'Connect' in marker_class:
                    current_notes = DEFAULT_MARKER_NOTES['connect']
                elif 'Probe' in marker_class:
                    current_notes = DEFAULT_MARKER_NOTES['probe']
            
            # Show input dialog for notes
            try:
                result = pya.QInputDialog.getText(
                    self.panel, 
                    f"Add Notes - {marker_id}",
                    "Enter notes for this marker:",
                    pya.QLineEdit.Normal,
                    current_notes
                )
                
                # Handle different return formats
                if isinstance(result, tuple) and len(result) >= 2:
                    new_notes, ok = result[0], result[1]
                else:
                    new_notes = str(result) if result else ""
                    ok = bool(new_notes) or new_notes == ""  # Allow empty notes
                    
            except Exception as dialog_error:
                print(f"[Marker Menu] Dialog error: {dialog_error}")
                return
            
            if ok:
                # Update marker notes in both places for redundancy
                marker.notes = new_notes
                
                # Also store in centralized dictionary
                if hasattr(self.panel, 'marker_notes_dict'):
                    self.panel.marker_notes_dict[marker_id] = new_notes
                    print(f"[Marker Menu] Stored in dict: {marker_id} -> '{new_notes}'")
                
                print(f"[Marker Menu] Updated notes for {marker_id}: '{new_notes}'")
                print(f"[Marker Menu] Marker object id: {id(marker)}")
                print(f"[Marker Menu] Total markers in panel: {len(self.panel.markers_list)}")
                
                # Verify the update by checking all markers
                for m in self.panel.markers_list:
                    if hasattr(m, 'notes'):
                        print(f"[Marker Menu]   {m.id}: notes='{m.notes}' (obj_id={id(m)})")
                
                # Also print the centralized dict
                if hasattr(self.panel, 'marker_notes_dict'):
                    print(f"[Marker Menu] Centralized dict: {self.panel.marker_notes_dict}")
                
                # Show success message
                try:
                    if new_notes:
                        pya.MainWindow.instance().message(f"Notes added to {marker_id}", UI_TIMEOUTS['message_short'])
                    else:
                        pya.MainWindow.instance().message(f"Notes cleared for {marker_id}", UI_TIMEOUTS['message_short'])
                except:
                    pass
                
                # Show confirmation dialog
                if new_notes:
                    pya.MessageBox.info(
                        "Notes Updated", 
                        f"Notes for {marker_id}:\n\n{new_notes}\n\nNotes will be included in PDF export.",
                        pya.MessageBox.Ok
                    )
                
        except Exception as e:
            print(f"[Marker Menu] Error adding notes: {e}")
            import traceback
            traceback.print_exc()
    
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
                # Trim whitespace
                new_name = new_name.strip()

                # Check for empty name after trimming
                if not new_name:
                    pya.MessageBox.warning(
                        "Rename Marker",
                        "Marker name cannot be empty.",
                        pya.MessageBox.Ok
                    )
                    return

                # Check for duplicate names (case-insensitive)
                existing_ids = [m.id.lower() for m in self.panel.markers_list]

                if new_name.lower() in existing_ids:
                    pya.MessageBox.warning(
                        "Rename Marker",
                        f"Marker name '{new_name}' already exists.\n\n"
                        f"Please choose a different name.",
                        pya.MessageBox.Ok
                    )
                    print(f"[Marker Menu] Rename rejected: duplicate name '{new_name}'")
                    return

                # Update marker object
                marker = self.find_marker_by_id(marker_id)
                if marker:
                    old_id = marker.id
                    marker.id = new_name
                    
                    # Update coordinate text in GDS layout
                    self.update_coordinate_text_in_gds(marker, old_id, new_name)
                    
                    # Refresh the entire marker list to avoid Qt text setting issues
                    self.refresh_marker_list()
                    
                    # Reset smart counters after rename
                    if hasattr(self.panel, 'smart_counter'):
                        self.panel.smart_counter.reset_counters()
                    
                    print(f"[Marker Menu] Renamed: {old_id} -> {new_name}")

                    # Show success message
                    try:
                        pya.MainWindow.instance().message(f"Renamed to {new_name}", UI_TIMEOUTS['message_short'])
                    except:
                        pass
                
        except Exception as e:
            print(f"[Marker Menu] Error renaming marker: {e}")
    
    def _safe_call(self, obj, method_name, *args):
        """Safely call a method that might be a property in some Qt versions
        
        This handles KLayout's Qt bindings where some methods might be properties.
        """
        try:
            attr = getattr(obj, method_name)
            
            # Check if it's callable
            if callable(attr):
                # It's a method, call it with args
                return attr(*args)
            else:
                # It's a property, return its value (should have no args)
                if len(args) > 0:
                    print(f"[Marker Menu] Warning: {method_name} is a property but args were provided: {args}")
                return attr
                
        except Exception as e:
            print(f"[Marker Menu] Error in _safe_call({method_name}, {args}): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def move_marker_up(self):
        """Move the selected marker up in the list"""
        if not self.current_item:
            return
        
        try:
            # Get row of current item
            try:
                current_row = self.panel.marker_list.row(self.current_item)
            except TypeError:
                print(f"[Marker Menu] row() not callable")
                return
            
            if current_row <= 0:
                # Already at top
                pya.MessageBox.info("Move Marker", "Marker is already at the top of the list", pya.MessageBox.Ok)
                return
            
            # Use the panel's move method instead of duplicating logic
            if hasattr(self.panel, 'on_move_marker_up'):
                # Set the current row first
                try:
                    self.panel.marker_list.setCurrentRow(current_row)
                except:
                    pass
                # Call the panel's move method
                self.panel.on_move_marker_up()
            else:
                print(f"[Marker Menu] Panel doesn't have on_move_marker_up method")
            
        except Exception as e:
            print(f"[Marker Menu] Error moving marker up: {e}")
            import traceback
            traceback.print_exc()
    
    def move_marker_down(self):
        """Move the selected marker down in the list"""
        if not self.current_item:
            return
        
        try:
            # Get row of current item
            try:
                current_row = self.panel.marker_list.row(self.current_item)
            except TypeError:
                print(f"[Marker Menu] row() not callable")
                return
            
            # Get count
            try:
                list_count = self.panel.marker_list.count()
            except TypeError:
                list_count = self.panel.marker_list.count
            
            if current_row < 0 or current_row >= list_count - 1:
                # Already at bottom
                pya.MessageBox.info("Move Marker", "Marker is already at the bottom of the list", pya.MessageBox.Ok)
                return
            
            # Use the panel's move method instead of duplicating logic
            if hasattr(self.panel, 'on_move_marker_down'):
                # Set the current row first
                try:
                    self.panel.marker_list.setCurrentRow(current_row)
                except:
                    pass
                # Call the panel's move method
                self.panel.on_move_marker_down()
            else:
                print(f"[Marker Menu] Panel doesn't have on_move_marker_down method")
            
        except Exception as e:
            print(f"[Marker Menu] Error moving marker down: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_marker(self):
        """Delete the selected marker(s) from both panel and GDS layout"""
        try:
            # Get all selected items
            selected_items = self.panel.marker_list.selectedItems()
            
            if not selected_items:
                print(f"[Marker Menu] No markers selected for deletion")
                return
            
            # Extract marker IDs from selected items
            markers_to_delete = []
            marker_ids = []
            
            for item in selected_items:
                marker_id = self.get_marker_id_from_item(item)
                marker_obj = self.find_marker_by_id(marker_id)
                
                if marker_obj:
                    markers_to_delete.append((item, marker_id, marker_obj))
                    marker_ids.append(marker_id)
                else:
                    print(f"[Marker Menu] Marker {marker_id} not found in markers list")
            
            if not markers_to_delete:
                print(f"[Marker Menu] No valid markers found for deletion")
                return
            
            # Confirm deletion
            if len(markers_to_delete) == 1:
                message = f"Are you sure you want to delete {marker_ids[0]}?\n\nThis will remove it from both the panel and the GDS layout."
                title = "Delete Marker"
            else:
                marker_list = "\n".join([f"  • {mid}" for mid in marker_ids])
                message = f"Are you sure you want to delete {len(markers_to_delete)} markers?\n\n{marker_list}\n\nThis will remove them from both the panel and the GDS layout."
                title = "Delete Multiple Markers"
            
            result = pya.MessageBox.question(title, message, pya.MessageBox.Yes | pya.MessageBox.No)
            
            if result == pya.MessageBox.Yes:
                deleted_count = 0
                failed_count = 0
                
                # Delete each marker
                for item, marker_id, marker_obj in markers_to_delete:
                    try:
                        # Delete from GDS layout first
                        success = self.delete_marker_from_gds(marker_obj)
                        
                        if success:
                            # Remove from list widget
                            try:
                                row = self.panel.marker_list.row(item)
                                self.panel.marker_list.takeItem(row)
                            except Exception as remove_error:
                                print(f"[Marker Menu] Error removing {marker_id} from list: {remove_error}")
                            
                            # Remove from markers list
                            self.panel.markers_list = [m for m in self.panel.markers_list if m.id != marker_id]
                            
                            deleted_count += 1
                            print(f"[Marker Menu] Successfully deleted marker: {marker_id}")
                        else:
                            failed_count += 1
                            print(f"[Marker Menu] Failed to delete {marker_id} from GDS layout")
                            
                    except Exception as delete_error:
                        failed_count += 1
                        print(f"[Marker Menu] Error deleting {marker_id}: {delete_error}")
                
                # Reset smart counters after deletion
                if hasattr(self.panel, 'smart_counter'):
                    self.panel.smart_counter.reset_counters()
                
                # Show summary message
                if deleted_count > 0:
                    if failed_count == 0:
                        if deleted_count == 1:
                            message = f"Deleted {marker_ids[0]} from layout"
                        else:
                            message = f"Deleted {deleted_count} markers from layout"
                    else:
                        message = f"Deleted {deleted_count} markers, {failed_count} failed"
                    
                    try:
                        pya.MainWindow.instance().message(message, UI_TIMEOUTS['message_short'])
                    except:
                        pass
                    
                    print(f"[Marker Menu] Deletion complete: {deleted_count} deleted, {failed_count} failed")
                else:
                    pya.MessageBox.warning("Delete Markers", "Failed to delete any markers from GDS layout", pya.MessageBox.Ok)
                
        except Exception as e:
            print(f"[Marker Menu] Error deleting markers: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_marker_from_gds(self, marker):
        """Delete marker geometry and coordinate texts from GDS layout"""
        try:
            # Get current view and layout
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view or not current_view.active_cellview().is_valid():
                print("[Marker Menu] No active layout found for deletion")
                return False
            
            cellview = current_view.active_cellview()
            cell = cellview.cell
            layout = cellview.layout()
            
            print(f"[Marker Menu] Deleting marker {marker.id} from GDS layout")
            
            # Step 1: Delete coordinate texts containing marker ID
            deleted_texts = self.delete_coordinate_texts_for_marker(marker, cell, layout)
            
            # Step 2: Delete marker geometry
            deleted_geometry = self.delete_marker_geometry(marker, cell, layout)
            
            total_deleted = deleted_texts + deleted_geometry
            print(f"[Marker Menu] Deleted {deleted_texts} texts and {deleted_geometry} geometry objects for {marker.id}")
            
            return total_deleted > 0
            
        except Exception as e:
            print(f"[Marker Menu] Error deleting marker from GDS: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_coordinate_texts_for_marker(self, marker, cell, layout):
        """Delete coordinate texts associated with the marker"""
        try:
            deleted_count = 0
            
            # Search ALL layers for texts containing marker ID
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
                        
                        # Delete any text containing the marker ID
                        if marker.id in text_string:
                            shapes_to_remove.append(shape)
                            print(f"[Marker Menu] Marking text for deletion: '{text_string}' on layer {layer_info.layer}/{layer_info.datatype}")
                
                # Remove the texts
                for shape in shapes_to_remove:
                    shapes.erase(shape)
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"[Marker Menu] Error deleting coordinate texts: {e}")
            return 0
    
    def delete_marker_geometry(self, marker, cell, layout):
        """Delete marker geometry from the appropriate FIB layer"""
        try:
            # Get the marker layer
            marker_type = marker.__class__.__name__.lower().replace('marker', '')
            # Handle multi-point markers (e.g., "multipointcutmarker" -> "cut")
            if 'multipoint' in marker_type:
                marker_type = marker_type.replace('multipoint', '')
            
            from .config import LAYERS
            if marker_type not in LAYERS:
                print(f"[Marker Menu] Unknown marker type: {marker_type}")
                return 0
            
            layer_num = LAYERS[marker_type]
            fib_layer = layout.layer(layer_num, 0)
            
            print(f"[Marker Menu] Deleting {marker_type} geometry from layer {layer_num}")
            
            # Get marker coordinates for geometry matching
            # Check for multi-point markers first (they have 'points' attribute)
            if hasattr(marker, 'points') and len(marker.points) > 0:
                # Multi-point marker: search around ALL points
                marker_coords = marker.points
                print(f"[Marker Menu] Multi-point marker with {len(marker_coords)} points")
            elif hasattr(marker, 'x1'):  # Regular CUT or CONNECT markers
                marker_coords = [(marker.x1, marker.y1), (marker.x2, marker.y2)]
            else:  # PROBE marker
                marker_coords = [(marker.x, marker.y)]
            
            # Convert to database units
            dbu = layout.dbu
            db_coords = [(int(x / dbu), int(y / dbu)) for x, y in marker_coords]
            
            # Find and delete geometry near marker coordinates
            deleted_count = 0
            shapes = cell.shapes(fib_layer)
            shapes_to_remove = []
            
            # Create search regions around marker coordinates
            search_radius = int(GEOMETRIC_PARAMS['search_radius'] / dbu)
            
            for db_x, db_y in db_coords:
                search_box = pya.Box(
                    db_x - search_radius, db_y - search_radius,
                    db_x + search_radius, db_y + search_radius
                )
                
                # Find overlapping shapes
                for shape in shapes.each_overlapping(search_box):
                    if not shape.is_text():  # Only delete geometry, not text
                        shapes_to_remove.append(shape)
                        print(f"[Marker Menu] Marking geometry for deletion near ({db_x * dbu:.2f}, {db_y * dbu:.2f})")
            
            # Remove duplicate shapes
            shapes_to_remove = list(set(shapes_to_remove))
            
            # Delete the shapes
            for shape in shapes_to_remove:
                shapes.erase(shape)
                deleted_count += 1
            
            print(f"[Marker Menu] Deleted {deleted_count} geometry shapes for {marker.id}")
            return deleted_count
            
        except Exception as e:
            print(f"[Marker Menu] Error deleting marker geometry: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def handle_double_click(self, item):
        """Handle double-click on marker (zoom to maximum detail)"""
        self.current_item = item
        self.zoom_to_marker(detail_zoom=True)  # Use detail zoom for double-click
    
    def refresh_marker_list(self):
        """Refresh the marker list display"""
        try:
            # Clear the current list
            self.panel.marker_list.clear()
            
            # Re-add all markers
            for marker in self.panel.markers_list:
                marker_class_name = marker.__class__.__name__
                marker_type = marker_class_name.replace('Marker', '').upper()
                
                # Handle multi-point markers
                if 'MultiPoint' in marker_class_name:
                    if 'Cut' in marker_class_name:
                        marker_type = "CUT (MULTI)"
                    elif 'Connect' in marker_class_name:
                        marker_type = "CONNECT (MULTI)"
                    
                    if hasattr(marker, 'points') and len(marker.points) > 0:
                        if len(marker.points) <= 3:
                            point_strs = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points]
                            coords = " -> ".join(point_strs)
                        else:
                            first = marker.points[0]
                            last = marker.points[-1]
                            coords = f"({first[0]:.3f},{first[1]:.3f}) -> ... -> ({last[0]:.3f},{last[1]:.3f}) [{len(marker.points)} pts]"
                    else:
                        coords = "(no points)"
                elif hasattr(marker, 'x1'):  # CUT or CONNECT
                    # Get layer info for display
                    layer1_str = getattr(marker, 'layer1', None) or 'N/A'
                    layer2_str = getattr(marker, 'layer2', None) or 'N/A'
                    coords = f"({marker.x1:.3f},{marker.y1:.3f}) {layer1_str} to ({marker.x2:.3f},{marker.y2:.3f}) {layer2_str}"
                else:  # PROBE
                    # Get layer info for display
                    target_layer_str = getattr(marker, 'target_layer', None) or 'N/A'
                    coords = f"({marker.x:.3f},{marker.y:.3f}) {target_layer_str}"
                
                item_text = f"{marker.id} - {marker_type} - {coords}"
                self.panel.marker_list.addItem(item_text)
            
            print(f"[Marker Menu] Refreshed marker list with {len(self.panel.markers_list)} items")
            
        except Exception as e:
            print(f"[Marker Menu] Error refreshing marker list: {e}")
    
    def update_coordinate_text_in_gds(self, marker, old_id, new_id):
        """Update coordinate text in GDS layout using search and replace on ALL layers"""
        try:
            # Get current view and layout
            main_window = pya.Application.instance().main_window()
            current_view = main_window.current_view()
            
            if not current_view or not current_view.active_cellview().is_valid():
                print("[Marker Menu] No active layout found for text update")
                return False
            
            cellview = current_view.active_cellview()
            cell = cellview.cell
            layout = cellview.layout()
            
            print(f"[Marker Menu] Search and replace: '{old_id}' -> '{new_id}' on ALL layers")
            
            total_updated = 0
            
            # Search ALL layers for text objects (not just coordinate layer)
            for layer_info in layout.layer_infos():
                layer_index = layout.layer(layer_info)
                if layer_index < 0:
                    continue
                
                shapes = cell.shapes(layer_index)
                shapes_to_remove = []
                shapes_to_add = []
                layer_updated = 0
                
                for shape in shapes.each():
                    if shape.is_text():
                        text_obj = shape.text
                        text_string = text_obj.string
                        
                        # Simple string replacement: if text contains old_id, replace it
                        if old_id in text_string:
                            new_text_string = text_string.replace(old_id, new_id)
                            
                            if new_text_string != text_string:
                                # Mark for replacement
                                shapes_to_remove.append(shape)
                                new_text_obj = pya.Text(new_text_string, text_obj.trans)
                                shapes_to_add.append(new_text_obj)
                                
                                print(f"[Marker Menu] Layer {layer_info.layer}/{layer_info.datatype}: '{text_string}' -> '{new_text_string}'")
                                layer_updated += 1
                
                # Apply changes for this layer
                for shape in shapes_to_remove:
                    shapes.erase(shape)
                
                for text_obj in shapes_to_add:
                    shapes.insert(text_obj)
                
                if layer_updated > 0:
                    total_updated += layer_updated
            
            print(f"[Marker Menu] Search and replace completed: {total_updated} texts updated across all layers")
            
            # Show success message if any updates were made
            if total_updated > 0:
                try:
                    pya.MainWindow.instance().message(f"Updated {total_updated} texts", UI_TIMEOUTS['message_short'])
                except:
                    pass
            else:
                print(f"[Marker Menu] No texts found containing '{old_id}' - this might be normal if texts don't include marker IDs")
            
            return total_updated > 0
            
        except Exception as e:
            print(f"[Marker Menu] Error in search and replace: {e}")
            import traceback
            traceback.print_exc()
            return False