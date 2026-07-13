import ast
import re
import unittest
from pathlib import Path


FIB_PANEL_PATH = Path(__file__).resolve().parents[1] / "python" / "fib_tool" / "fib_panel.py"


def load_layer_display_formatter():
    source = FIB_PANEL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    formatter = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_format_layer_for_panel"
        ),
        None,
    )
    if formatter is None:
        raise AssertionError("missing _format_layer_for_panel")

    formatter_module = ast.Module(body=[formatter], type_ignores=[])
    namespace = {"re": re}
    exec(compile(formatter_module, str(FIB_PANEL_PATH), "exec"), namespace)
    return namespace["_format_layer_for_panel"]


class FIBPanelLayerDisplayTests(unittest.TestCase):
    def test_layer_name_keeps_one_layer_number_and_datatype(self):
        format_layer = load_layer_display_formatter()

        self.assertEqual(
            "UBM_CU.drawing - 318/0",
            format_layer("UBM_CU.drawing - 318/0:318/0"),
        )
        self.assertEqual(
            "BALL.drawing:319/0",
            format_layer("BALL.drawing:319/0:319/0"),
        )
        self.assertEqual("318/0", format_layer("318/0:318/0"))
        self.assertEqual(
            "UBM_CU.drawing - 318/0",
            format_layer("UBM_CU.drawing - 318/0"),
        )
        self.assertEqual("N/A", format_layer(None))

    def test_marker_list_uses_the_condensed_layer_display(self):
        source = FIB_PANEL_PATH.read_text(encoding="utf-8")

        self.assertIn("layer1_str = _format_layer_for_panel", source)
        self.assertIn("layer2_str = _format_layer_for_panel", source)


if __name__ == "__main__":
    unittest.main()
