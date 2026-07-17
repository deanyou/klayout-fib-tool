import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "python" / "fib_tool" / "core" / "logging_utils.py"


def load_logging_utils():
    spec = importlib.util.spec_from_file_location("fib_logging_utils", PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LoggingUtilsTests(unittest.TestCase):
    def test_info_adds_level_and_component(self):
        logging_utils = load_logging_utils()
        self.assertTrue(hasattr(logging_utils, "info"))
        with patch.object(logging_utils, "safe_print") as output:
            logging_utils.info("Codec", "saved marker")
        output.assert_called_once_with("[INFO] [Codec] saved marker")

    def test_exception_includes_traceback(self):
        logging_utils = load_logging_utils()
        self.assertTrue(hasattr(logging_utils, "exception"))
        with patch.object(logging_utils, "safe_print") as output:
            try:
                raise ValueError("bad marker")
            except ValueError:
                logging_utils.exception("Codec", "conversion failed")
        message = output.call_args.args[0]
        self.assertIn("[ERROR] [Codec] conversion failed", message)
        self.assertIn("ValueError: bad marker", message)


if __name__ == "__main__":
    unittest.main()
