import unittest
from pathlib import Path


FIB_PANEL_PATH = Path(__file__).resolve().parents[1] / "python" / "fib_tool" / "fib_panel.py"


class FIBPanelVersionTests(unittest.TestCase):
    def test_dock_title_includes_current_version(self):
        source = FIB_PANEL_PATH.read_text(encoding="utf-8")

        self.assertIn('super().__init__("FIB Panel v1.0.2", parent)', source)


if __name__ == "__main__":
    unittest.main()
