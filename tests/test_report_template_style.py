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

    def test_header_contains_compact_summary_and_readable_light_title(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('class="header-layout"', html)
        self.assertIn('class="header-copy"', html)
        self.assertIn(
            '            <button id="theme-toggle" class="theme-toggle" type="button" '
            'onclick="toggleTheme()" aria-label="切换明暗主题" title="切换明暗主题">◐</button>'
            '\n        </div>\n    </div>\n\n'
            '    <div class="notes-section">',
            html,
        )
        self.assertIn(
            'html[data-theme="light"] .header h1 { color: #4D1A4C; }',
            html,
        )

    def test_theme_toggle_uses_header_grid_instead_of_overlay(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(
            'grid-template-columns: minmax(0, 1.45fr) minmax(420px, 1fr) auto;',
            html,
        )
        self.assertIn('.theme-toggle {\n            position: static;', html)
        self.assertIn('.summary { grid-column: 1 / -1; }', html)


if __name__ == "__main__":
    unittest.main()
