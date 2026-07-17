import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "python" / "fib_tool" / "core" / "plugin_registry.py"


def load_registry_module():
    spec = importlib.util.spec_from_file_location("plugin_registry_under_test", REGISTRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginRegistryTests(unittest.TestCase):
    def test_registry_owns_plugins_and_active_plugin(self):
        registry_module = load_registry_module()
        registry = registry_module.FibPluginRegistry()
        cut_plugin = object()

        registry.register("cut", cut_plugin)
        registry.activate(cut_plugin)

        self.assertIs(cut_plugin, registry.get("cut"))
        self.assertIs(cut_plugin, registry.active_plugin)
        self.assertIn(cut_plugin, registry.values())
        self.assertTrue(registry.deactivate(cut_plugin))
        self.assertIsNone(registry.active_plugin)

    def test_registry_rejects_unknown_modes(self):
        registry_module = load_registry_module()
        registry = registry_module.FibPluginRegistry()

        with self.assertRaises(ValueError):
            registry.register("execute", object())

    def test_deactivating_inactive_plugin_preserves_active_plugin(self):
        registry_module = load_registry_module()
        registry = registry_module.FibPluginRegistry()
        active = object()
        registry.activate(active)

        self.assertFalse(registry.deactivate(object()))
        self.assertIs(active, registry.active_plugin)


if __name__ == "__main__":
    unittest.main()
