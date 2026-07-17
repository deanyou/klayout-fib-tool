# Compact Report Header Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the report identity and marker summary into one compact responsive header, and make the light-theme title readable.

**Architecture:** Keep all report data placeholders and theme JavaScript unchanged. Restructure only the static template markup so `.summary` is a child of `.header`, then use CSS Grid for the desktop split and responsive stacking; regression tests inspect the generated template source.

**Tech Stack:** HTML5, CSS Grid, Python 3.8+ `unittest`, standard library only.

## Global Constraints

- Preserve `{generation_datetime}`, `{total_markers}`, `{cut_count}`, `{connect_count}`, and `{probe_count}` exactly.
- Preserve the existing `toggleTheme()` integration and `fib-report-theme` persistence behavior.
- Use `#4D1A4C` for the light-theme report title.
- Do not change serialization, marker data, report generation, or JavaScript.

---

### Task 1: Compact Responsive Report Header

**Files:**
- Modify: `tests/test_report_template_style.py`
- Modify: `python/fib_tool/templates/report_template.html`

**Interfaces:**
- Consumes: Existing report-template placeholders and the `.header`, `.header-meta`, `.summary`, `.summary-box`, and `.theme-toggle` selectors.
- Produces: A `.header-layout` container with `.header-copy` and nested `.summary` regions; explicit light-theme `h1` color styling.

- [ ] **Step 1: Write the failing structural and contrast tests**

Add this method to `ReportTemplateStyleTests`:

```python
def test_header_contains_compact_summary_and_readable_light_title(self):
    html = TEMPLATE.read_text(encoding="utf-8")
    self.assertIn('class="header-layout"', html)
    self.assertIn('class="header-copy"', html)
    self.assertIn(
        '            </div>\n        </div>\n    </div>\n\n    <div class="notes-section">',
        html,
    )
    self.assertIn('html[data-theme="light"] .header h1 { color: #4D1A4C; }', html)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m unittest tests.test_report_template_style.ReportTemplateStyleTests.test_header_contains_compact_summary_and_readable_light_title -v
```

Expected: FAIL because `.header-layout`, `.header-copy`, nested summary markup, and explicit light-title styling do not exist.

- [ ] **Step 3: Implement the compact header markup**

Inside `.header`, wrap the identity content and move the existing summary beside it:

```html
<div class="header-layout">
    <div class="header-copy">
        <p class="header-eyebrow">KLayout · Focused Ion Beam Operations</p>
        <h1>FIB Markers Report with Screenshots</h1>
        <div class="header-meta">
            <p>Generated {generation_datetime}</p>
            <p>{total_markers} total markers</p>
        </div>
    </div>
    <div class="summary">
        <div class="summary-box">
            <h3>CUT Markers</h3>
            <div class="number">{cut_count}</div>
        </div>
        <div class="summary-box">
            <h3>CONNECT Markers</h3>
            <div class="number">{connect_count}</div>
        </div>
        <div class="summary-box">
            <h3>PROBE Markers</h3>
            <div class="number">{probe_count}</div>
        </div>
    </div>
</div>
```

Remove the old standalone `.summary` block below `.header`.

- [ ] **Step 4: Implement the compact responsive styles**

Add or update the Linear-inspired override rules:

```css
.header { margin-bottom: 16px; padding: 28px 30px; }
.header-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(420px, 1fr);
    gap: 32px;
    align-items: center;
}
.header-copy { min-width: 0; padding-right: 42px; }
.summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0;
    margin: 0;
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    overflow: hidden;
}
.summary-box { border: 0; border-right: 1px solid var(--border-soft); border-radius: 0; }
.summary-box:last-child { border-right: 0; }
html[data-theme="light"] .header h1 { color: #4D1A4C; }
@media (max-width: 900px) {
    .header-layout { grid-template-columns: 1fr; gap: 20px; }
    .header-copy { padding-right: 42px; }
}
@media (max-width: 720px) {
    .header { padding: 24px 20px; }
    .summary { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .summary-box { padding: 14px 12px; }
}
```

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_report_template_style -v
```

Expected: all report-template style tests PASS.

- [ ] **Step 6: Run the complete regression suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests PASS with zero failures.

- [ ] **Step 7: Check formatting and commit**

Run:

```bash
git diff --check
git add tests/test_report_template_style.py python/fib_tool/templates/report_template.html
git commit -m "Compact report header layout"
```
