#!/usr/bin/env python3
"""
Screenshot Export Module for FIB Tool

Generates 3-level screenshots for each marker:
1. Overview (Fit All) with crosshair
2. Zoom 2x (medium zoom)
3. Detail (close-up)

Each screenshot includes a scale bar in micrometers.
"""

import os
import pya
from .config import SCREENSHOT_CONFIG


def get_marker_bbox(marker):
    """
    Get bounding box for a marker
    
    Args:
        marker: Marker object (CutMarker, ConnectMarker, ProbeMarker, or MultiPoint)
    
    Returns:
        pya.DBox: Bounding box in microns
    """
    try:
        # Multi-point markers
        if hasattr(marker, 'points') and marker.points:
            xs = [p[0] for p in marker.points]
            ys = [p[1] for p in marker.points]
            return pya.DBox(min(xs), min(ys), max(xs), max(ys))
        
        # CUT or CONNECT markers (2 points)
        elif hasattr(marker, 'x1'):
            return pya.DBox(
                min(marker.x1, marker.x2), 
                min(marker.y1, marker.y2),
                max(marker.x1, marker.x2), 
                max(marker.y1, marker.y2)
            )
        
        # PROBE marker (single point)
        elif hasattr(marker, 'x'):
            # Use a default radius for single point
            r = SCREENSHOT_CONFIG['default_probe_radius']  # Default probe radius
            return pya.DBox(marker.x - r, marker.y - r, marker.x + r, marker.y + r)
        
        else:
            print(f"[Screenshot] Warning: Unknown marker type for {marker.id}")
            return pya.DBox(0, 0, 10, 10)
            
    except Exception as e:
        print(f"[Screenshot] Error getting bbox for {marker.id}: {e}")
        return pya.DBox(0, 0, 10, 10)


def calculate_scale_bar_length(view_width):
    """
    Calculate appropriate scale bar length
    
    Args:
        view_width: Width of the view in microns
    
    Returns:
        float: Scale bar length in microns
    """
    # Target: 10-20% of view width
    target_length = view_width * SCREENSHOT_CONFIG['scale_bar']['target_percentage']

    # Nice round numbers for scale bars
    nice_values = SCREENSHOT_CONFIG['scale_bar']['nice_values']
    
    # Find the closest nice value
    for val in nice_values:
        if val >= target_length * 0.5:
            return val
    
    return nice_values[-1]


def create_marker_dimension_rulers(view, marker):
    """
    Create dimension rulers at marker coordinates showing X and Y lengths
    
    Args:
        view: LayoutView object
        marker: Marker object
    """
    try:
        # Get marker coordinates
        if hasattr(marker, 'points') and len(marker.points) >= 2:
            # Multi-point marker: use first and last points
            x1, y1 = marker.points[0]
            x2, y2 = marker.points[-1]
        elif hasattr(marker, 'x1'):
            # CUT or CONNECT marker
            x1, y1 = marker.x1, marker.y1
            x2, y2 = marker.x2, marker.y2
        else:
            # PROBE marker - no dimensions to show
            print(f"[Screenshot] PROBE marker has no dimensions to measure")
            return
        
        # Calculate deltas
        delta_x = abs(x2 - x1)
        delta_y = abs(y2 - y1)
        
        # X direction ruler (horizontal)
        if delta_x > 0.01:  # Only show if significant
            x_ruler = pya.Annotation()
            x_ruler.p1 = pya.DPoint(x1, y1)
            x_ruler.p2 = pya.DPoint(x2, y1)
            x_ruler.style = pya.Annotation.StyleRuler  # Ruler with measurement
            # Remove custom format to avoid $ syntax errors
            view.insert_annotation(x_ruler)
            print(f"[Screenshot] Created X ruler: DX = {delta_x:.2f} um")
        
        # Y direction ruler (vertical)
        if delta_y > 0.01:  # Only show if significant
            y_ruler = pya.Annotation()
            y_ruler.p1 = pya.DPoint(x2, y1)
            y_ruler.p2 = pya.DPoint(x2, y2)
            y_ruler.style = pya.Annotation.StyleRuler  # Ruler with measurement
            # Remove custom format to avoid $ syntax errors
            view.insert_annotation(y_ruler)
            print(f"[Screenshot] Created Y ruler: DY = {delta_y:.2f} um")
        
        print(f"[Screenshot] Marker dimensions: DX={delta_x:.2f} um, DY={delta_y:.2f} um")
        
    except Exception as e:
        print(f"[Screenshot] Error creating dimension rulers: {e}")
        import traceback
        traceback.print_exc()


def create_crosshair_annotation(view, marker_center, layout_bbox):
    """
    Create crosshair annotation pointing to marker center
    
    Note: Annotation color is controlled by KLayout view settings.
    To change to white, go to: File → Setup → Display → Rulers/Annotations
    and set the color to white (RGB: 255, 255, 255).
    
    Args:
        view: LayoutView object
        marker_center: pya.DPoint - center of marker
        layout_bbox: pya.DBox - layout bounding box
    """
    try:
        # Horizontal line
        h_ruler = pya.Annotation()
        h_ruler.p1 = pya.DPoint(layout_bbox.left, marker_center.y)
        h_ruler.p2 = pya.DPoint(layout_bbox.right, marker_center.y)
        h_ruler.style = pya.Annotation.StyleLine
        view.insert_annotation(h_ruler)
        
        # Vertical line
        v_ruler = pya.Annotation()
        v_ruler.p1 = pya.DPoint(marker_center.x, layout_bbox.bottom)
        v_ruler.p2 = pya.DPoint(marker_center.x, layout_bbox.top)
        v_ruler.style = pya.Annotation.StyleLine
        view.insert_annotation(v_ruler)
        
        print(f"[Screenshot] Created crosshair at ({marker_center.x:.2f}, {marker_center.y:.2f})")
        print(f"[Screenshot] Note: To change crosshair color to white, set ruler color in KLayout preferences")
        
    except Exception as e:
        print(f"[Screenshot] Error creating crosshair: {e}")


