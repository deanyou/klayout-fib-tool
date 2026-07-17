# Runtime State, Serialization, and Error Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify runtime state and marker persistence, fix confirmed bugs, and establish tested error handling without breaking KLayout compatibility.

**Architecture:** A shared `FibGlobalState` coordinates counters across panel, plugin, and SmartCounter. A canonical marker record codec feeds both JSON and legacy XML persistence. A lightweight logging facade handles diagnostics while UI dialogs stay in the panel/UI layer.

**Tech Stack:** Python 3.8+, standard-library `unittest`, KLayout `pya` in production, test fakes outside KLayout.

## Global Constraints

- Preserve existing public imports and XML function signatures.
- Add no third-party dependencies.
- Write and observe each regression test failing before production changes.
- Do not include unrelated untracked files in commits.

---

### Task 1: Shared Runtime State

**Files:**
- Modify: `python/fib_tool/core/global_state.py`
- Modify: `python/fib_tool/fib_plugin.py`
- Modify: `python/fib_tool/fib_panel.py`
- Modify: `python/fib_tool/smart_counter.py`
- Create: `tests/test_runtime_state.py`

**Interfaces:**
- Produces: `get_global_state() -> FibGlobalState`
- Produces: `fib_plugin.clear_pending_points() -> None`

- [ ] Write tests proving repeated state lookup returns one object, SmartCounter updates it, and production modules contain no `sys.modules['__main__']` access.
- [ ] Run `python3 -m unittest tests.test_runtime_state -v` and verify failures describe the missing shared-state API and old coupling.
- [ ] Add lazy shared-state lookup, inject/use it in plugin, panel, and SmartCounter, and replace panel fallbacks with plugin APIs.
- [ ] Run the focused test and then the full suite.

### Task 2: Canonical Marker Codec and Persistence

**Files:**
- Create: `python/fib_tool/business/marker_codec.py`
- Modify: `python/fib_tool/business/file_manager.py`
- Modify: `python/fib_tool/storage.py`
- Create: `tests/test_marker_persistence.py`

**Interfaces:**
- Produces: `marker_to_record(marker) -> dict`
- Produces: `marker_from_record(record) -> marker`

- [ ] Write round-trip tests for CUT, CONNECT, PROBE, multi-point markers, JSON project data, and legacy XML metadata.
- [ ] Run `python3 -m unittest tests.test_marker_persistence -v` and verify it fails because the codec does not exist.
- [ ] Implement the codec and delegate JSON/XML marker conversion to it.
- [ ] Run focused and full tests, confirming old XML signatures remain unchanged.

### Task 3: Marker Transformation

**Files:**
- Modify: `python/fib_tool/business/marker_transformer.py`
- Create: `tests/test_marker_transformer.py`

**Interfaces:**
- Consumes: real marker classes and `config.LAYERS`
- Produces: working `convert_to_cut/connect/probe/multipoint` methods

- [ ] Write conversion-matrix tests using actual marker classes and assert configured target layers.
- [ ] Run the focused tests and verify the current `unknown` type failure.
- [ ] Derive source type from marker classes and use keyword constructors with configured layers.
- [ ] Run focused and full tests.

### Task 4: Dialog and Report Bugs

**Files:**
- Modify: `python/fib_tool/file_dialog_helper.py`
- Modify: `python/fib_tool/report.py`
- Create: `tests/test_dialog_and_report.py`

**Interfaces:**
- Produces: fallback save path after dialog exceptions
- Produces: `_take_screenshot(...) -> bool`

- [ ] Write tests for dialog exception fallback, CUT endpoint bbox, and screenshot failure propagation.
- [ ] Run focused tests and observe the `None` fallback and missing `CutMarker.x` failures.
- [ ] Return the fallback path, calculate CUT bbox from endpoints, and propagate screenshot failure to `generate_report`.
- [ ] Run focused and full tests.

### Task 5: Logging Facade and Final Verification

**Files:**
- Modify: `python/fib_tool/core/logging_utils.py`
- Modify touched business/report modules to use the facade
- Create: `tests/test_logging_utils.py`

**Interfaces:**
- Produces: `info`, `warning`, `error`, and `exception` logging helpers
- Preserves: `safe_print(*args, **kwargs) -> bool`

- [ ] Write tests for component prefixes and traceback-preserving fallback output.
- [ ] Run focused tests and verify the new facade functions are absent.
- [ ] Implement the facade and adopt it in changed non-UI modules.
- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Run syntax compilation for root, core, business, and UI modules.
- [ ] Scan the runtime files and confirm no `sys.modules['__main__']` access remains.
