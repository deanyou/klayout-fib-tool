# FIB Layer Auto-Creation - Testing Guide

## Overview

The FIB tool now automatically creates required layers (317, 318, 319) if they don't exist in the current PDK/layout.

## Implementation

### Files Modified
- `src/layer_manager.py` - Layer detection and creation logic
- `src/fib_plugin.py` - Added `get_or_create_layer()` helper function
- All layer access points updated to use `get_or_create_layer()`

### How It Works

1. **On Plugin Load**: `ensure_fib_layers()` is called automatically
   - Checks if layers 317/0, 318/0, 319/0 exist
   - Creates missing layers with proper names (FIB_CUT, FIB_CONNECT, FIB_PROBE)
   - Shows summary message

2. **On Marker Creation**: `get_or_create_layer()` is called
   - First tries to find existing layer
   - If not found, creates it automatically
   - Returns layer index for drawing

### Layers Created

| Layer | Number/Datatype | Name | Purpose |
|-------|----------------|------|---------|
| FIB_CUT | 317/0 | FIB_CUT | Cut markers |
| FIB_CONNECT | 318/0 | FIB_CONNECT | Connect markers |
| FIB_PROBE | 319/0 | FIB_PROBE | Probe markers |
| FIB_COORDINATES | 319/0 | FIB_COORDINATES | Coordinate text labels |

## Testing

### Method 1: Run Test Script

1. Open KLayout
2. Open any GDS file (or create a new layout)
3. Open Macro Development console (F5)
4. Run:
   ```python
   exec(open('/path/to/klayout-fib-tool/test_layer_creation.py', encoding='utf-8').read())
   ```

The test will:
- Show existing layers before
- Run layer creation
- Verify layers were created
- Show summary of results

### Method 2: Check Console Output

When you load the FIB plugin, check the console for:

```
=== Layer Check ===
[Layer Manager] Checking FIB layers...
[Layer Manager] Layout has X existing layers
[Layer Manager] ✓ Layer 317/0 already exists (name: FIB_CUT)
[Layer Manager] ✓ Created layer 318/0 (FIB_CONNECT) with index Y
...
✓ FIB layers verified/created successfully
```

### Method 3: Create a Marker

1. Activate FIB tool (any mode)
2. Click to create a marker
3. Check console for:
   ```
   [FIB] Created layer 317/0 (FIB_CUT) with index X
   ```
4. Check Layer Panel - you should see the new layers

### Method 4: Visual Verification

1. Open Layer Panel (F4)
2. Look for layers:
   - 317/0 (FIB_CUT)
   - 318/0 (FIB_CONNECT)
   - 319/0 (FIB_PROBE or FIB_COORDINATES)
3. If they exist, layer creation worked!

## Expected Behavior

### First Time (Layers Don't Exist)
```
[Layer Manager] Checking FIB layers...
[Layer Manager] Layout has 50 existing layers
[Layer Manager] ✓ Created layer 317/0 (FIB_CUT) with index 50
[Layer Manager] ✓ Created layer 318/0 (FIB_CONNECT) with index 51
[Layer Manager] ✓ Created layer 319/0 (FIB_PROBE) with index 52
[Layer Manager] Layer check complete: 3 layers verified
FIB Tool: Created 3 new layer(s), 0 layer(s) already existed
```

### Subsequent Times (Layers Exist)
```
[Layer Manager] Checking FIB layers...
[Layer Manager] Layout has 53 existing layers
[Layer Manager] ✓ Layer 317/0 already exists (name: FIB_CUT)
[Layer Manager] ✓ Layer 318/0 already exists (name: FIB_CONNECT)
[Layer Manager] ✓ Layer 319/0 already exists (name: FIB_PROBE)
[Layer Manager] Layer check complete: 3 layers verified
[Layer Manager] All 3 FIB layers already exist
```

## Troubleshooting

### Layers Not Created

**Symptom**: Console shows "Created" but layers don't appear in Layer Panel

**Possible Causes**:
1. Layout not saved after creation
2. Layer Panel needs refresh (close/reopen)
3. KLayout API version incompatibility

**Solutions**:
1. Save the layout (Ctrl+S)
2. Close and reopen Layer Panel (F4)
3. Run test script to verify

### Markers Show Empty Layer Index

**Symptom**: Console shows `Created marker on layer []`

**Cause**: `get_or_create_layer()` not being used

**Solution**: Check that all layer access uses `get_or_create_layer()` instead of `layout.layer()`

### Permission Errors

**Symptom**: "Failed to create layer" errors

**Cause**: Layout is read-only or locked

**Solution**: 
1. Make sure layout is editable
2. Check file permissions
3. Try with a new/empty layout

## API Reference

### `get_or_create_layer(layout, layer_num, datatype=0, layer_name=None)`

Helper function to get or create a layer.

**Parameters**:
- `layout`: pya.Layout object
- `layer_num`: Layer number (e.g., 317)
- `datatype`: Datatype (default 0)
- `layer_name`: Optional layer name (e.g., "FIB_CUT")

**Returns**: Layer index (int)

**Example**:
```python
from fib_plugin import get_or_create_layer
from config import LAYERS

# Get or create FIB_CUT layer
cut_layer = get_or_create_layer(layout, LAYERS['cut'], 0, 'FIB_CUT')

# Use the layer
cell.shapes(cut_layer).insert(some_shape)
```

### `ensure_fib_layers()`

Ensures all FIB layers exist in the current layout.

**Returns**: True if successful, False otherwise

**Called automatically** when plugin loads.

### `check_and_create_layers(layout)`

Checks and creates FIB layers.

**Parameters**: `layout` - pya.Layout object

**Returns**: dict with layer status (existed/created/failed)

### `verify_layers_exist(layout)`

Verifies that all FIB layers exist.

**Parameters**: `layout` - pya.Layout object

**Returns**: dict mapping layer number to exists (bool)

## Notes

- Layer creation happens automatically - no user action required
- Layers are created with proper names for easy identification
- If a layer already exists, it won't be recreated
- Layer creation is logged to console for debugging
- The same logic applies to coordinate text layer (319/0)