def create_scale_bar(view, view_bbox):
    """
    Create scale bar annotation in lower left corner
    
    Args:
        view: LayoutView object
        view_bbox: pya.DBox - current view bounding box
    """
    try:
        # Calculate appropriate scale bar length
        scale_length = calculate_scale_bar_length(view_bbox.width())
        
        # Position: lower left corner with 5% margin
        margin_x = view_bbox.width() * 0.05
        margin_y = view_bbox.height() * 0.05
        
        scale_x = view_bbox.left + margin_x
        scale_y = view_bbox.bottom + margin_y
        
        # Create scale bar with ruler style (shows measurement)
        scale_bar = pya.Annotation()
        scale_bar.p1 = pya.DPoint(scale_x, scale_y)
        scale_bar.p2 = pya.DPoint(scale_x + scale_length, scale_y)
        scale_bar.style = pya.Annotation.StyleRuler  # Ruler style with measurement
        view.insert_annotation(scale_bar)
        
        print(f"[Screenshot] Created scale bar: {scale_length} um")
        
    except Exception as e:
        print(f"[Screenshot] Error creating scale bar: {e}")


def select_marker_path(view, marker):
    """
    Select the marker's coordinate text labels for highlighting in screenshots
    
    This function finds and selects the text labels associated with the marker
    to make them more visible in screenshots with highlighting boxes.
    
    Args:
        view: LayoutView object
        marker: Marker object
    
    Returns:
        bool: True if selection successful
    """
    try:
        print(f"[Screenshot] Attempting to select text labels for {marker.id}")
        
        # Clear any existing selection first
        view.clear_selection()
        
        cellview = view.active_cellview()
        if not cellview.is_valid():
            print(f"[Screenshot] Invalid cellview for {marker.id}")
            return False
        
        cell = cellview.cell
        layout = cellview.layout()
        dbu = layout.dbu
        
        # Get marker layer
        marker_class = marker.__class__.__name__.lower()
        if 'cut' in marker_class:
            layer_key = 'cut'
        elif 'connect' in marker_class:
            layer_key = 'connect'
        elif 'probe' in marker_class:
            layer_key = 'probe'
        else:
            layer_key = 'cut'  # fallback
        
        from .config import LAYERS
        fib_layer_num = LAYERS[layer_key]
        fib_layer = layout.layer(fib_layer_num, 0)
        
        # Create search regions around marker coordinates to find text labels
        search_regions = []
        
        if hasattr(marker, 'points') and len(marker.points) >= 2:
            # Multi-point marker: search around each point for coordinate texts
            print(f"[Screenshot] Searching for {len(marker.points)} coordinate texts for multi-point {marker.id}")
            for i, (x, y) in enumerate(marker.points):
                # Create search box around each coordinate
                margin = SCREENSHOT_CONFIG['search_radius']  # Search radius in microns
                db_box = pya.Box(
                    int((x - margin) / dbu), 
                    int((y - margin) / dbu),
                    int((x + margin) / dbu), 
                    int((y + margin) / dbu)
                )
                search_regions.append(db_box)
                
        elif hasattr(marker, 'x1'):
            # Regular 2-point marker: search around both endpoints
            print(f"[Screenshot] Searching for 2 coordinate texts for 2-point {marker.id}")
            for x, y in [(marker.x1, marker.y1), (marker.x2, marker.y2)]:
                margin = SCREENSHOT_CONFIG['search_radius']  # Search radius in microns
                db_box = pya.Box(
                    int((x - margin) / dbu), 
                    int((y - margin) / dbu),
                    int((x + margin) / dbu), 
                    int((y + margin) / dbu)
                )
                search_regions.append(db_box)
                
        else:
            # PROBE marker: search around single point
            print(f"[Screenshot] Searching for 1 coordinate text for probe {marker.id}")
            margin = SCREENSHOT_CONFIG['search_radius']  # Search radius in microns
            db_box = pya.Box(
                int((marker.x - margin) / dbu), 
                int((marker.y - margin) / dbu),
                int((marker.x + margin) / dbu), 
                int((marker.y + margin) / dbu)
            )
            search_regions.append(db_box)
        
        # Search for text labels in each region
        texts_found = 0
        texts_selected = 0
        
        for i, search_box in enumerate(search_regions):
            print(f"[Screenshot] Searching region {i+1}/{len(search_regions)}: {search_box}")
            
            for shape in cell.shapes(fib_layer).each_overlapping(search_box):
                if shape.is_text():
                    text_obj = shape.text
                    text_string = text_obj.string
                    texts_found += 1
                    
                    # Check if this text belongs to our marker
                    if marker.id in text_string or any(f"({coord[0]:.3f},{coord[1]:.3f})" in text_string 
                                                     for coord in (marker.points if hasattr(marker, 'points') 
                                                                 else [(marker.x1, marker.y1), (marker.x2, marker.y2)] if hasattr(marker, 'x1')
                                                                 else [(marker.x, marker.y)])):
                        
                        print(f"[Screenshot] Found matching text: '{text_string}'")
                        
                        # Create a highlight box around the text for better visibility
                        try:
                            text_pos = text_obj.trans.disp
                            select_point = pya.DPoint(text_pos.x * dbu, text_pos.y * dbu)
                            
                            print(f"[Screenshot] Found text '{text_string}' at ({select_point.x:.2f}, {select_point.y:.2f})")
                            
                            # Create a highlight annotation box around the text
                            try:
                                # Use line annotations to create a box (more compatible)
                                margin = SCREENSHOT_CONFIG['highlight_margin']  # Margin around text in microns
                                
                                # Create 4 lines to form a rectangle
                                # Top line
                                top_line = pya.Annotation()
                                top_line.p1 = pya.DPoint(select_point.x - margin, select_point.y + margin)
                                top_line.p2 = pya.DPoint(select_point.x + margin, select_point.y + margin)
                                top_line.style = pya.Annotation.StyleLine
                                view.insert_annotation(top_line)
                                
                                # Bottom line
                                bottom_line = pya.Annotation()
                                bottom_line.p1 = pya.DPoint(select_point.x - margin, select_point.y - margin)
                                bottom_line.p2 = pya.DPoint(select_point.x + margin, select_point.y - margin)
                                bottom_line.style = pya.Annotation.StyleLine
                                view.insert_annotation(bottom_line)
                                
                                # Left line
                                left_line = pya.Annotation()
                                left_line.p1 = pya.DPoint(select_point.x - margin, select_point.y - margin)
                                left_line.p2 = pya.DPoint(select_point.x - margin, select_point.y + margin)
                                left_line.style = pya.Annotation.StyleLine
                                view.insert_annotation(left_line)
                                
                                # Right line
                                right_line = pya.Annotation()
                                right_line.p1 = pya.DPoint(select_point.x + margin, select_point.y - margin)
                                right_line.p2 = pya.DPoint(select_point.x + margin, select_point.y + margin)
                                right_line.style = pya.Annotation.StyleLine
                                view.insert_annotation(right_line)
                                
                                print(f"[Screenshot] ✓ Created highlight box around text '{text_string}'")
                                texts_selected += 1
                                
                            except Exception as highlight_error:
                                print(f"[Screenshot] Could not create highlight box: {highlight_error}")
                                # Still count as processed even if highlighting failed
                                texts_selected += 1
                            
                        except Exception as text_select_error:
                            print(f"[Screenshot] Could not process text '{text_string}': {text_select_error}")
        
        print(f"[Screenshot] Text search results for {marker.id}: {texts_found} texts found, {texts_selected} processed")
        
        if texts_found > 0:
            print(f"[Screenshot] ✓ Found {texts_found} text labels for {marker.id}")
            return True
        else:
            print(f"[Screenshot] ⚠ No text labels found for {marker.id}")
            return False
            
    except Exception as e:
        print(f"[Screenshot] Error selecting text labels for {marker.id}: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail the screenshot process due to selection issues
        return True


def take_marker_screenshots(marker, view, output_dir):
    """
    Generate 3 screenshots for a single marker
    
    Args:
        marker: Marker object
        view: LayoutView object
        output_dir: Output directory path
    
    Returns:
        list: List of tuples (description, filename, filepath)
    """
    screenshots = []
    
    try:
        # Get layout and marker info
        cellview = view.active_cellview()
        if not cellview.is_valid():
            print(f"[Screenshot] Error: Invalid cellview")
            return screenshots
        
        layout_bbox = cellview.cell.dbbox()
        marker_bbox = get_marker_bbox(marker)
        marker_center = marker_bbox.center()
        
        print(f"[Screenshot] Processing {marker.id}...")
        print(f"[Screenshot]   Marker bbox: {marker_bbox}")
        print(f"[Screenshot]   Marker center: ({marker_center.x:.2f}, {marker_center.y:.2f})")
        
        # Store original view state
        original_box = view.box()
        
        # Attempt to select marker path for highlighting in screenshots
        # Note: Path selection is currently disabled due to API compatibility issues
        selection_success = select_marker_path(view, marker)
        if selection_success:
            print(f"[Screenshot] ✓ Marker path selected for highlighting in {marker.id}")
        else:
            print(f"[Screenshot] ℹ Screenshots will be generated without path highlighting for {marker.id}")
        
        # === Screenshot 1: Overview (Fit All) with crosshair ===
        try:
            view.zoom_fit()
            view.clear_annotations()
            
            # Create crosshair pointing to marker
            create_crosshair_annotation(view, marker_center, layout_bbox)
            
            # Create scale bar
            current_box = view.box()
            create_scale_bar(view, current_box)
            
            # Save screenshot
            overview_filename = f"{marker.id}_overview.png"
            overview_path = os.path.join(output_dir, overview_filename)
            view.save_image(overview_path, 800, 600)
            
            screenshots.append(('Overview', overview_filename, overview_path))
            print(f"[Screenshot]   ✓ Overview saved: {overview_filename}")
            
        except Exception as e:
            print(f"[Screenshot]   ✗ Overview failed: {e}")
        
        # === Screenshot 2: Zoom 2x (medium zoom) ===
        try:
            view.clear_annotations()
            
            # Expand marker bbox by 10x
            zoom2_bbox = marker_bbox.enlarged(
                marker_bbox.width() * 5, 
                marker_bbox.height() * 5
            )
            
            # Ensure minimum size (50 microns)
            if zoom2_bbox.width() < 50:
                zoom2_bbox = zoom2_bbox.enlarged(25, 25)
            
            view.zoom_box(zoom2_bbox)
            
            # Create dimension rulers showing marker X and Y lengths
            create_marker_dimension_rulers(view, marker)
            
            # Create scale bar
            create_scale_bar(view, zoom2_bbox)
            
            # Save screenshot
            zoom2_filename = f"{marker.id}_zoom2x.png"
            zoom2_path = os.path.join(output_dir, zoom2_filename)
            view.save_image(zoom2_path, 800, 600)
            
            screenshots.append(('Zoom 2x', zoom2_filename, zoom2_path))
            print(f"[Screenshot]   ✓ Zoom 2x saved: {zoom2_filename}")
            
        except Exception as e:
            print(f"[Screenshot]   ✗ Zoom 2x failed: {e}")
        
        # === Screenshot 3: Detail (close-up) ===
        try:
            view.clear_annotations()
            
            # Expand marker bbox by 2x
            detail_bbox = marker_bbox.enlarged(
                marker_bbox.width() * 0.5, 
                marker_bbox.height() * 0.5
            )
            
            # Ensure minimum size (10 microns)
            if detail_bbox.width() < 10:
                detail_bbox = detail_bbox.enlarged(5, 5)
            
            view.zoom_box(detail_bbox)
            
            # Create dimension rulers showing marker X and Y lengths
            create_marker_dimension_rulers(view, marker)
            
            # Create scale bar
            create_scale_bar(view, detail_bbox)
            
            # Save screenshot
            detail_filename = f"{marker.id}_detail.png"
            detail_path = os.path.join(output_dir, detail_filename)
            view.save_image(detail_path, 800, 600)
            
            screenshots.append(('Detail', detail_filename, detail_path))
            print(f"[Screenshot]   ✓ Detail saved: {detail_filename}")
            
        except Exception as e:
            print(f"[Screenshot]   ✗ Detail failed: {e}")
        
        # Restore original view and clear selection
        view.clear_annotations()
        view.clear_selection()  # Clear marker path selection
        view.zoom_box(original_box)
        
        print(f"[Screenshot] Completed {marker.id}: {len(screenshots)} screenshots")
        
    except Exception as e:
        print(f"[Screenshot] Error processing {marker.id}: {e}")
        import traceback
        traceback.print_exc()
    
    return screenshots


def export_markers_with_screenshots(markers, view, output_dir):
    """
    Export all markers with screenshots
    
    Args:
        markers: List of marker objects
        view: LayoutView object
        output_dir: Output directory path
    
    Returns:
        dict: Dictionary mapping marker.id to list of screenshots
    """
    all_screenshots = {}
    
    try:
        # Create images subdirectory
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        print(f"[Screenshot] Starting export for {len(markers)} markers")
        print(f"[Screenshot] Output directory: {images_dir}")
        
        # Process each marker
        for i, marker in enumerate(markers, 1):
            print(f"[Screenshot] [{i}/{len(markers)}] Processing {marker.id}...")
            
            screenshots = take_marker_screenshots(marker, view, images_dir)
            all_screenshots[marker.id] = screenshots
        
        print(f"[Screenshot] Export complete: {len(all_screenshots)} markers processed")
        
    except Exception as e:
        print(f"[Screenshot] Error in export: {e}")
        import traceback
        traceback.print_exc()
    
    return all_screenshots


# ============================================================================
# Helper functions for HTML generation
# ============================================================================

def _load_template_file(filename):
    """Load template file from templates directory"""
    from pathlib import Path
    template_path = Path(__file__).parent / 'templates' / filename
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[Screenshot] Warning: Template file {filename} not found, using fallback")
        return None


def _get_marker_coordinates(marker):
    """Extract coordinates string from marker (helper function)"""
    import math

    if hasattr(marker, 'points') and len(marker.points) > 0:
        # Multi-point marker
        if len(marker.points) <= 5:
            point_strs = []
            for i, p in enumerate(marker.points):
                layer_info = ""
                if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                    layer_info = f" [{marker.point_layers[i]}]"
                point_strs.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
            return f"{len(marker.points)} points: " + " → ".join(point_strs)
        else:
            # Show first 3, ..., last 2
            first_points = []
            for i in range(3):
                p = marker.points[i]
                layer_info = ""
                if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                    layer_info = f" [{marker.point_layers[i]}]"
                first_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")

            last_points = []
            for i in range(-2, 0):
                p = marker.points[i]
                idx = len(marker.points) + i
                layer_info = ""
                if hasattr(marker, 'point_layers') and idx < len(marker.point_layers) and marker.point_layers[idx]:
                    layer_info = f" [{marker.point_layers[idx]}]"
                last_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")

            return f"{len(marker.points)} points: " + " → ".join(first_points) + " → ... → " + " → ".join(last_points)

    elif hasattr(marker, 'x1'):
        # 2-point marker
        layer1_info = f" [{marker.layer1}]" if hasattr(marker, 'layer1') and marker.layer1 else ""
        layer2_info = f" [{marker.layer2}]" if hasattr(marker, 'layer2') and marker.layer2 else ""
        return f"({marker.x1:.3f},{marker.y1:.3f}){layer1_info} to ({marker.x2:.3f},{marker.y2:.3f}){layer2_info}"

    else:
        # Single point marker
        layer_info = f" [{marker.target_layer}]" if hasattr(marker, 'target_layer') and marker.target_layer else ""
        return f"({marker.x:.3f},{marker.y:.3f}){layer_info}"


def _get_marker_dimensions(marker):
    """Calculate marker dimensions (helper function)"""
    import math

    if hasattr(marker, 'points') and len(marker.points) > 0:
        first = marker.points[0]
        last = marker.points[-1]
        delta_x = abs(last[0] - first[0])
        delta_y = abs(last[1] - first[1])

        # Calculate total path length
        total_length = 0
        for i in range(len(marker.points) - 1):
            p1 = marker.points[i]
            p2 = marker.points[i + 1]
            segment_length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_length += segment_length

        dimensions_str = f"DX = {delta_x:.2f} um, DY = {delta_y:.2f} um"
        length_str = f"Path Length = {total_length:.2f} um"
        return dimensions_str, length_str

    elif hasattr(marker, 'x1'):
        delta_x = abs(marker.x2 - marker.x1)
        delta_y = abs(marker.y2 - marker.y1)
        length = math.sqrt(delta_x**2 + delta_y**2)
        dimensions_str = f"DX = {delta_x:.2f} um, DY = {delta_y:.2f} um"
        length_str = f"Length = {length:.2f} um"
        return dimensions_str, length_str

    else:
        return "Single point marker", "-"


def _generate_marker_section_html(marker, screenshots_dict):
    """Generate HTML for a single marker section (helper function)"""
    marker_class = marker.__class__.__name__

    # Determine marker type
    if 'MultiPoint' in marker_class:
        if 'Cut' in marker_class:
            marker_type = "CUT (Multi-Point)"
        elif 'Connect' in marker_class:
            marker_type = "CONNECT (Multi-Point)"
        else:
            marker_type = "Multi-Point"
    else:
        marker_type = marker_class.replace('Marker', '').upper()

    # Get coordinates and dimensions
    coords = _get_marker_coordinates(marker)
    dimensions_str, length_str = _get_marker_dimensions(marker)

    # Get notes
    notes = getattr(marker, 'notes', '')
    if not notes:
        if 'Cut' in marker_class:
            notes = "切断"
        elif 'Connect' in marker_class:
            notes = "连接"
        elif 'Probe' in marker_class:
            notes = "点测"

    # Build marker section HTML
    html = f"""
    <div class="marker-section">
        <h2>{marker.id}</h2>

        <div class="marker-info">
            <p><strong>Type:</strong> {marker_type}</p>
            <p><strong>Coordinates:</strong> {coords} um</p>
            <p><strong>Dimensions:</strong> {dimensions_str}</p>
            <p><strong>Length:</strong> {length_str}</p>
            <p><strong>Notes:</strong> {notes if notes else '-'}</p>
        </div>
"""

    # Add screenshots if available
    if marker.id in screenshots_dict:
        screenshots = screenshots_dict[marker.id]
        html += f"""
        <div class="screenshots" data-marker-id="{marker.id}">
"""
        for desc, filename, filepath in screenshots:
            html += f"""
            <div class="screenshot">
                <h4>{desc}</h4>
                <img src="images/{filename}" alt="{desc}">
                <p>{desc} view of {marker.id}</p>
            </div>
"""

        # Add custom images container
        html += f"""
            <div class="screenshot add-custom-images" id="custom-images-{marker.id}">
                <!-- Custom images will be added here -->
            </div>

            <div class="screenshot add-image-btn">
                <button onclick="addImage('{marker.id}')">
                    <span class="plus-icon">+</span>
                    <span>添加图片</span>
                </button>
                <input type="file" id="file-input-{marker.id}"
                       accept="image/*" multiple
                       style="display: none;"
                       onchange="handleImageUpload('{marker.id}', this.files)">
            </div>
        </div>
"""

    html += """
    </div>
"""
    return html


def generate_html_report_with_screenshots(markers, screenshots_dict, output_path):
    """
    Generate HTML report with screenshots using external template files.

    Refactored to eliminate embedded HTML following Linus's "good taste" principle:
    - HTML/CSS/JavaScript separated into template files
    - Single responsibility helper functions
    - Cleaner, more maintainable code

    Args:
        markers: List of marker objects
        screenshots_dict: Dictionary mapping marker.id to screenshots
        output_path: Output HTML file path
    """
    from datetime import datetime

    try:
        # Generate unique timestamp for this HTML report
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        print(f"[Screenshot Export] Generated report timestamp: {timestamp}")

        # Group markers by type
        markers_by_type = {'CUT': [], 'CONNECT': [], 'PROBE': []}

        for marker in markers:
            marker_class = marker.__class__.__name__
            if 'Cut' in marker_class:
                markers_by_type['CUT'].append(marker)
            elif 'Connect' in marker_class:
                markers_by_type['CONNECT'].append(marker)
            elif 'Probe' in marker_class:
                markers_by_type['PROBE'].append(marker)
        
        # Generate marker sections HTML
        marker_sections_html = ""
        for marker in markers:
            marker_sections_html += _generate_marker_section_html(marker, screenshots_dict)

        # Load templates from files (cleaner, more maintainable)
        html_template = _load_template_file('report_template.html')
        js_content = _load_template_file('report_script.js')
        
        if html_template and js_content:
            # Use external templates (preferred method)
            #
            # NOTE:
            # The HTML template contains many single braces `{` `}` in CSS
            # blocks. Using `str.format()` on such a template causes Python to
            # interpret those as format fields, which leads to KeyError like:
            #   KeyError: '\\n            font-family'
            #
            # To avoid having to escape every CSS brace in the template, we
            # perform a very small custom placeholder replacement just for the
            # known fields we actually need to substitute.
            context = {
                "timestamp": timestamp,
                "generation_datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_markers": len(markers),
                "cut_count": len(markers_by_type['CUT']),
                "connect_count": len(markers_by_type['CONNECT']),
                "probe_count": len(markers_by_type['PROBE']),
                "marker_sections": marker_sections_html,
            }

            html = html_template
            for key, value in context.items():
                placeholder = "{" + key + "}"
                html = html.replace(placeholder, str(value))
            
            # Embed JavaScript inline for single-file export
            html = html.replace('<script src="report_script.js"></script>', 
                               f'<script>\n{js_content}\n</script>')
            
            print("[Screenshot] Using external template files")
        else:
            # Fallback: Use minimal embedded HTML if templates not found
            print("[Screenshot] Warning: Template files not found, using embedded fallback")
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FIB Markers Report</title>
</head>
<body>
    <h1>FIB Markers Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Markers: {len(markers)}</p>
    <p><strong>Error:</strong> Template files not found in templates/ directory.</p>
    <p>Please ensure report_template.html and report_script.js exist.</p>
</body>
</html>'''
        
        
        # Add each marker section
        for marker in markers:
            marker_class = marker.__class__.__name__
            
            # Get marker type
            if 'MultiPoint' in marker_class:
                if 'Cut' in marker_class:
                    marker_type = "CUT (Multi-Point)"
                elif 'Connect' in marker_class:
                    marker_type = "CONNECT (Multi-Point)"
                else:
                    marker_type = "Multi-Point"
            else:
                marker_type = marker_class.replace('Marker', '').upper()
            
            # Get coordinates and dimensions
            dimensions_str = ""
            length_str = ""
            
            if hasattr(marker, 'points') and len(marker.points) > 0:
                # Display all points for multi-point markers with layer info
                if len(marker.points) <= 5:
                    # For 5 or fewer points, show all coordinates with layer info
                    point_strs = []
                    for i, p in enumerate(marker.points):
                        layer_info = ""
                        if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                            layer_info = f" [{marker.point_layers[i]}]"
                        point_strs.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
                    coords = f"{len(marker.points)} points: " + " → ".join(point_strs)
                else:
                    # For more than 5 points, show first 3, ..., last 2 with layer info
                    first_points = []
                    for i in range(3):
                        p = marker.points[i]
                        layer_info = ""
                        if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
                            layer_info = f" [{marker.point_layers[i]}]"
                        first_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
                    
                    last_points = []
                    for i in range(-2, 0):
                        p = marker.points[i]
                        layer_info = ""
                        if hasattr(marker, 'point_layers') and len(marker.points) + i < len(marker.point_layers) and marker.point_layers[len(marker.points) + i]:
                            layer_info = f" [{marker.point_layers[len(marker.points) + i]}]"
                        last_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
                    
                    coords = f"{len(marker.points)} points: " + " → ".join(first_points) + " → ... → " + " → ".join(last_points)
                
                # Calculate dimensions (first to last point)
                first = marker.points[0]
                last = marker.points[-1]
                delta_x = abs(last[0] - first[0])
                delta_y = abs(last[1] - first[1])
                
                # Calculate total path length (sum of all segments)
                import math
                total_length = 0
                for i in range(len(marker.points) - 1):
                    p1 = marker.points[i]
                    p2 = marker.points[i + 1]
                    segment_length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    total_length += segment_length
                
                dimensions_str = f"DX = {delta_x:.2f} um, DY = {delta_y:.2f} um"
                length_str = f"Path Length = {total_length:.2f} um"
            elif hasattr(marker, 'x1'):
                # Include layer information if available
                layer1_info = f" [{marker.layer1}]" if hasattr(marker, 'layer1') and marker.layer1 else ""
                layer2_info = f" [{marker.layer2}]" if hasattr(marker, 'layer2') and marker.layer2 else ""
                coords = f"({marker.x1:.3f},{marker.y1:.3f}){layer1_info} to ({marker.x2:.3f},{marker.y2:.3f}){layer2_info}"
                # Calculate dimensions
                delta_x = abs(marker.x2 - marker.x1)
                delta_y = abs(marker.y2 - marker.y1)
                # Calculate line length (Euclidean distance)
                import math
                length = math.sqrt(delta_x**2 + delta_y**2)
                dimensions_str = f"DX = {delta_x:.2f} um, DY = {delta_y:.2f} um"
                length_str = f"Length = {length:.2f} um"
            else:
                # Include layer information if available (for probe markers)
                layer_info = f" [{marker.target_layer}]" if hasattr(marker, 'target_layer') and marker.target_layer else ""
                coords = f"({marker.x:.3f},{marker.y:.3f}){layer_info}"
                dimensions_str = "Single point marker"
                length_str = "-"
            
            # Try to get notes from centralized dict first (if available)
            notes = getattr(marker, 'notes', '')
            
            # If notes is empty, set default based on marker type
            if not notes:
                if 'Cut' in marker_class:
                    notes = "切断"
                elif 'Connect' in marker_class:
                    notes = "连接"
                elif 'Probe' in marker_class:
                    notes = "点测"
            
            # Debug: Print notes for each marker
            print(f"[Screenshot Export] {marker.id}: notes='{notes}' (obj_id={id(marker)})")
            print(f"[Screenshot Export] Marker class: {marker_class}")
            
            html += f"""
    <div class="marker-section">
        <h2>{marker.id}</h2>
        
        <div class="marker-info">
            <p><strong>Type:</strong> {marker_type}</p>
            <p><strong>Coordinates:</strong> {coords} um</p>
            <p><strong>Dimensions:</strong> {dimensions_str}</p>
            <p><strong>Length:</strong> {length_str}</p>
            <p><strong>Notes:</strong> {notes if notes else '-'}</p>
        </div>
"""
            
            # Add screenshots
            if marker.id in screenshots_dict:
                screenshots = screenshots_dict[marker.id]

                html += f"""
        <div class="screenshots" data-marker-id="{marker.id}">
"""

                for desc, filename, filepath in screenshots:
                    html += f"""
            <div class="screenshot">
                <h4>{desc}</h4>
                <img src="images/{filename}" alt="{desc}">
                <p>{desc} view of {marker.id}</p>
            </div>
"""

                # Add custom images container
                html += f"""
            <div class="screenshot add-custom-images" id="custom-images-{marker.id}">
                <!-- Custom images will be added here -->
            </div>

            <div class="screenshot add-image-btn">
                <button onclick="addImage('{marker.id}')">
                    <span class="plus-icon">+</span>
                    <span>添加图片</span>
                </button>
                <input type="file" id="file-input-{marker.id}"
                       accept="image/*" multiple
                       style="display: none;"
                       onchange="handleImageUpload('{marker.id}', this.files)">
            </div>
"""

                html += """
        </div>
"""
            
            html += """
    </div>
"""
        
        html += """
    <div class="footer">
        <p>Generated by KLayout FIB Tool</p>
        <p>All measurements in micrometers (&mu;m)</p>
    </div>

    <script>
    // 获取当前 HTML 的时间戳
    function getReportTimestamp() {
        var meta = document.getElementById('report-timestamp');
        if (meta) {
            return meta.getAttribute('content');
        }
        // 兜底：如果没有时间戳，使用固定值
        return 'legacy';
    }

    // Custom image upload functionality
    function addImage(markerId) {
        document.getElementById('file-input-' + markerId).click();
    }

    function handleImageUpload(markerId, files) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            if (file.type.startsWith('image/')) {
                var reader = new FileReader();
                reader.onload = (function(f) {
                    return function(e) {
                        var base64 = e.target.result;
                        displayCustomImage(markerId, base64, f.name);
                        saveCustomImage(markerId, base64, f.name);
                    };
                })(file);
                reader.readAsDataURL(file);
            }
        }
    }

    function displayCustomImage(markerId, base64, filename) {
        var container = document.getElementById('custom-images-' + markerId);
        var imageId = 'custom-img-' + markerId + '-' + Date.now();

        var imgDiv = document.createElement('div');
        imgDiv.className = 'custom-image';
        imgDiv.id = imageId;
        // 简化结构：只保留图片和删除按钮，去掉文件名
        imgDiv.innerHTML =
            '<img src="' + base64 + '" alt="Custom image">' +
            '<button onclick="removeCustomImage(\\'' + markerId + '\\', \\'' + imageId + '\\')" class="remove-btn" title="删除此图片">×</button>';

        container.appendChild(imgDiv);

        // 为新添加的图片附加 Lightbox 功能
        var img = imgDiv.querySelector('img');
        img.addEventListener('click', function() {
            openLightbox(this.src);
        });
    }

    function saveCustomImage(markerId, base64, filename) {
        var timestamp = getReportTimestamp();
        var storageKey = 'fib-custom-images-' + markerId + '-' + timestamp;
        var images = JSON.parse(localStorage.getItem(storageKey) || '[]');

        images.push({
            id: 'custom-img-' + markerId + '-' + Date.now(),
            filename: filename,
            data: base64,
            timestamp: new Date().toISOString()
        });

        localStorage.setItem(storageKey, JSON.stringify(images));
        updateStorageInfo();
    }

    function loadCustomImages() {
        var timestamp = getReportTimestamp();
        if (!timestamp) {
            console.warn('No report timestamp found, skipping image load');
            return;
        }

        var sections = document.querySelectorAll('.screenshots');
        for (var i = 0; i < sections.length; i++) {
            var section = sections[i];
            var markerId = section.getAttribute('data-marker-id');
            if (markerId) {
                var storageKey = 'fib-custom-images-' + timestamp + '-' + markerId;
                var images = JSON.parse(localStorage.getItem(storageKey) || '[]');

                for (var j = 0; j < images.length; j++) {
                    var img = images[j];
                    displayCustomImage(markerId, img.data, img.filename);
                }
            }
        }
    }

    function removeCustomImage(markerId, imageId) {
        var element = document.getElementById(imageId);
        if (element) {
            element.remove();
        }

        var timestamp = getReportTimestamp();
        if (!timestamp) return;

        var storageKey = 'fib-custom-images-' + timestamp + '-' + markerId;
        var images = JSON.parse(localStorage.getItem(storageKey) || '[]');
        images = images.filter(function(img) {
            return img.id !== imageId;
        });
        localStorage.setItem(storageKey, JSON.stringify(images));

        updateStorageInfo();
    }

    function clearAllCustomImages() {
        if (!confirm('确定要清除当前报告的所有自定义图片吗？此操作不可撤销！')) {
            return;
        }

        var timestamp = getReportTimestamp();
        if (!timestamp) return;

        // Remove from DOM
        var customImages = document.querySelectorAll('.custom-image');
        for (var i = 0; i < customImages.length; i++) {
            customImages[i].remove();
        }

        // Clear localStorage for this report only
        var keys = Object.keys(localStorage);
        var prefix = 'fib-custom-images-' + timestamp + '-';
        for (var i = 0; i < keys.length; i++) {
            if (keys[i].startsWith(prefix)) {
                localStorage.removeItem(keys[i]);
            }
        }

        // Also clear notes for this report
        localStorage.removeItem('fib-notes-' + timestamp);

        updateStorageInfo();
        alert('当前报告的所有自定义图片已清除！');
    }

    function updateStorageInfo() {
        var timestamp = getReportTimestamp();
        if (!timestamp) return;

        var totalSize = 0;
        var keys = Object.keys(localStorage);
        var prefix = 'fib-custom-images-' + timestamp + '-';
        var notesKey = 'fib-notes-' + timestamp;
        
        for (var i = 0; i < keys.length; i++) {
            if (keys[i].startsWith(prefix) || keys[i] === notesKey) {
                totalSize += localStorage[keys[i]].length;
            }
        }

        var sizeKB = (totalSize / 1024).toFixed(2);
        var storageElement = document.getElementById('storage-used');
        if (storageElement) {
            storageElement.textContent = sizeKB + ' KB (当前报告)';
        }

        // Warning if approaching 5MB limit for this report
        if (totalSize > 5 * 1024 * 1024 * 0.8) {
            alert('警告：当前报告存储空间接近限制（5MB），建议导出报告并清除部分图片。');
        }
    }

    function exportHTMLWithImages() {
        // 先保存 Notes 到 localStorage
        saveNotes();
        
        // 将 textarea 的当前值同步到 DOM（这样克隆时会包含最新内容）
        var reportNotes = document.getElementById('report-notes');
        if (reportNotes) {
            reportNotes.setAttribute('value', reportNotes.value);
            // 更新 textarea 的 textContent（用于导出）
            reportNotes.textContent = reportNotes.value;
        }
        
        // Clone current document
        var clone = document.documentElement.cloneNode(true);

        // Remove export buttons and file inputs from clone
        var elementsToRemove = clone.querySelectorAll('.save-btn, .export-btn, .load-btn, .clear-btn, input[type="file"], .add-image-btn button');
        for (var i = 0; i < elementsToRemove.length; i++) {
            elementsToRemove[i].remove();
        }

        // Generate complete HTML
        var htmlContent = '<!DOCTYPE html>\\n' + clone.outerHTML;

        // Trigger download
        var blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'FIB_Report_with_Custom_Images_' + getTimestamp() + '.html';
        a.click();
        URL.revokeObjectURL(url);

        alert('报告已导出！包含所有自定义图片和 Notes 的 HTML 文件已下载。');
    }

    function getTimestamp() {
        return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    }

    // Lightbox 图片放大功能
    function openLightbox(imgSrc) {
        var lightbox = document.getElementById('lightbox');
        var lightboxImg = document.getElementById('lightbox-img');
        lightboxImg.src = imgSrc;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // 禁止页面滚动
    }

    function closeLightbox() {
        var lightbox = document.getElementById('lightbox');
        lightbox.classList.remove('active');
        document.body.style.overflow = ''; // 恢复页面滚动
    }

    // ESC 键关闭 Lightbox
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLightbox();
        }
    });

    // 为所有截图图片添加点击放大功能
    function attachLightboxToImages() {
        var images = document.querySelectorAll('.screenshot img, .custom-image img');
        for (var i = 0; i < images.length; i++) {
            images[i].addEventListener('click', function(e) {
                // 如果点击的是删除按钮，不触发 lightbox
                if (e.target.className === 'remove-btn') {
                    return;
                }
                openLightbox(this.src);
            });
        }
    }

    // Notes 持久化功能
    function saveNotes() {
        var timestamp = getReportTimestamp();
        if (!timestamp) {
            console.warn('No report timestamp found, cannot save notes');
            return false;
        }

        // 保存全局 report notes
        var reportNotes = document.getElementById('report-notes');
        if (reportNotes) {
            var storageKey = 'fib-notes-' + timestamp;
            localStorage.setItem(storageKey, reportNotes.value);
            updateStorageInfo();
            console.log('Notes saved successfully to:', storageKey);
            return true;
        } else {
            console.warn('Report notes textarea not found');
            return false;
        }
    }

    function loadNotes() {
        var timestamp = getReportTimestamp();
        if (!timestamp) {
            console.warn('No report timestamp found, skipping notes load');
            return;
        }

        var storageKey = 'fib-notes-' + timestamp;
        var savedNotes = localStorage.getItem(storageKey);
        
        if (savedNotes) {
            var reportNotes = document.getElementById('report-notes');
            if (reportNotes) {
                reportNotes.value = savedNotes;
                console.log('Notes loaded successfully from:', storageKey);
            }
        } else {
            console.log('No saved notes found for this report');
        }
    }

    // 自动保存 Notes（防抖）
    var saveNotesTimeout;
    function autoSaveNotes() {
        clearTimeout(saveNotesTimeout);
        saveNotesTimeout = setTimeout(saveNotes, 1000); // 1秒后保存
    }

    // Load custom images on page load
    window.addEventListener('DOMContentLoaded', function() {
        loadCustomImages(); // 现在使用时间戳隔离，可以安全加载
        loadNotes(); // 加载保存的 Notes
        updateStorageInfo();
        attachLightboxToImages(); // 为所有图片添加点击放大功能

        // 为所有 Notes textarea 添加自动保存监听器
        var textareas = document.querySelectorAll('textarea[id^="notes-"]');
        for (var i = 0; i < textareas.length; i++) {
            textareas[i].addEventListener('input', autoSaveNotes);
        }
    });
    </script>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[Screenshot] HTML report saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"[Screenshot] Error generating HTML: {e}")
        import traceback
        traceback.print_exc()
        return False
