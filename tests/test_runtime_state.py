import importlib.util
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL = ROOT / "python" / "fib_tool"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        package = types.ModuleType("fib_tool")
        package.__path__ = [str(FIB_TOOL)]
        core = types.ModuleType("fib_tool.core")
        core.__path__ = [str(FIB_TOOL / "core")]
        sys.modules["fib_tool"] = package
        sys.modules["fib_tool.core"] = core
        cls.state_module = load_module(
            "fib_tool.core.global_state", FIB_TOOL / "core" / "global_state.py"
        )

    def setUp(self):
        if hasattr(self.state_module, "reset_global_state"):
            self.state_module.reset_global_state()

    def test_global_state_is_shared(self):
        first = self.state_module.get_global_state()
        second = self.state_module.get_global_state()
        self.assertIs(first, second)

    def test_smart_counter_uses_panel_state(self):
        load_module(
            "fib_tool.core.logging_utils", FIB_TOOL / "core" / "logging_utils.py"
        )
        smart_counter = load_module(
            "fib_tool.smart_counter", FIB_TOOL / "smart_counter.py"
        )
        panel = types.SimpleNamespace(
            state=self.state_module.get_global_state(), markers_list=[]
        )
        counter = smart_counter.SmartCounter(panel)

        counter.update_global_counter("cut", 4)

        self.assertEqual(5, panel.state.marker_counters["cut"])
        self.assertEqual(5, counter.get_fallback_counter("cut"))

    def test_runtime_modules_do_not_access_main_namespace(self):
        for relative_path in ("fib_plugin.py", "fib_panel.py", "smart_counter.py"):
            source = (FIB_TOOL / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("sys.modules['__main__']", source, relative_path)

    def test_fib_plugin_does_not_expose_mutable_runtime_aliases(self):
        source = (FIB_TOOL / "fib_plugin.py").read_text(encoding="utf-8")
        for declaration in (
            "marker_counter =",
            "current_plugins =",
            "active_plugin =",
            "current_mode =",
        ):
            self.assertNotIn(declaration, source)

    def test_marker_type_callers_do_not_sniff_class_names(self):
        for relative_path in (
            "fib_plugin.py",
            "fib_panel.py",
            "smart_counter.py",
            "report.py",
            "marker_menu.py",
            "core/validation_utils.py",
            "business/file_manager.py",
            "business/marker_transformer.py",
            "screenshot_export.py",
            "storage.py",
        ):
            source = (FIB_TOOL / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("__class__.__name__", source, relative_path)


if __name__ == "__main__":
    unittest.main()
