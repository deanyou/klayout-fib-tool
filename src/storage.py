"""
FIB Data Storage

Simple XML serialization. No fancy ORM, no schema validation.
Just read and write XML files.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Union
from markers import CutMarker, ConnectMarker, ProbeMarker


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
            # Each marker knows how to serialize itself
            marker_xml = ET.fromstring(marker.to_xml())
            markers_elem.append(marker_xml)
        
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
        
        # Dispatch to appropriate marker class based on tag name
        marker_types = {
            'cut': CutMarker.from_xml,
            'connect': ConnectMarker.from_xml,
            'probe': ProbeMarker.from_xml,
        }
        
        for elem in markers_elem:
            factory = marker_types.get(elem.tag)
            if factory:
                markers.append(factory(elem))
        
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
