import unittest
from pathlib import Path


FIB_PANEL_PATH = Path(__file__).resolve().parents[1] / "python" / "fib_tool" / "fib_panel.py"


class FIBPanelVersionTests(unittest.TestCase):
    def test_dock_title_includes_current_version(self):
        source = FIB_PANEL_PATH.read_text(encoding="utf-8")

        self.assertIn('super().__init__("FIB Panel v1.0.3", parent)', source)

    def test_marker_buttons_use_a_safe_control_height(self):
        source = FIB_PANEL_PATH.read_text(encoding="utf-8")

        self.assertIn("widget_height = 24", source)


if __name__ == "__main__":
    unittest.main()
