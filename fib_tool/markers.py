"""
FIB Marker Classes

Simple dataclasses. No abstract base classes, no over-engineering.
Each marker knows how to draw itself and serialize to XML.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
import pya
from config import LAYERS, SYMBOL_SIZES


@dataclass
class CutMarker:
    """Cut operation marker - Line connecting two mouse click points"""
    id: str
    x1: float  # First click point
    y1: float
    x2: float  # Second click point
    y2: float
    layer: int
    # Layer info for each point (layer name or "layer/datatype" format)
    layer1: Optional[str] = None  # Layer at point 1
    layer2: Optional[str] = None  # Layer at point 2
    
    def to_gds(self, cell, fib_layer):
        """Draw line connecting the two click points with fixed width"""
        dbu = cell.layout().dbu
        fixed_width = SYMBOL_SIZES['cut']['line_width']
        width = int(fixed_width / dbu)  # Convert to database units
        
        # Convert coordinates to database units
        p1_x = int(self.x1 / dbu)
        p1_y = int(self.y1 / dbu)
        p2_x = int(self.x2 / dbu)
        p2_y = int(self.y2 / dbu)
        
        # Draw line connecting the two points
        pts = [pya.Point(p1_x, p1_y), pya.Point(p2_x, p2_y)]
        cell.shapes(fib_layer).insert(pya.Path(pts, width))
        
        # Draw label at the midpoint
        mid_x = int((p1_x + p2_x) / 2)
        mid_y = int((p1_y + p2_y) / 2)
        text = pya.Text(self.id, pya.Trans(pya.Point(mid_x, mid_y)))
        cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        layer1_attr = f' layer1="{self.layer1}"' if self.layer1 else ''
        layer2_attr = f' layer2="{self.layer2}"' if self.layer2 else ''
        return (f'<cut id="{self.id}" x1="{self.x1}" y1="{self.y1}" ' 
                f'x2="{self.x2}" y2="{self.y2}" layer="{self.layer}"{layer1_attr}{layer2_attr}/>')
    
    @staticmethod
    def from_xml(elem) -> 'CutMarker':
        """Deserialize from XML element"""
        marker = CutMarker(
            id=elem.get('id'),
            x1=float(elem.get('x1')),
            y1=float(elem.get('y1')),
            x2=float(elem.get('x2')),
            y2=float(elem.get('y2')),
            layer=int(elem.get('layer')),
            layer1=elem.get('layer1'),
            layer2=elem.get('layer2')
        )
        return marker


@dataclass
class ConnectMarker:
    """Connect operation marker - line with endpoints"""
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    layer: int
    # Layer info for each point (layer name or "layer/datatype" format)
    layer1: Optional[str] = None  # Layer at point 1
    layer2: Optional[str] = None  # Layer at point 2
    
    def to_gds(self, cell, fib_layer):
        """Draw connection line + endpoints + label on GDS using fixed width path"""
        dbu = cell.layout().dbu
        radius = SYMBOL_SIZES['connect']['endpoint_radius']
        fixed_width = SYMBOL_SIZES['connect']['line_width']
        width = int(fixed_width / dbu)  # Convert to database units
        
        # Convert to database units
        p1 = pya.Point(int(self.x1 / dbu), int(self.y1 / dbu))
        p2 = pya.Point(int(self.x2 / dbu), int(self.y2 / dbu))
        
        # Draw connection line with fixed width
        line = pya.Path([p1, p2], width)
        cell.shapes(fib_layer).insert(line)
        
        # Draw endpoint circles
        r = int(radius / dbu)
        circle1 = pya.Polygon.ellipse(pya.Box(p1.x - r, p1.y - r, p1.x + r, p1.y + r), 32)
        circle2 = pya.Polygon.ellipse(pya.Box(p2.x - r, p2.y - r, p2.x + r, p2.y + r), 32)
        cell.shapes(fib_layer).insert(circle1)
        cell.shapes(fib_layer).insert(circle2)
        
        # Record start and end coordinates (already stored in dataclass)
        self.start_x = self.x1
        self.start_y = self.y1
        self.end_x = self.x2
        self.end_y = self.y2
        
        # Draw label at midpoint
        mid_x = (p1.x + p2.x) // 2
        mid_y = (p1.y + p2.y) // 2
        text = pya.Text(self.id, pya.Trans(pya.Point(mid_x, mid_y)))
        cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        layer1_attr = f' layer1="{self.layer1}"' if self.layer1 else ''
        layer2_attr = f' layer2="{self.layer2}"' if self.layer2 else ''
        return (f'<connect id="{self.id}" x1="{self.x1}" y1="{self.y1}" ' 
                f'x2="{self.x2}" y2="{self.y2}" layer="{self.layer}" ' 
                f'start_x="{self.x1}" start_y="{self.y1}" ' 
                f'end_x="{self.x2}" end_y="{self.y2}"{layer1_attr}{layer2_attr}/>')
    
    @staticmethod
    def from_xml(elem) -> 'ConnectMarker':
        """Deserialize from XML element"""
        marker = ConnectMarker(
            id=elem.get('id'),
            x1=float(elem.get('x1')),
            y1=float(elem.get('y1')),
            x2=float(elem.get('x2')),
            y2=float(elem.get('y2')),
            layer=int(elem.get('layer')),
            layer1=elem.get('layer1'),
            layer2=elem.get('layer2')
        )
        return marker


@dataclass
class ProbeMarker:
    """Probe operation marker - circle"""
    id: str
    x: float
    y: float
    layer: int
    # Layer info at probe point (layer name or "layer/datatype" format)
    target_layer: Optional[str] = None  # Layer at probe point
    
    def to_gds(self, cell, fib_layer):
        """Draw circle + label on GDS using KLayout's circle tool"""
        dbu = cell.layout().dbu
        
        # Convert to database units
        cx = int(self.x / dbu)
        cy = int(self.y / dbu)
        
        # Draw circle instead of arrow
        circle_radius = SYMBOL_SIZES['probe']['circle_radius']
        r = int(circle_radius / dbu)  # Convert to database units
        circle = pya.Polygon.ellipse(pya.Box(cx - r, cy - r, cx + r, cy + r), 32)
        cell.shapes(fib_layer).insert(circle)
        
        # Record start and end coordinates (same as center for circle)
        self.start_x = self.x
        self.start_y = self.y
        self.end_x = self.x
        self.end_y = self.y
        
        # Draw label
        text = pya.Text(self.id, pya.Trans(pya.Point(cx, cy + r)))
        cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        target_layer_attr = f' target_layer="{self.target_layer}"' if self.target_layer else ''
        return (f'<probe id="{self.id}" x="{self.x}" y="{self.y}" layer="{self.layer}" ' 
                f'start_x="{self.x}" start_y="{self.y}" ' 
                f'end_x="{self.x}" end_y="{self.y}"{target_layer_attr}/>')
    
    @staticmethod
    def from_xml(elem) -> 'ProbeMarker':
        """Deserialize from XML element"""
        marker = ProbeMarker(
            id=elem.get('id'),
            x=float(elem.get('x')),
            y=float(elem.get('y')),
            layer=int(elem.get('layer')),
            target_layer=elem.get('target_layer')
        )
        return marker
