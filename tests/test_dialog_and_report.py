import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL = ROOT / "python" / "fib_tool"


class FakeDBox:
    def __init__(self, *coordinates):
        self.coordinates = coordinates


class DialogAndReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pya = types.ModuleType("pya")
        pya.DBox = FakeDBox
        pya.QFileDialog = type(
            "QFileDialog",
            (),
            {"getSaveFileName": staticmethod(
                lambda *_: (_ for _ in ()).throw(RuntimeError("dialog failed"))
            )},
        )
        sys.modules["pya"] = pya
        for name, path in (
            ("fib_tool", FIB_TOOL),
            ("fib_tool.core", FIB_TOOL / "core"),
        ):
            module = types.ModuleType(name)
            module.__path__ = [str(path)]
            sys.modules[name] = module
        cls.dialog = importlib.import_module("fib_tool.file_dialog_helper")
        cls.markers = importlib.import_module("fib_tool.markers")
        cls.report = importlib.import_module("fib_tool.report")

    def test_save_dialog_returns_fallback_path_after_native_error(self):
        result = self.dialog.FileDialogHelper.get_save_filename(
            default_name="fallback.json"
        )
        self.assertIsNotNone(result)
        self.assertEqual(Path.home() / "fallback.json", Path(result))

    def test_cut_screenshot_bbox_contains_both_endpoints(self):
        view = types.SimpleNamespace()
        view.zoom_box = lambda box: setattr(view, "box", box)
        view.save_image = lambda *_: None
        marker = self.markers.CutMarker("CUT_1", 10, 20, 30, 40, 337)
        result = self.report._take_screenshot(marker, Path("unused.png"), view)
        margin = self.report.SCREENSHOT_MARGIN
        self.assertTrue(result)
        self.assertEqual(
            (10 - margin, 20 - margin, 30 + margin, 40 + margin),
            view.box.coordinates,
        )

    def test_report_fails_when_screenshot_cannot_be_saved(self):
        view = types.SimpleNamespace(
            zoom_box=lambda *_: None,
            save_image=lambda *_: (_ for _ in ()).throw(OSError("save failed")),
        )
        marker = self.markers.ProbeMarker("PROBE_1", 10, 20, 339)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.html"
            result = self.report.generate_report([marker], "lib", "cell", str(path), view)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
