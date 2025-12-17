# Multi-Point Mode Usage Guide

## Overview

The FIB Tool now supports multi-point modes for CUT and CONNECT markers, allowing you to create complex cutting and connection paths with multiple vertices.

## Features

### Multi-Point CUT Markers
- Create continuous cutting paths with multiple points
- Each vertex is marked with a small circle
- Path connects all points in sequence
- Useful for complex cutting patterns

### Multi-Point CONNECT Markers
- Create connection paths with multiple junction points
- Endpoints shown with larger circles
- Junction points shown with smaller circles
- Useful for multi-point electrical connections

## How to Use

### Activating Multi-Point Mode

1. **From FIB Panel:**
   - Click the dropdown next to "Cut" or "Connect" button
   - Select "Multi Points" from the dropdown
   - Click the "Cut" or "Connect" button to activate

2. **Mode Indicators:**
   - Button turns green when active
   - Status message shows: "CUT/CONNECT multi-point mode - Left-click points, right-click to finish"

### Creating Multi-Point Markers

1. **Left-Click to Add Points:**
   - Left-click on the layout to add each point
   - Each click adds a coordinate text label
   - Status message updates with point count

2. **Complete the Marker:**
   - **Right-click** to finish (standard CAD workflow)
   - Requires at least 2 points
   - Marker is created and drawn on the layout

3. **Visual Feedback:**
   - Coordinate texts show at each click position
   - After completion, texts are updated with marker ID
   - Path is drawn connecting all points

### Switching Between Modes

- **2 Points Mode:** Traditional two-click markers (default)
- **Multi Points Mode:** Collect multiple points, double-click to finish

You can switch between modes at any time using the dropdown menu.

## Examples

### Multi-Point Cut Path
```
Points: (0,0) → (1,1) → (2,0) → (3,1)
Result: CUT_0 with 4 vertices
Visual: Path with small circles at each vertex
```

### Multi-Point Connect Path
```
Points: (0,0) → (2,2) → (4,0)
Result: CONNECT_0 with 3 points
Visual: Path with large circles at endpoints, small circle at junction
```

## Technical Details

### Right-Click to Finish
- Standard CAD workflow
- Right-click anywhere to complete the multi-point path
- No need for precise positioning or timing

### Marker Properties
- **Line width:** 0.2 microns (same as 2-point markers)
- **Vertex circles:** 0.1 micron radius (CUT)
- **Endpoint circles:** 0.5 micron radius (CONNECT)
- **Junction circles:** 0.3 micron radius (CONNECT)

### Data Storage
- Multi-point markers saved in JSON format
- Points stored as array: `[(x1,y1), (x2,y2), ...]`
- Backward compatible with 2-point markers
- Type: `multipoint_cut` or `multipoint_connect`

## Tips

1. **Precision:** Zoom in for accurate point placement
2. **Undo:** Switch modes to cancel current multi-point input
3. **Minimum Points:** Need at least 2 points to create a marker
4. **Right-Click:** Right-click anywhere to finish (standard CAD workflow)
5. **Coordinate Labels:** Each point gets a coordinate label that updates with marker ID
6. **Left vs Right:** Left-click adds points, right-click finishes

## Troubleshooting

### Marker Not Created
- Ensure you have at least 2 points
- Double-click at the last point (not a new location)
- Check console for debug messages

### Right-Click Not Working
- Make sure you're in multi-point mode (dropdown shows "Multi Points")
- Ensure you have at least 2 points added
- Try right-clicking in an empty area

### Points Not Showing
- Check that coordinate layer (319) is visible
- Verify you're in multi-point mode (dropdown shows "Multi Points")
- Look for status message updates

## Keyboard Shortcuts

Currently, multi-point mode is activated through the panel UI. Future versions may include keyboard shortcuts for faster workflow.

## Future Enhancements

Planned features for future releases:
- Undo last point (Backspace key)
- Real-time path preview
- Snap to grid/objects
- Distance measurements between points
- Polygon fill mode
- Star/radial connection patterns