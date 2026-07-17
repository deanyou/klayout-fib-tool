import importlib.util
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIB_TOOL = ROOT / "python" / "fib_tool"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeometryUtilsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geometry = load_module(
            "geometry_utils_under_test", FIB_TOOL / "core" / "geometry_utils.py"
        )

    def test_distance_direction_and_bounding_box(self):
        self.assertEqual(5.0, self.geometry.calculate_distance(0, 0, 3, 4))
        self.assertEqual("right", self.geometry.calculate_direction(0, 0, 5, 1))
        self.assertEqual((0, -2, 5, 4), self.geometry.get_bounding_box([(0, 4), (5, -2)]))

    def test_marker_center_supports_real_probe_shape(self):
        probe = types.SimpleNamespace(x=5.0, y=6.0)
        self.assertEqual((5.0, 6.0), self.geometry.get_marker_center(probe))


class ValidationUtilsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validation = load_module(
            "validation_utils_under_test", FIB_TOOL / "core" / "validation_utils.py"
        )

    def test_marker_id_and_coordinates_validation(self):
        self.assertEqual((True, None), self.validation.validate_marker_id("CUT_7"))
        self.assertFalse(self.validation.validate_marker_id("EXECUTE_7")[0])
        self.assertFalse(self.validation.validate_coordinates(float("inf"), 0)[0])

    def test_file_path_validation(self):
        self.assertFalse(self.validation.validate_file_path("")[0])
        with tempfile.TemporaryDirectory() as temp_dir:
            path = str(Path(temp_dir) / "report.html")
            self.assertEqual(
                (True, None),
                self.validation.validate_file_path(path, must_be_writable=True),
            )


class ExportManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export_manager = load_module(
            "export_manager_under_test", FIB_TOOL / "business" / "export_manager.py"
        ).FibExportManager

    def test_prerequisites_and_output_directory(self):
        self.assertFalse(self.export_manager.validate_export_prerequisites([])[0])
        self.assertEqual(
            (True, None), self.export_manager.validate_export_prerequisites([object()])
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output = self.export_manager.create_output_directory(temp_dir, "fib")
            self.assertTrue(Path(output).is_dir())


if __name__ == "__main__":
    unittest.main()
