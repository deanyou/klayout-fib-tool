import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL = ROOT / "python" / "fib_tool"


class MarkerTransformerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules["pya"] = types.ModuleType("pya")
        for name, path in (
            ("fib_tool", FIB_TOOL),
            ("fib_tool.core", FIB_TOOL / "core"),
            ("fib_tool.business", FIB_TOOL / "business"),
        ):
            module = types.ModuleType(name)
            module.__path__ = [str(path)]
            sys.modules[name] = module
        cls.config = importlib.import_module("fib_tool.config")
        cls.markers = importlib.import_module("fib_tool.markers")
        cls.transformer = importlib.import_module(
            "fib_tool.business.marker_transformer"
        ).FibMarkerTransformer

    def test_connect_converts_to_cut_on_cut_layer(self):
        source = self.markers.ConnectMarker("CONNECT_1", 1, 2, 3, 4, 338)
        result = self.transformer.convert_to_cut(source)
        self.assertIsInstance(result, self.markers.CutMarker)
        self.assertEqual(self.config.LAYERS["cut"], result.layer)

    def test_cut_converts_to_connect_on_connect_layer(self):
        source = self.markers.CutMarker("CUT_1", 1, 2, 3, 4, 337)
        result = self.transformer.convert_to_connect(source)
        self.assertIsInstance(result, self.markers.ConnectMarker)
        self.assertEqual(self.config.LAYERS["connect"], result.layer)

    def test_cut_converts_to_probe_on_probe_layer(self):
        source = self.markers.CutMarker("CUT_1", 1, 2, 3, 4, 337)
        result = self.transformer.convert_to_probe(source)
        self.assertIsInstance(result, self.markers.ProbeMarker)
        self.assertEqual(self.config.LAYERS["probe"], result.layer)

    def test_probe_to_multipoint_is_rejected_without_raising(self):
        source = self.markers.ProbeMarker("PROBE_1", 1, 2, 339)
        self.assertIsNone(self.transformer.convert_to_multipoint(source))


if __name__ == "__main__":
    unittest.main()
