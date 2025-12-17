# FIB Tool - Automatic Layer Creation

## Overview
FIB Tool now automatically detects and creates required layers when the plugin is loaded. This ensures that the tool works correctly even in PDKs that don't have the FIB layers predefined.

## Required Layers

The FIB Tool uses the following layers:

| Layer Name | Layer Number | Datatype | Purpose |
|------------|--------------|----------|---------|
| FIB_CUT | 317 | 0 | Cut operation markers |
| FIB_CONNECT | 318 | 0 | Connection operation markers |
| FIB_PROBE | 319 | 0 | Probe point markers |
| FIB_COORDINATES | 319 | 0 | Coordinate text labels (same as PROBE) |

## Automatic Layer Detection

When the FIB Tool plugin is loaded, it automatically:

1. **Checks** if each required layer exists in the current layout
2. **Creates** any missing layers with appropriate names
3. **Reports** the status of each layer in the console

### Console Output Example

```
=== Layer Check ===
[Layer Manager] Checking FIB layers...
[Layer Manager] ✓ Created layer 317/0 (FIB_CUT)
[Layer Manager] ✓ Created layer 318/0 (FIB_CONNECT)
[Layer Manager] ✓ Layer 319/0 (FIB_PROBE) already exists
[Layer Manager] Layer check complete: 3 layers verified
✓ FIB layers verified/created successfully
FIB Tool Layers:
----------------------------------------
  FIB_CUT              : Layer 317/0
  FIB_CONNECT          : Layer 318/0
  FIB_PROBE            : Layer 319/0
----------------------------------------
```

## Benefits

### 1. **PDK Independence**
- Works with any PDK, regardless of whether FIB layers are predefined
- No manual layer creation required

### 2. **Automatic Setup**
- Layers are created automatically on first use
- Consistent layer naming across different projects

### 3. **Error Prevention**
- Prevents "layer not found" errors
- Ensures markers are always created on the correct layers

### 4. **User-Friendly**
- No manual configuration needed
- Clear console messages about layer status

## Manual Layer Creation (Optional)

If you prefer to create layers manually or need to customize them:

1. Open the Layer Panel in KLayout
2. Create new layers with the following specifications:
   - Layer 317/0 - Name: FIB_CUT
   - Layer 318/0 - Name: FIB_CONNECT
   - Layer 319/0 - Name: FIB_PROBE

The plugin will detect these existing layers and use them without modification.

## Layer Visibility

After layers are created, you can control their visibility in the Layer Panel:

- **Show/Hide**: Toggle layer visibility
- **Color**: Customize layer colors for better visualization
- **Fill/Frame**: Adjust rendering style

## Technical Details

### Implementation

The layer detection and creation is handled by `src/layer_manager.py`:

- `check_and_create_layers(layout)` - Checks and creates layers
- `ensure_fib_layers()` - Main function called during plugin initialization
- `get_layer_info_summary()` - Returns formatted layer information

### Layer Creation Logic

```python
# For each required layer:
1. Create LayerInfo object with layer number, datatype, and name
2. Try to get layer index from layout
3. If layer doesn't exist (index < 0):
   - Insert new layer into layout
   - Report creation
4. If layer exists:
   - Report existing status
```

### Error Handling

- If layer creation fails, the plugin continues to load
- Warning messages are displayed in the console
- Existing layers are never modified or overwritten

## Troubleshooting

### Layers Not Created

If layers are not created automatically:

1. Check console for error messages
2. Ensure you have an active layout open
3. Try reloading the plugin
4. Create layers manually as a fallback

### Layer Number Conflicts

If your PDK already uses layers 317-319 for other purposes:

1. Edit `src/config.py` to change layer numbers
2. Update the LAYERS dictionary with new numbers
3. Reload the plugin

### Layer Names

Layer names (FIB_CUT, FIB_CONNECT, FIB_PROBE) are for identification only and don't affect functionality. You can rename them in the Layer Panel if needed.

## Future Enhancements

Potential improvements for layer management:

- [ ] Configurable layer numbers through UI
- [ ] Layer color customization
- [ ] Export/import layer configuration
- [ ] Layer conflict detection and resolution
- [ ] Support for custom layer naming schemes
