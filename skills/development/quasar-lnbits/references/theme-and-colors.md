# Theme And Colors

Use Quasar's theme system first. Do not hand-paint dark or light surfaces in component markup unless the color carries meaning.

Official docs:

- https://quasar.dev/style/dark-mode
- https://quasar.dev/style/color-palette

Rules:

- Let Quasar and LNbits decide surface, text, and contrast colors.
- Prefer component defaults over `bg-*` and `text-*` utility classes.
- Use semantic colors only for meaning:
  - `primary` for the main action
  - `positive`, `warning`, `negative`, `info` for state
- Avoid forcing dark-mode looks with `bg-dark`, `text-white`, or grey utility stacks.
- If a page feels weak, fix composition and spacing before adding color.

Good defaults:

- `q-card`
- `q-banner`
- `q-list`
- `q-item`
- `q-table`
- `q-dialog`
- `q-btn color="primary"` for the main CTA

Avoid:

- manual surface colors on every card
- custom dark overlays in markup
- mixing many accent colors in one page
