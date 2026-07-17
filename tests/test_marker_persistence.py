import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL = ROOT / "python" / "fib_tool"


def install_test_package():
    pya = types.ModuleType("pya")
    sys.modules["pya"] = pya
    for name, path in (
        ("fib_tool", FIB_TOOL),
        ("fib_tool.core", FIB_TOOL / "core"),
        ("fib_tool.business", FIB_TOOL / "business"),
        ("fib_tool.ui", FIB_TOOL / "ui"),
    ):
        module = types.ModuleType(name)
        module.__path__ = [str(path)]
        sys.modules[name] = module
    dialogs = types.ModuleType("fib_tool.ui.dialog_manager")
    dialogs.FibDialogManager = type(
        "FibDialogManager",
        (),
        {
            "show_error_json_parse": staticmethod(lambda *_: None),
            "show_error_file_not_found": staticmethod(lambda *_: None),
            "show_error_permission_denied": staticmethod(lambda *_: None),
            "show_error_invalid_file": staticmethod(lambda *_: None),
        },
    )
    sys.modules["fib_tool.ui.dialog_manager"] = dialogs


class MarkerPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_test_package()
        cls.markers = importlib.import_module("fib_tool.markers")
        cls.multipoint = importlib.import_module("fib_tool.multipoint_markers")

    def test_codec_module_exists(self):
        self.assertTrue((FIB_TOOL / "business" / "marker_codec.py").exists())

    def test_all_marker_types_round_trip_through_records(self):
        codec = importlib.import_module("fib_tool.business.marker_codec")
        samples = [
            self.markers.CutMarker("CUT_1", 1, 2, 3, 4, 337, "M1", "M2"),
            self.markers.ConnectMarker("CONNECT_1", 1, 2, 3, 4, 338, "M2", "M3"),
            self.markers.ProbeMarker("PROBE_1", 5, 6, 339, "M4"),
            self.multipoint.MultiPointCutMarker("CUT_2", [(1, 2), (3, 4)], 337, ["M1", "M2"]),
            self.multipoint.MultiPointConnectMarker("CONNECT_2", [(1, 2), (3, 4)], 338, ["M2", "M3"]),
        ]
        for marker in samples:
            marker.notes = "note"
            marker.screenshots = ["shot.png"]
            restored = codec.marker_from_record(codec.marker_to_record(marker))
            self.assertEqual(marker.__class__, restored.__class__)
            self.assertEqual(marker.id, restored.id)
            self.assertEqual(marker.layer, restored.layer)
            self.assertEqual("note", restored.notes)

    def test_json_uses_canonical_records(self):
        codec = importlib.import_module("fib_tool.business.marker_codec")
        file_manager = importlib.import_module("fib_tool.business.file_manager")
        marker = self.markers.CutMarker("CUT_3", 1, 2, 3, 4, 337)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "project.json"
            self.assertTrue(file_manager.FibFileManager.save_markers_to_json([marker], str(path)))
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(codec.marker_to_record(marker), data["markers"][0])

    def test_xml_round_trip_supports_multipoint_and_metadata(self):
        storage = importlib.import_module("fib_tool.storage")
        marker = self.multipoint.MultiPointCutMarker(
            "CUT_4", [(1, 2), (3, 4)], 337, ["M1", "M2"]
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "project.xml"
            self.assertTrue(storage.save_markers([marker], str(path), "lib", "cell"))
            restored, library, cell = storage.load_markers(str(path))
        self.assertEqual(("lib", "cell"), (library, cell))
        self.assertEqual(marker.points, restored[0].points)
        self.assertEqual(marker.point_layers, restored[0].point_layers)


if __name__ == "__main__":
    unittest.main()
