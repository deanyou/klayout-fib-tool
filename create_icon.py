#!/usr/bin/env python3
"""
Create a simple but professional icon for FIB Tool
Size: 64x64 pixels PNG
Theme: FIB beam + IC chip/circuit
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create 64x64 image with white background
size = 64
img = Image.new('RGB', (size, size), color='white')
draw = ImageDraw.Draw(img)

# Color scheme (professional blue/gray)
bg_color = (240, 248, 255)  # Alice blue
border_color = (70, 130, 180)  # Steel blue
beam_color = (255, 140, 0)  # Dark orange (FIB beam)
circuit_color = (100, 149, 237)  # Cornflower blue
accent_color = (220, 20, 60)  # Crimson (markers)

# Fill background
draw.rectangle([0, 0, size, size], fill=bg_color)

# Draw IC chip outline (bottom half)
chip_margin = 8
chip_y_start = size // 2
draw.rectangle(
    [chip_margin, chip_y_start, size - chip_margin, size - chip_margin],
    outline=border_color,
    width=2
)

# Draw circuit lines inside chip (simple pattern)
for i in range(3):
    y = chip_y_start + 8 + i * 6
    draw.line([chip_margin + 4, y, size - chip_margin - 4, y], fill=circuit_color, width=1)

# Draw vertical circuit lines
for i in range(4):
    x = chip_margin + 10 + i * 10
    draw.line([x, chip_y_start + 4, x, size - chip_margin - 4], fill=circuit_color, width=1)

# Draw FIB beam (angled line from top center, pointing down)
beam_start_x = size // 2
beam_start_y = 4
beam_end_x = size // 2 + 8
beam_end_y = chip_y_start - 4

# FIB beam (thick orange line with glow effect)
draw.line([beam_start_x, beam_start_y, beam_end_x, beam_end_y], fill=beam_color, width=3)

# Add small arrow head at beam end
arrow_size = 3
draw.polygon([
    (beam_end_x, beam_end_y),
    (beam_end_x - arrow_size, beam_end_y - arrow_size * 2),
    (beam_end_x + arrow_size, beam_end_y - arrow_size * 2)
], fill=beam_color)

# Draw FIB marker symbols (small X and circle) on the chip
# X marker
marker_x = size // 2 - 8
marker_y = chip_y_start + 12
marker_size = 4
draw.line([marker_x - marker_size, marker_y - marker_size,
           marker_x + marker_size, marker_y + marker_size], fill=accent_color, width=2)
draw.line([marker_x - marker_size, marker_y + marker_size,
           marker_x + marker_size, marker_y - marker_size], fill=accent_color, width=2)

# Circle marker
circle_x = size // 2 + 10
circle_y = chip_y_start + 12
circle_r = 3
draw.ellipse([circle_x - circle_r, circle_y - circle_r,
              circle_x + circle_r, circle_y + circle_r],
             outline=accent_color, width=2)

# Add border around entire icon
draw.rectangle([0, 0, size - 1, size - 1], outline=border_color, width=1)

# Save icon
output_path = 'docs/fib_icon.png'
os.makedirs('docs', exist_ok=True)
img.save(output_path, 'PNG')
print(f"Icon created: {output_path}")
print(f"Size: {size}x{size} pixels")
