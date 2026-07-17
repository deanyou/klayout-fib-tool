"""
FIB Data Storage

Simple XML serialization. No fancy ORM, no schema validation.
Just read and write XML files.
"""

import sys
import os

# Add the current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import xml.etree.ElementTree as ET
import json
from datetime import datetime
from typing import List, Union
from .markers import CutMarker, ConnectMarker, ProbeMarker
from .business.marker_codec import marker_from_record, marker_to_record


_FLOAT_FIELDS = {'x', 'y', 'x1', 'y1', 'x2', 'y2'}
_JSON_FIELDS = {'points', 'point_layers', 'screenshots', 'target_layers'}


def _record_to_element(record):
    elem = ET.Element(record['type'])
    for key, value in record.items():
        if key == 'type' or value is None:
            continue
        elem.set(key, json.dumps(value) if key in _JSON_FIELDS else str(value))
    return elem


def _element_to_record(elem):
    record = {'type': elem.tag}
    for key, value in elem.attrib.items():
        if key in _JSON_FIELDS:
            try:
                record[key] = json.loads(value)
            except json.JSONDecodeError:
                record[key] = value
        elif key in _FLOAT_FIELDS:
            record[key] = float(value)
        elif key == 'layer':
            record[key] = int(value)
        else:
            record[key] = value
    # Accept the original semicolon-separated multipoint XML representation.
    if isinstance(record.get('points'), str):
        record['points'] = [tuple(map(float, point.split(',')))
                            for point in record['points'].split(';') if point]
    return record


def save_markers(markers: List[Union[CutMarker, ConnectMarker, ProbeMarker]], 
                 filename: str, library: str, cell: str) -> bool:
    """
    Save markers to XML file.
    
    Returns True on success, False on failure.
    Early return pattern - no nested ifs.
    """
    if not markers or not filename:
        return True  # Nothing to save
    
    try:
        # Build XML tree
        root = ET.Element('fib_project', version='1.0')
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'library').text = library
        ET.SubElement(metadata, 'cell').text = cell
        ET.SubElement(metadata, 'created').text = datetime.now().isoformat()
        
        # Markers
        markers_elem = ET.SubElement(root, 'markers')
        for marker in markers:
            markers_elem.append(_record_to_element(marker_to_record(marker)))
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')  # Pretty print
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except (IOError, ET.ParseError) as e:
        print(f"Error saving markers: {e}")
        return False


def load_markers(filename: str) -> tuple:
    """
    Load markers from XML file.
    
    Returns (markers_list, library, cell) tuple.
    Returns ([], '', '') on failure.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Extract metadata
        metadata = root.find('metadata')
        library = metadata.find('library').text if metadata is not None else ''
        cell = metadata.find('cell').text if metadata is not None else ''
        
        # Extract markers
        markers = []
        markers_elem = root.find('markers')
        
        if markers_elem is None:
            return markers, library, cell
        
        for elem in markers_elem:
            try:
                markers.append(marker_from_record(_element_to_record(elem)))
            except (KeyError, TypeError, ValueError):
                continue
        
        return markers, library, cell
        
    except (IOError, ET.ParseError) as e:
        print(f"Error loading markers: {e}")
        return [], '', ''


def draw_markers_to_gds(markers: List[Union[CutMarker, ConnectMarker, ProbeMarker]], 
                        cell, layer_map: dict):
    """
    Draw all markers to GDS cell.
    
    Each marker type uses its own layer from layer_map.
    """
    if not markers:
        return
    
    layout = cell.layout()
    
    # Create layers if they don't exist
    fib_layers = {
        'cut': layout.layer(layer_map['cut'], 0),
        'connect': layout.layer(layer_map['connect'], 0),
        'probe': layout.layer(layer_map['probe'], 0),
    }
    
    # Each marker draws itself
    for marker in markers:
        marker_type = marker.__class__.__name__.lower().replace('marker', '')
        fib_layer = fib_layers.get(marker_type)
        if fib_layer is not None:
            marker.to_gds(cell, fib_layer)
