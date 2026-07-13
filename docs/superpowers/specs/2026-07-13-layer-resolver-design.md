# Layer Resolver Design

## Goal

Make layer detection accurate for hierarchical KLayout layouts and deterministic when multiple visible layers overlap a click.

## Scope

- Search visible, non-FIB layers recursively below the active cell.
- Return the single detected layer directly.
- For multiple detected layers, return the Layer Panel selection only when it is one of the detected layers.
- Return no layer when zero layers are detected, when multiple layers have no selected match, or when detection fails.
- Preserve the existing `LayerInfo` display format and CUT/CONNECT marker fields.
- Delete the unused legacy scanner in `fib_plugin.py`.

## Non-goals

- Changing CUT from a two-point marker to a position-and-direction model.
- Changing JSON/XML schemas.
- Adding a layer picker dialog.
- Recording resolution provenance in markers.

## Data flow

1. A marker click calls `get_layer_at_point_with_selection`.
2. `get_layers_at_point` filters to visible, non-FIB layout layers.
3. Each layer is queried with KLayout's recursive touching iterator.
4. The resolver applies the deterministic selection rules above.
5. Existing callers continue receiving `LayerInfo` or `None` and format it as before.

## Failure behavior

KLayout access and parsing failures remain non-fatal: they are logged and resolve to no layer. The resolver never substitutes a layer that was not detected at the click.

## Testing

Standard-library `unittest` tests load `layer_tap.py` with a small fake `pya` environment. Tests cover hierarchical-only shapes, single matches, matching and mismatching Panel selections, and no-selection ambiguity. KLayout F5 testing remains required for the real application adapter.

