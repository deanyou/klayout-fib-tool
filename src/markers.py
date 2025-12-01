"""
FIB Marker Classes

Simple dataclasses. No abstract base classes, no over-engineering.
Each marker knows how to draw itself and serialize to XML.
"""

from dataclasses import dataclass
from typing import Tuple
import pya
from config import LAYERS, SYMBOL_SIZES


@dataclass
class CutMarker:
    """Cut operation marker - X symbol with direction arrow"""
    id: str
    x: float
    y: float
    direction: str  # "up", "down", "left", "right"
    layer: int
    
    def to_gds(self, cell, fib_layer):
        """Draw X symbol + arrow + label on GDS"""
        dbu = cell.layout().dbu
        size = SYMBOL_SIZES['cut']['size']
        arrow_len = SYMBOL_SIZES['cut']['arrow_length']
        width = int(SYMBOL_SIZES['cut']['line_width'] / dbu)
        
        # Convert to database units
        cx = int(self.x / dbu)
        cy = int(self.y / dbu)
        half = int(size / 2 / dbu)
        
        # Draw X symbol (two diagonal lines)
        pts1 = [pya.Point(cx - half, cy + half), pya.Point(cx + half, cy - half)]
        pts2 = [pya.Point(cx - half, cy - half), pya.Point(cx + half, cy + half)]
        cell.shapes(fib_layer).insert(pya.Path(pts1, width))
        cell.shapes(fib_layer).insert(pya.Path(pts2, width))
        
        # Draw direction arrow
        arrow_end = self._get_arrow_end(cx, cy, arrow_len, dbu)
        arrow_pts = [pya.Point(cx, cy), arrow_end]
        cell.shapes(fib_layer).insert(pya.Path(arrow_pts, width))
        
        # Draw label
        text = pya.Text(self.id, pya.Trans(arrow_end))
        cell.shapes(fib_layer).insert(text)
    
    def _get_arrow_end(self, cx, cy, arrow_len, dbu):
        """Calculate arrow endpoint based on direction"""
        offset = int(arrow_len / dbu)
        directions = {
            'up': pya.Point(cx, cy + offset),
            'down': pya.Point(cx, cy - offset),
            'left': pya.Point(cx - offset, cy),
            'right': pya.Point(cx + offset, cy),
        }
        return directions.get(self.direction, pya.Point(cx, cy - offset))
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        return (f'<cut id="{self.id}" x="{self.x}" y="{self.y}" '
                f'direction="{self.direction}" layer="{self.layer}"/>')
    
    @staticmethod
    def from_xml(elem) -> 'CutMarker':
        """Deserialize from XML element"""
        return CutMarker(
            id=elem.get('id'),
            x=float(elem.get('x')),
            y=float(elem.get('y')),
            direction=elem.get('direction'),
            layer=int(elem.get('layer'))
        )


@dataclass
class ConnectMarker:
    """Connect operation marker - line with endpoints"""
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    layer: int
    
    def to_gds(self, cell, fib_layer):
        """Draw connection line + endpoints + label on GDS"""
        dbu = cell.layout().dbu
        radius = SYMBOL_SIZES['connect']['endpoint_radius']
        width = int(SYMBOL_SIZES['connect']['line_width'] / dbu)
        
        # Convert to database units
        p1 = pya.Point(int(self.x1 / dbu), int(self.y1 / dbu))
        p2 = pya.Point(int(self.x2 / dbu), int(self.y2 / dbu))
        
        # Draw connection line
        line = pya.Path([p1, p2], width)
        cell.shapes(fib_layer).insert(line)
        
        # Draw endpoint circles
        r = int(radius / dbu)
        circle1 = pya.Polygon.ellipse(pya.Box(p1.x - r, p1.y - r, p1.x + r, p1.y + r), 32)
        circle2 = pya.Polygon.ellipse(pya.Box(p2.x - r, p2.y - r, p2.x + r, p2.y + r), 32)
        cell.shapes(fib_layer).insert(circle1)
        cell.shapes(fib_layer).insert(circle2)
        
        # Draw label at midpoint
        mid_x = (p1.x + p2.x) // 2
        mid_y = (p1.y + p2.y) // 2
        text = pya.Text(self.id, pya.Trans(pya.Point(mid_x, mid_y)))
        cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        return (f'<connect id="{self.id}" x1="{self.x1}" y1="{self.y1}" '
                f'x2="{self.x2}" y2="{self.y2}" layer="{self.layer}"/>')
    
    @staticmethod
    def from_xml(elem) -> 'ConnectMarker':
        """Deserialize from XML element"""
        return ConnectMarker(
            id=elem.get('id'),
            x1=float(elem.get('x1')),
            y1=float(elem.get('y1')),
            x2=float(elem.get('x2')),
            y2=float(elem.get('y2')),
            layer=int(elem.get('layer'))
        )


@dataclass
class ProbeMarker:
    """Probe operation marker - downward arrow"""
    id: str
    x: float
    y: float
    layer: int
    
    def to_gds(self, cell, fib_layer):
        """Draw arrow symbol + label on GDS"""
        dbu = cell.layout().dbu
        height = SYMBOL_SIZES['probe']['height']
        width_size = SYMBOL_SIZES['probe']['width']
        line_width = int(SYMBOL_SIZES['probe']['line_width'] / dbu)
        
        # Convert to database units
        cx = int(self.x / dbu)
        cy = int(self.y / dbu)
        h = int(height / dbu)
        w = int(width_size / 2 / dbu)
        
        # Draw arrow pointing down (triangle)
        arrow_pts = [
            pya.Point(cx, cy - h),      # Top point
            pya.Point(cx - w, cy),      # Left point
            pya.Point(cx + w, cy),      # Right point
        ]
        arrow = pya.Polygon(arrow_pts)
        cell.shapes(fib_layer).insert(arrow)
        
        # Draw label above arrow
        text = pya.Text(self.id, pya.Trans(pya.Point(cx, cy + h // 2)))
        cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        return f'<probe id="{self.id}" x="{self.x}" y="{self.y}" layer="{self.layer}"/>'
    
    @staticmethod
    def from_xml(elem) -> 'ProbeMarker':
        """Deserialize from XML element"""
        return ProbeMarker(
            id=elem.get('id'),
            x=float(elem.get('x')),
            y=float(elem.get('y')),
            layer=int(elem.get('layer'))
        )
