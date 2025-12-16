"""
Multi-Point FIB Marker Classes

Extended marker classes that support multiple points for complex cutting and connection paths.
Maintains backward compatibility with existing 2-point markers.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import pya
from config import LAYERS, SYMBOL_SIZES


@dataclass
class MultiPointCutMarker:
    """Multi-point cut operation marker - Path connecting multiple points"""
    id: str
    points: List[Tuple[float, float]]  # List of (x, y) coordinates
    layer: int
    
    def __post_init__(self):
        """Validate that we have at least 2 points"""
        if len(self.points) < 2:
            raise ValueError("MultiPointCutMarker requires at least 2 points")
    
    @property
    def x1(self):
        """First point x coordinate (for compatibility)"""
        return self.points[0][0] if self.points else 0
    
    @property
    def y1(self):
        """First point y coordinate (for compatibility)"""
        return self.points[0][1] if self.points else 0
    
    @property
    def x2(self):
        """Last point x coordinate (for compatibility)"""
        return self.points[-1][0] if self.points else 0
    
    @property
    def y2(self):
        """Last point y coordinate (for compatibility)"""
        return self.points[-1][1] if self.points else 0
    
    def to_gds(self, cell, fib_layer):
        """Draw multi-point path with fixed width"""
        if len(self.points) < 2:
            return
        
        dbu = cell.layout().dbu
        fixed_width = 0.2  # Fixed line width in microns
        width = int(fixed_width / dbu)  # Convert to database units
        
        # Convert all points to database units
        db_points = []
        for x, y in self.points:
            db_x = int(x / dbu)
            db_y = int(y / dbu)
            db_points.append(pya.Point(db_x, db_y))
        
        # Draw path connecting all points
        path = pya.Path(db_points, width)
        cell.shapes(fib_layer).insert(path)
        
        # Draw small circles at each point to show vertices
        vertex_radius = int(0.1 / dbu)  # 0.1 micron radius
        for point in db_points:
            vertex_circle = pya.Polygon.ellipse(
                pya.Box(point.x - vertex_radius, point.y - vertex_radius,
                       point.x + vertex_radius, point.y + vertex_radius), 16)
            cell.shapes(fib_layer).insert(vertex_circle)
        
        # Draw label at the center of the path
        if len(db_points) >= 2:
            # Calculate center point
            center_x = sum(p.x for p in db_points) // len(db_points)
            center_y = sum(p.y for p in db_points) // len(db_points)
            text = pya.Text(self.id, pya.Trans(pya.Point(center_x, center_y)))
            cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        points_str = ";".join(f"{x},{y}" for x, y in self.points)
        return f'<multipoint_cut id="{self.id}" points="{points_str}" layer="{self.layer}"/>'
    
    @staticmethod
    def from_xml(elem) -> 'MultiPointCutMarker':
        """Deserialize from XML element"""
        points_str = elem.get('points', '')
        points = []
        if points_str:
            for point_str in points_str.split(';'):
                if ',' in point_str:
                    x, y = point_str.split(',')
                    points.append((float(x), float(y)))
        
        return MultiPointCutMarker(
            id=elem.get('id'),
            points=points,
            layer=int(elem.get('layer'))
        )


@dataclass
class MultiPointConnectMarker:
    """Multi-point connect operation marker - Path with endpoints and junctions"""
    id: str
    points: List[Tuple[float, float]]  # List of (x, y) coordinates
    layer: int
    
    def __post_init__(self):
        """Validate that we have at least 2 points"""
        if len(self.points) < 2:
            raise ValueError("MultiPointConnectMarker requires at least 2 points")
    
    @property
    def x1(self):
        """First point x coordinate (for compatibility)"""
        return self.points[0][0] if self.points else 0
    
    @property
    def y1(self):
        """First point y coordinate (for compatibility)"""
        return self.points[0][1] if self.points else 0
    
    @property
    def x2(self):
        """Last point x coordinate (for compatibility)"""
        return self.points[-1][0] if self.points else 0
    
    @property
    def y2(self):
        """Last point y coordinate (for compatibility)"""
        return self.points[-1][1] if self.points else 0
    
    def to_gds(self, cell, fib_layer):
        """Draw multi-point connection path with endpoints and junctions"""
        if len(self.points) < 2:
            return
        
        dbu = cell.layout().dbu
        fixed_width = 0.2  # Fixed line width in microns
        width = int(fixed_width / dbu)  # Convert to database units
        endpoint_radius = SYMBOL_SIZES['connect']['endpoint_radius']
        junction_radius = 0.3  # Slightly smaller than endpoints
        
        # Convert all points to database units
        db_points = []
        for x, y in self.points:
            db_x = int(x / dbu)
            db_y = int(y / dbu)
            db_points.append(pya.Point(db_x, db_y))
        
        # Draw path connecting all points
        path = pya.Path(db_points, width)
        cell.shapes(fib_layer).insert(path)
        
        # Draw endpoint circles (first and last points)
        endpoint_r = int(endpoint_radius / dbu)
        junction_r = int(junction_radius / dbu)
        
        for i, point in enumerate(db_points):
            if i == 0 or i == len(db_points) - 1:
                # Endpoints - larger circles
                circle = pya.Polygon.ellipse(
                    pya.Box(point.x - endpoint_r, point.y - endpoint_r,
                           point.x + endpoint_r, point.y + endpoint_r), 32)
            else:
                # Junction points - smaller circles
                circle = pya.Polygon.ellipse(
                    pya.Box(point.x - junction_r, point.y - junction_r,
                           point.x + junction_r, point.y + junction_r), 16)
            
            cell.shapes(fib_layer).insert(circle)
        
        # Draw label at the center of the path
        if len(db_points) >= 2:
            # Calculate center point
            center_x = sum(p.x for p in db_points) // len(db_points)
            center_y = sum(p.y for p in db_points) // len(db_points)
            text = pya.Text(self.id, pya.Trans(pya.Point(center_x, center_y)))
            cell.shapes(fib_layer).insert(text)
    
    def to_xml(self) -> str:
        """Serialize to XML element"""
        points_str = ";".join(f"{x},{y}" for x, y in self.points)
        return f'<multipoint_connect id="{self.id}" points="{points_str}" layer="{self.layer}"/>'
    
    @staticmethod
    def from_xml(elem) -> 'MultiPointConnectMarker':
        """Deserialize from XML element"""
        points_str = elem.get('points', '')
        points = []
        if points_str:
            for point_str in points_str.split(';'):
                if ',' in point_str:
                    x, y = point_str.split(',')
                    points.append((float(x), float(y)))
        
        return MultiPointConnectMarker(
            id=elem.get('id'),
            points=points,
            layer=int(elem.get('layer'))
        )


# Utility functions for creating markers
def create_multipoint_cut_marker(marker_id: str, points: List[Tuple[float, float]], 
                                target_layers=None) -> MultiPointCutMarker:
    """Create a multi-point cut marker with additional metadata"""
    marker = MultiPointCutMarker(marker_id, points, LAYERS['cut'])
    marker.target_layers = target_layers or []
    marker.notes = "切断"  # Default notes for multi-point CUT markers
    marker.screenshots = []
    
    # Notify panel if available
    try:
        from fib_panel import get_fib_panel
        panel = get_fib_panel()
        if panel:
            panel.add_marker(marker)
            print(f"[MultiPoint] Added {marker_id} to panel")
    except Exception as e:
        print(f"[MultiPoint] Error notifying panel for multi-point CUT marker: {e}")
    
    return marker


def create_multipoint_connect_marker(marker_id: str, points: List[Tuple[float, float]], 
                                   target_layers=None) -> MultiPointConnectMarker:
    """Create a multi-point connect marker with additional metadata"""
    marker = MultiPointConnectMarker(marker_id, points, LAYERS['connect'])
    marker.target_layers = target_layers or []
    marker.notes = "连接"  # Default notes for multi-point CONNECT markers
    marker.screenshots = []
    
    # Notify panel if available
    try:
        from fib_panel import get_fib_panel
        panel = get_fib_panel()
        if panel:
            panel.add_marker(marker)
            print(f"[MultiPoint] Added {marker_id} to panel")
    except Exception as e:
        print(f"[MultiPoint] Error notifying panel for multi-point CONNECT marker: {e}")
    
    return marker