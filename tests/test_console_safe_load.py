import builtins
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL_PATH = ROOT / "python" / "fib_tool"
FILE_MANAGER_PATH = FIB_TOOL_PATH / "business" / "file_manager.py"


def load_file_manager():
    package = types.ModuleType("fib_tool")
    package.__path__ = [str(FIB_TOOL_PATH)]

    business = types.ModuleType("fib_tool.business")
    business.__path__ = [str(FIB_TOOL_PATH / "business")]

    ui = types.ModuleType("fib_tool.ui")
    ui.__path__ = [str(FIB_TOOL_PATH / "ui")]

    dialog_manager = types.ModuleType("fib_tool.ui.dialog_manager")

    class FibDialogManager:
        @staticmethod
        def show_error_json_parse(*_args):
            pass

        @staticmethod
        def show_error_file_not_found(*_args):
            pass

        @staticmethod
        def show_error_permission_denied(*_args):
            pass

        @staticmethod
        def show_error_invalid_file(*_args):
            pass

    dialog_manager.FibDialogManager = FibDialogManager

    module_name = "fib_tool.business.file_manager"
    module_names = (
        "fib_tool",
        "fib_tool.business",
        "fib_tool.ui",
        "fib_tool.ui.dialog_manager",
        module_name,
    )
    missing = object()
    previous_modules = {
        name: sys.modules.get(name, missing) for name in module_names
    }

    try:
        sys.modules["fib_tool"] = package
        sys.modules["fib_tool.business"] = business
        sys.modules["fib_tool.ui"] = ui
        sys.modules["fib_tool.ui.dialog_manager"] = dialog_manager
        sys.modules.pop(module_name, None)

        spec = importlib.util.spec_from_file_location(module_name, FILE_MANAGER_PATH)
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


class ConsoleSafeLoadTests(unittest.TestCase):
    def test_json_load_succeeds_when_console_print_is_unavailable(self):
        file_manager = load_file_manager()
        data = {
            "version": "1.0",
            "markers": [{"id": "CUT_0", "type": "cut"}],
            "marker_notes_dict": {"CUT_0": "test"},
            "marker_counters": {"cut": 1, "connect": 0, "probe": 0},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "markers.json"
            json_path.write_text(json.dumps(data), encoding="utf-8")

            with patch.object(
                builtins,
                "print",
                side_effect=RuntimeError("Macro Development console is closed"),
            ):
                result = file_manager.FibFileManager.load_markers_from_json(
                    str(json_path)
                )

        self.assertEqual(data["markers"], result[0])
        self.assertEqual(data["marker_notes_dict"], result[1])
        self.assertEqual(data["marker_counters"], result[2])


if __name__ == "__main__":
    unittest.main()
