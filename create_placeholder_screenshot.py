#!/usr/bin/env python3
"""
Create a placeholder screenshot for SALT package
This should be replaced with actual KLayout screenshot later
Size: 800x600 pixels
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create 800x600 image
width, height = 800, 600
img = Image.new('RGB', (width, height), color=(245, 245, 245))
draw = ImageDraw.Draw(img)

# Colors
border_color = (70, 130, 180)
text_color = (50, 50, 50)
accent_color = (220, 20, 60)

# Draw border
draw.rectangle([0, 0, width - 1, height - 1], outline=border_color, width=3)

# Draw title area
title_bg = (70, 130, 180)
draw.rectangle([0, 0, width, 80], fill=title_bg)

# Add title text (using default font since we don't have custom fonts)
try:
    # Try to use a nicer font if available
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    # Fallback to default font
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Title
title = "FIB Tool - IC Layout Marker Tool"
draw.text((width // 2, 35), title, fill='white', font=font_large, anchor='mm')

# Draw simulated panel/UI area
panel_x = 20
panel_y = 100
panel_width = 350
panel_height = 480

# Panel background
draw.rectangle([panel_x, panel_y, panel_x + panel_width, panel_y + panel_height],
               fill='white', outline=border_color, width=2)

# Panel title
draw.rectangle([panel_x, panel_y, panel_x + panel_width, panel_y + 40],
               fill=(100, 149, 237), outline=border_color, width=1)
draw.text((panel_x + panel_width // 2, panel_y + 20), "FIB Panel",
          fill='white', font=font_medium, anchor='mm')

# Simulate marker list
marker_y = panel_y + 60
markers = [
    "CUT_001 - X:1234.5 Y:2345.6",
    "CONNECT_001 - X:1500.0 Y:2000.0",
    "PROBE_001 - X:1800.0 Y:2200.0"
]

draw.text((panel_x + 10, panel_y + 50), "Markers:", fill=text_color, font=font_medium)

for i, marker in enumerate(markers):
    y = marker_y + i * 30
    # Marker item background
    draw.rectangle([panel_x + 10, y, panel_x + panel_width - 10, y + 25],
                   fill=(230, 230, 250), outline=border_color, width=1)
    draw.text((panel_x + 15, y + 12), marker, fill=text_color, font=font_small, anchor='lm')

# Draw simulated layout view
layout_x = panel_x + panel_width + 30
layout_y = panel_y
layout_width = width - layout_x - 20
layout_height = panel_height

# Layout background
draw.rectangle([layout_x, layout_y, layout_x + layout_width, layout_y + layout_height],
               fill='black', outline=border_color, width=2)

# Draw some simulated circuit elements
circuit_color = (100, 200, 100)
for i in range(5):
    for j in range(4):
        x = layout_x + 30 + i * 70
        y = layout_y + 50 + j * 100
        draw.rectangle([x, y, x + 50, y + 60], outline=circuit_color, width=1)

# Draw FIB markers on layout
# CUT marker (X symbol)
cut_x, cut_y = layout_x + 100, layout_y + 150
marker_size = 15
draw.line([cut_x - marker_size, cut_y - marker_size,
           cut_x + marker_size, cut_y + marker_size], fill=accent_color, width=3)
draw.line([cut_x - marker_size, cut_y + marker_size,
           cut_x + marker_size, cut_y - marker_size], fill=accent_color, width=3)
draw.text((cut_x + 20, cut_y), "CUT_001", fill='yellow', font=font_small)

# CONNECT marker (line with circles)
con_x1, con_y1 = layout_x + 180, layout_y + 250
con_x2, con_y2 = layout_x + 280, layout_y + 300
draw.line([con_x1, con_y1, con_x2, con_y2], fill=(0, 191, 255), width=2)
draw.ellipse([con_x1 - 5, con_y1 - 5, con_x1 + 5, con_y1 + 5], outline=(0, 191, 255), width=2)
draw.ellipse([con_x2 - 5, con_y2 - 5, con_x2 + 5, con_y2 + 5], outline=(0, 191, 255), width=2)

# PROBE marker (circle with arrow)
probe_x, probe_y = layout_x + 200, layout_y + 400
draw.ellipse([probe_x - 12, probe_y - 12, probe_x + 12, probe_y + 12],
             outline=(255, 140, 0), width=2)
draw.polygon([
    (probe_x, probe_y + 12),
    (probe_x - 6, probe_y + 20),
    (probe_x + 6, probe_y + 20)
], fill=(255, 140, 0))

# Footer text
footer_text = "Note: Replace this with actual KLayout screenshot showing FIB Panel in action"
draw.text((width // 2, height - 20), footer_text, fill=text_color, font=font_small, anchor='mm')

# Save screenshot
output_path = 'docs/screenshot.png'
img.save(output_path, 'PNG')
print(f"Placeholder screenshot created: {output_path}")
print(f"Size: {width}x{height} pixels")
print("\n⚠️  IMPORTANT: Replace this with actual KLayout screenshot!")
