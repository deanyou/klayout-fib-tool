# Layer Resolver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect layers recursively and refuse ambiguous or false Layer Panel fallbacks.

**Architecture:** Keep the existing `LayerInfo | None` caller interface. Deepen `layer_tap.py` by putting recursive KLayout querying and deterministic arbitration behind that interface; test it with a local fake KLayout adapter.

**Tech Stack:** Python 3.8+, standard-library `unittest`, KLayout `pya`.

---

### Task 1: Add resolver regression tests

**Files:**
- Create: `tests/test_layer_tap.py`
- Test: `tests/test_layer_tap.py`

- [ ] Write a fake `pya.Application`, view, layout, cell, recursive iterator, and `Box` sufficient to load `layer_tap.py` without KLayout.
- [ ] Add `test_finds_shape_in_child_cell_hierarchy`, expecting a layer found only by `begin_shapes_rec_touching`.
- [ ] Add selection-policy tests: single candidate, matching selected candidate, mismatching selection, and no selection.
- [ ] Run `python3 -m unittest tests.test_layer_tap -v`; expect the hierarchy, mismatching-selection, and no-selection tests to fail against the current implementation.

### Task 2: Implement recursive detection and deterministic arbitration

**Files:**
- Modify: `python/fib_tool/layer_tap.py:166-269`
- Modify: `python/fib_tool/layer_tap.py:383-443`
- Test: `tests/test_layer_tap.py`

- [ ] Replace direct `cell.shapes(layer_index).each_touching(...)` with `cell.begin_shapes_rec_touching(layer_index, search_box)` and detect whether its iterator is non-empty.
- [ ] Keep single-candidate behavior unchanged.
- [ ] Return `None` for zero candidates.
- [ ] For multiple candidates, return the Panel selection only if layer/datatype matches a candidate; otherwise return `None`.
- [ ] Run `python3 -m unittest tests.test_layer_tap -v`; expect all tests to pass.

### Task 3: Remove dead scanner and verify

**Files:**
- Modify: `python/fib_tool/fib_plugin.py:673-771`

- [ ] Confirm `_get_layers_at_position` and `_shape_contains_point` have no callers with `rg`.
- [ ] Delete both unused methods.
- [ ] Re-run the resolver tests.
- [ ] Parse all changed Python files with `ast.parse`.
- [ ] Review `git diff --check` and `git diff` for unrelated changes.
- [ ] Provide the user with KLayout F5 test cases for hierarchical, single-layer, overlapping-layer, and empty-area clicks.

