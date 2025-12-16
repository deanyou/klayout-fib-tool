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
        'line_width': 0.1,     # Line width
    },
    'connect': {
        'endpoint_radius': 0.5,  # Endpoint circle radius
        'line_width': 0.1,       # Connection line width
    },
    'probe': {
        'height': 3.0,         # Arrow height
        'width': 1.5,          # Arrow width
        'line_width': 0.1,     # Line width
    },
}

# Screenshot settings
SCREENSHOT_DPI = 150
SCREENSHOT_MARGIN = 5.0  # μm

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
