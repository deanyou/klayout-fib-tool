"""
FIB Report Generation

Simple HTML report. No Jinja2 for MVP - just string formatting.
Keep it simple, stupid.
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from datetime import datetime
from typing import List, Union
from pathlib import Path
import pya
from markers import CutMarker, ConnectMarker, ProbeMarker
from config import REPORT_TEMPLATE, SCREENSHOT_DPI, SCREENSHOT_MARGIN


def generate_report(markers: List[Union[CutMarker, ConnectMarker, ProbeMarker]],
                   library: str, cell: str, output_path: str, view) -> bool:
    """
    Generate HTML report with screenshots.
    
    Returns True on success, False on failure.
    """
    if not markers or not output_path:
        return False
    
    try:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate operations HTML
        operations_html = []
        for i, marker in enumerate(markers):
            op_html = _generate_operation_html(marker, i, output_dir, view)
            operations_html.append(op_html)
        
        # Fill template
        html = REPORT_TEMPLATE.format(
            library=library,
            cell=cell,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_ops=len(markers),
            operations_html='\n'.join(operations_html)
        )
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return True
        
    except (IOError, OSError) as e:
        print(f"Error generating report: {e}")
        return False


def _generate_operation_html(marker, index: int, output_dir: Path, view) -> str:
    """Generate HTML for single operation with screenshot"""
    
    # Get marker info
    marker_type = marker.__class__.__name__.replace('Marker', '')
    
    if isinstance(marker, CutMarker):
        position = f"({marker.x:.3f}, {marker.y:.3f})"
        details = f"Direction: {marker.direction}, Layer: {marker.layer}"
    elif isinstance(marker, ConnectMarker):
        position = f"({marker.x1:.3f}, {marker.y1:.3f}) → ({marker.x2:.3f}, {marker.y2:.3f})"
        details = f"Layer: {marker.layer}"
    elif isinstance(marker, ProbeMarker):
        position = f"({marker.x:.3f}, {marker.y:.3f})"
        details = f"Layer: {marker.layer}"
    else:
        position = "Unknown"
        details = ""
    
    # Take screenshot
    screenshot_file = f"{marker.id}.png"
    screenshot_path = output_dir / screenshot_file
    _take_screenshot(marker, screenshot_path, view)
    
    # Generate HTML
    html = f"""
    <div class="operation">
        <h3>{marker.id} - {marker_type}</h3>
        <p><strong>Position:</strong> {position}</p>
        <p><strong>Details:</strong> {details}</p>
        <img src="{screenshot_file}" alt="{marker.id}">
    </div>
    """
    
    return html


def _take_screenshot(marker, output_path: Path, view):
    """
    Take screenshot of marker area.
    
    Simple 1:1 zoom for MVP. No fancy multi-level views yet.
    """
    if view is None:
        return
    
    try:
        # Calculate bounding box around marker
        margin = SCREENSHOT_MARGIN
        
        if isinstance(marker, CutMarker):
            x, y = marker.x, marker.y
            bbox = pya.DBox(x - margin, y - margin, x + margin, y + margin)
        elif isinstance(marker, ConnectMarker):
            x1, y1, x2, y2 = marker.x1, marker.y1, marker.x2, marker.y2
            bbox = pya.DBox(
                min(x1, x2) - margin, min(y1, y2) - margin,
                max(x1, x2) + margin, max(y1, y2) + margin
            )
        elif isinstance(marker, ProbeMarker):
            x, y = marker.x, marker.y
            bbox = pya.DBox(x - margin, y - margin, x + margin, y + margin)
        else:
            return
        
        # Zoom to area and take screenshot
        view.zoom_box(bbox)
        view.save_image(str(output_path), SCREENSHOT_DPI)
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")
