import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
LAYER_TAP_PATH = ROOT / "python" / "fib_tool" / "layer_tap.py"


class FakeBox:
    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top


class FakeRecursiveIterator:
    def __init__(self, has_shape):
        self._has_shape = has_shape

    def at_end(self):
        return not self._has_shape


class FakeShapes:
    def size(self):
        return 0

    def each_touching(self, _box):
        return iter(())


class FakeLayerInfo:
    def __init__(self, layer, datatype=0, name=""):
        self.layer = layer
        self.datatype = datatype
        self.name = name


class FakeCell:
    def __init__(self, recursive_layers=()):
        self.recursive_layers = set(recursive_layers)
        self.recursive_queries = []

    def shapes(self, _layer_index):
        return FakeShapes()

    def begin_shapes_rec_touching(self, layer_index, search_box):
        self.recursive_queries.append((layer_index, search_box))
        return FakeRecursiveIterator(layer_index in self.recursive_layers)


class FakeLayout:
    dbu = 0.001

    def __init__(self, layer_infos):
        self._layer_infos = layer_infos

    def layer_infos(self):
        return self._layer_infos

    def layer(self, layer_info):
        return layer_info.layer


class FakeCellView:
    def __init__(self, layout, cell):
        self._layout = layout
        self.cell = cell

    def is_valid(self):
        return True

    def layout(self):
        return self._layout


class FakeView:
    def __init__(self, cellview):
        self._cellview = cellview

    def active_cellview(self):
        return self._cellview


class FakeMainWindow:
    def __init__(self, view):
        self._view = view

    def current_view(self):
        return self._view


class FakeApplicationInstance:
    def __init__(self, view):
        self._main_window = FakeMainWindow(view)

    def main_window(self):
        return self._main_window


def load_layer_tap(view=None):
    package = types.ModuleType("fib_tool")
    package.__path__ = [str(LAYER_TAP_PATH.parent)]

    config = types.ModuleType("fib_tool.config")
    config.LAYERS = {"cut": 337, "connect": 338, "probe": 339}
    config.GEOMETRIC_PARAMS = {"layer_tap_radius": 0.5}

    application_instance = FakeApplicationInstance(view)

    class Application:
        @staticmethod
        def instance():
            return application_instance

    pya = types.ModuleType("pya")
    pya.Application = Application
    pya.Box = FakeBox

    module_name = "fib_tool.layer_tap_under_test"
    module_names = ("fib_tool", "fib_tool.config", "pya", module_name)
    missing = object()
    previous_modules = {
        name: sys.modules.get(name, missing) for name in module_names
    }

    try:
        sys.modules["fib_tool"] = package
        sys.modules["fib_tool.config"] = config
        sys.modules["pya"] = pya
        sys.modules.pop(module_name, None)

        spec = importlib.util.spec_from_file_location(module_name, LAYER_TAP_PATH)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for name, previous_module in previous_modules.items():
            if previous_module is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous_module


class LayerHierarchyTests(unittest.TestCase):
    def test_finds_shape_in_child_cell_hierarchy(self):
        layout = FakeLayout([FakeLayerInfo(10, 0, "M1")])
        cell = FakeCell(recursive_layers={10})
        view = FakeView(FakeCellView(layout, cell))
        layer_tap = load_layer_tap(view)

        with patch.object(layer_tap, "get_visible_layers", return_value={(10, 0)}):
            result = layer_tap.get_layers_at_point(1.0, 2.0)

        self.assertEqual([layer_tap.LayerInfo(10, 0, "M1")], result)
        self.assertEqual(1, len(cell.recursive_queries))


class LayerSelectionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.layer_tap = load_layer_tap()
        self.m1 = self.layer_tap.LayerInfo(10, 0, "M1")
        self.m2 = self.layer_tap.LayerInfo(20, 0, "M2")
        self.m3 = self.layer_tap.LayerInfo(30, 0, "M3")

    def resolve(self, candidates, selected):
        with patch.object(
            self.layer_tap, "get_layers_at_point", return_value=candidates
        ), patch.object(
            self.layer_tap, "get_selected_layer_from_panel", return_value=selected
        ):
            return self.layer_tap.get_layer_at_point_with_selection(1.0, 2.0)

    def test_single_layer_does_not_require_panel_selection(self):
        self.assertEqual(self.m1, self.resolve([self.m1], None))

    def test_multiple_layers_accept_matching_panel_selection(self):
        self.assertEqual(self.m2, self.resolve([self.m1, self.m2], self.m2))

    def test_multiple_layers_reject_panel_selection_not_at_point(self):
        self.assertIsNone(self.resolve([self.m1, self.m2], self.m3))

    def test_multiple_layers_without_panel_selection_is_unresolved(self):
        self.assertIsNone(self.resolve([self.m1, self.m2], None))

    def test_no_detected_layer_does_not_fall_back_to_panel_selection(self):
        self.assertIsNone(self.resolve([], self.m3))


if __name__ == "__main__":
    unittest.main()
