# Compact Report Header Design

## Goal

Reduce the vertical space used by the HTML report header while keeping the report identity, generation metadata, marker totals, and theme control immediately visible. Fix the low-contrast title in the light theme.

## Layout

- Merge the existing `.header` and `.summary` regions into one `.header` card.
- Use a two-column desktop layout:
  - Left: eyebrow, report title, generation time, and total marker count.
  - Right: CUT, CONNECT, and PROBE statistics in one compact three-column group.
- Keep the theme toggle in the top-right corner of the card.
- On viewports at or below 720 px, stack the title area above the statistics while keeping all three statistics on one row when space allows.
- Preserve all existing template placeholders and JavaScript behavior.

## Visual Rules

- Remove the separate outer spacing formerly created by `.summary` below `.header`.
- Use subtle internal separators rather than three large standalone cards.
- Keep the current Linear-inspired dark theme.
- In the light theme, explicitly set the report title to `#4D1A4C`; metadata remains `#6D3961`.
- Maintain the existing light palette and theme persistence behavior.

## Testing

- Add template regression assertions proving `.summary` is nested inside `.header`.
- Assert that the light-theme title has an explicit high-contrast color.
- Keep the existing theme token and persistence tests passing.
- Run the full unit-test suite after implementation.

## Scope

Only the HTML report template and its style regression tests change. Marker data, serialization, report generation, and theme-switching JavaScript remain unchanged.
