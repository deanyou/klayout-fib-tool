import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "python" / "fib_tool" / "templates" / "report_template.html"


class ReportTemplateStyleTests(unittest.TestCase):
    def test_template_uses_linear_visual_tokens(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("--surface: #111318", html)
        self.assertIn("--accent: #5e6ad2", html)
        self.assertIn('class="header-eyebrow"', html)
        self.assertIn("backdrop-filter: blur(18px)", html)


if __name__ == "__main__":
    unittest.main()
