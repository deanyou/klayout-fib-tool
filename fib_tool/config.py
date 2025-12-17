"""
FIB Tool Configuration

Simple dictionary-based config. No classes, no over-engineering.
"""

# Layer mapping - dead simple
LAYERS = {
    'cut': 317,
    'connect': 318,
    'probe': 319,
    'coordinates': 319,  # Layer for coordinate text labels (same as probe)
}

# Symbol sizes in micrometers
SYMBOL_SIZES = {
    'cut': {
        'size': 2.0,           # X symbol size
        'arrow_length': 3.0,   # Direction arrow length
        'line_width': 0.2,     # Line width (updated to match actual usage)
    },
    'connect': {
        'endpoint_radius': 0.5,  # Endpoint circle radius
        'line_width': 0.2,       # Connection line width (updated to match actual usage)
    },
    'probe': {
        'height': 3.0,         # Arrow height
        'width': 1.5,          # Arrow width
        'line_width': 0.1,     # Line width
        'circle_radius': 0.5,  # Circle radius for probe marker
    },
    'multipoint': {
        'line_width': 0.2,        # Multi-point line width
        'vertex_radius': 0.1,     # Vertex circle radius
        'junction_radius': 0.3,   # Junction circle radius
        'circle_segments': 16,    # Number of segments for circles
    },
}

# Screenshot settings
SCREENSHOT_DPI = 150
SCREENSHOT_MARGIN = 5.0  # μm

# Geometric parameters (search, zoom, precision)
GEOMETRIC_PARAMS = {
    'search_radius': 5.0,              # Search radius for markers (μm)
    'zoom_padding': 2.0,               # Padding when zooming to markers (μm) - reduced for better detail
    'zoom_padding_detail': 0.5,       # Padding for double-click zoom (μm) - very close for maximum detail
    'coordinate_jump_padding': 10.0,   # Padding when jumping to coordinates (μm)
    'double_click_distance': 5.0,      # Maximum distance for double-click detection (μm)
    'coordinate_precision': 0.001,     # Coordinate precision (μm)
    'min_ruler_delta': 0.01,           # Minimum delta to show rulers (μm)
}

# UI timeout settings (milliseconds)
UI_TIMEOUTS = {
    'message_short': 2000,    # Short status messages (2 seconds)
    'message_medium': 3000,   # Medium status messages (3 seconds)
    'message_long': 10000,    # Long status messages (10 seconds)
    'double_click': 500,      # Double-click time threshold (500ms)
}

# Default marker notes (Chinese)
DEFAULT_MARKER_NOTES = {
    'cut': '切断',
    'connect': '连接',
    'probe': '点测',
}

# Report settings
REPORT_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FIB Operation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .operation {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; }}
        .operation h3 {{ color: #4CAF50; }}
        img {{ max-width: 800px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>FIB Operation Report</h1>
    
    <h2>Design Information</h2>
    <table>
        <tr><th>Library</th><td>{library}</td></tr>
        <tr><th>Cell</th><td>{cell}</td></tr>
        <tr><th>Generated</th><td>{timestamp}</td></tr>
        <tr><th>Total Operations</th><td>{total_ops}</td></tr>
    </table>
    
    <h2>Operations</h2>
    {operations_html}
</body>
</html>
"""
