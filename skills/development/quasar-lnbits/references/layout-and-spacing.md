# Layout And Spacing

Prefer Quasar layout helpers and spacing utilities over custom wrapper divs and hand-written CSS.

Official docs:

- https://quasar.dev/layout/grid/introduction-to-flexbox

Use these first:

- `row`, `col-*`
- `q-col-gutter-*` for grid columns
- `q-gutter-*` for regular child spacing
- `items-center`, `items-start`, `justify-between`, `no-wrap`
- `q-pa-*`, `q-px-*`, `q-py-*`, `q-ma-*`, `q-mt-*`, `q-mb-*`
- `text-h*`, `text-subtitle*`, `text-body*`, `text-caption`, `text-overline`

Practical rules:

- Use `q-page` as the shell for full pages.
- Put cards in a `row` and size them with `col-12 col-md-6 col-lg-4` style classes.
- Use `q-card-section` instead of nested plain wrappers inside cards.
- Use `q-card-actions` for button rows instead of ad hoc flex wrappers.
- Style the content child, not the `row q-col-gutter-*` parent.

Avoid:

- extra `div`s that exist only for spacing
- custom inline flex CSS when Quasar classes already express it
- putting borders, background, or radius on gutter parents
