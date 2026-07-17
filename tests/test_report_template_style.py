import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "python" / "fib_tool" / "templates" / "report_template.html"
SCRIPT = ROOT / "python" / "fib_tool" / "templates" / "report_script.js"


class ReportTemplateStyleTests(unittest.TestCase):
    def test_template_uses_linear_visual_tokens(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("--surface: #111318", html)
        self.assertIn("--accent: #5e6ad2", html)
        self.assertIn('class="header-eyebrow"', html)
        self.assertIn("backdrop-filter: blur(18px)", html)

    def test_template_has_persisted_light_theme_toggle(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        for color in ("#FFFFFF", "#4D1A4C", "#FFEEED", "#6D3961", "#3FBC8E"):
            self.assertIn(color, html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn("function toggleTheme()", script)
        self.assertIn("fib-report-theme", script)
        self.assertIn("initializeTheme();", script)


if __name__ == "__main__":
    unittest.main()
