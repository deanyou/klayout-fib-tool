# Runtime State, Serialization, and Error Handling Design

## Goal

Remove the remaining `__main__` coupling, make marker persistence share one
canonical representation, fix the confirmed dialog/report/transformation bugs,
and provide regression tests that run without KLayout.

## Constraints

- Keep Python 3.8+ and KLayout 0.28+ compatibility.
- Use only the standard library outside KLayout's `pya` runtime.
- Preserve legacy imports and XML entry points.
- Do not change marker geometry or the visible workflow.
- Keep UI notifications at the UI boundary; lower layers log and return status.

## Runtime State

`core.global_state` will own a lazily-created shared `FibGlobalState`. The panel,
plugin, and `SmartCounter` will use that same object. Counter reset, JSON load,
and marker creation therefore update one dictionary.

The plugin registry remains private to `fib_plugin`: it is runtime behavior, not
project data. `fib_panel` will call explicit plugin module functions to activate
modes, clear pending points, and clear coordinate labels. All writes to and
reads from `sys.modules['__main__']` will be removed.

## Marker Codec and Persistence

`business.marker_codec` will define the canonical marker record and the two
operations `marker_to_record(marker)` and `marker_from_record(record)`. Records
contain type, ID, geometry, layer, per-point layer information, notes,
screenshots, and target layers where supported.

`FibFileManager` will use the codec for JSON. `storage.py` will remain the
backward-compatible XML facade, but it will also pass marker data through the
codec instead of maintaining an independent object-construction path. XML keeps
its existing metadata return signature `(markers, library, cell)`.

## Confirmed Bug Fixes

- `FileDialogHelper.get_save_filename()` returns its computed fallback path when
  the native dialog raises.
- `report._take_screenshot()` computes CUT bounds from both endpoints and returns
  success/failure. Report generation fails rather than claiming success with a
  missing screenshot.
- `FibMarkerTransformer` derives types from real marker classes, constructs
  markers with keyword arguments, and assigns the configured marker layer rather
  than treating line width as a layer.

## Logging

`core.logging_utils` remains the compatibility location for `safe_print` and
adds small `info`, `warning`, `error`, and `exception` functions. They format a
consistent component prefix and preserve traceback details in the fallback log.
The modules changed by this work use this facade; `FibDialogManager` remains a
UI concern.

## Testing

Tests will use small `pya` fakes and import modules without initializing the full
KLayout UI. Coverage includes:

- shared-state identity and counter synchronization;
- absence of `sys.modules['__main__']` coupling;
- SmartCounter fallback/update behavior;
- all marker types through codec, JSON, and XML round trips;
- transformer conversion matrix and configured layers;
- file-dialog exception fallback;
- CUT screenshot bbox and report failure propagation;
- logging fallback and exception formatting.

The final gate is the full unittest suite, Python compilation, import checks with
the existing fake runtime, and a source scan for forbidden `__main__` access.
