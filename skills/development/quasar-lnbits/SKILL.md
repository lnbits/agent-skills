---
name: quasar-lnbits
description: Use when building or cleaning LNbits Vue/Quasar pages. Prefer Quasar layout, spacing, typography, and theme behavior over hand-applied colors. Follow LNbits extension patterns such as tpos, inventory, bitcoinswitch, satspay or auction_house, and avoid custom dark/light styling when Quasar theming already handles it.
category: development
---

# Quasar LNbits Skill

Use this skill for LNbits extension UI work that uses Quasar and Vue.

Primary goal:

- make pages feel native to LNbits
- let Quasar theme and layout systems do the work
- avoid custom color painting unless there is a clear semantic reason

## When To Use

Use this skill when:

- building a new LNbits extension page with Quasar
- refactoring a page that uses too many plain wrappers or custom CSS
- cleaning up spacing, layout, and card composition
- removing hand-applied dark/light styling that fights LNbits theming

Do not use this skill as the main guide for:

- extension-specific business logic
- backend API design
- one-off visual branding that belongs only to a single extension repo

## Inputs

Before applying this skill, gather:

- the target Vue or template file
- any related LNbits extension page used as a reference
- the current Quasar component structure, if one already exists
- the user-facing goal of the page

## Core Rules

1. Prefer Quasar structure over plain `div` structure.
2. Prefer Quasar spacing, grid, and typography helpers over custom CSS.
3. Do not simulate dark mode or light mode with hand-picked backgrounds.
4. Use Quasar theme tokens and component defaults before adding `color`, `text-*`, or `bg-*` classes.
5. Follow existing LNbits extension markup patterns before inventing new ones.
6. Treat Quasar components as Vue APIs, not just markup tags: choose props, slots, and model bindings deliberately.

## Vue And Component API Rule

Quasar is not only a markup vocabulary. It is a Vue component library, so the component API matters just as much as the HTML shape.

Prefer:

- component props before custom wrappers or duplicated markup
- `v-model` and Quasar events for stateful controls
- declarative component configuration in script data where the component expects it
- scoped slots only when props and built-in behavior are not enough

Examples:

- drive `q-table` with a `columns` array and rows data instead of manually building every table cell
- use `q-dialog v-model="showDialog"` instead of toggling visibility with ad hoc DOM logic
- use `q-input` props such as `type`, `dense`, `filled`, `hint`, and validation hooks before custom input shells
- keep repeated formatting logic in computed values, helpers, or table column definitions instead of scattering it through the template

## Theme Rule

Default assumption:

- Quasar theme already handles dark/light surfaces

So:

- do not add things like `bg-dark`, `text-white`, `bg-grey-1`, `bg-grey-2` just to force a look
- do not try to create a fake “darker theme” in component markup
- do not manually color cards unless the color is semantically meaningful

Allowed uses of color:

- primary actions: `q-btn color="primary"`
- status semantics: positive / warning / negative / info
- chips or badges that communicate state
- rare emphasis where LNbits already uses the same pattern

If a component should simply look like the rest of LNbits:

- omit explicit color styling
- use plain `q-card`, `q-banner`, `q-list`, `q-item`, `q-table`, `q-btn`

## Layout Rule

Prefer Quasar layout primitives:

- `row`, `col-*`
- `q-col-gutter-*` for grid columns
- `q-gutter-*` for non-column children
- `items-center`, `justify-between`, `no-wrap`, `flex-center`
- `q-pa-*`, `q-px-*`, `q-py-*`, `q-ma-*`, `q-mt-*`, etc.
- `text-h*`, `text-subtitle*`, `text-body*`, `text-caption`, `text-overline`

Do not:

- wrap everything in extra `div`s when `q-card-section`, `q-item-section`, `q-card-actions`, or `q-banner` already solve it
- style `row q-col-gutter-*` parents with background or border-related styling

If you need a bordered or styled block inside a gutter layout:

- style the child content element
- not the gutter parent

## Component Rule

Use Quasar components intentionally:

- page shell: `q-page`
- main blocks: `q-card`
- internal content: `q-card-section`
- actions: `q-card-actions`
- repeated detail rows: `q-list` + `q-item`
- notices/status: `q-banner`
- data grids: `q-table`
- lightweight state labels: `q-chip`, `q-badge`
- modal flows: `q-dialog`
- forms: `q-form`, `q-input`, `q-select`, `q-toggle`

Do not use `q-card flat` by default.

Use `bordered` only when the surrounding LNbits markup uses that look or when a card needs a stronger boundary.

When choosing a component, check its API as well as its rendered structure:

- important props
- slot names
- event names
- expected data shape
- whether the logic should live in template markup or in the Vue script

## LNbits Conventions

For LNbits extensions:

- prefer `v-text` over template interpolation for simple text output
- avoid Jinja includes inside static `.vue` files
- keep table formatting in `index.js` column definitions when practical
- use LNbits core JS utils before adding local helpers
- keep page state and Quasar component configuration predictable and close to the component that uses them

When a page already follows LNbits patterns:

- preserve the structure and visual language
- improve composition, not the brand direction

## Workflow

When doing UI cleanup:

1. inspect the nearest LNbits reference extension
2. identify where plain `div`s can become Quasar structure
3. remove hand-applied colors that fight the theme
4. normalize spacing using Quasar classes
5. only after structure is sound, adjust semantic color usage

## LNbits References To Check

These are useful LNbits patterns to inspect in the main LNbits codebase when relevant:

- `lnbits/extensions/tpos/templates/tpos/index.html`
- `lnbits/extensions/inventory/`
- `lnbits/extensions/bitcoinswitch/static/index.vue`
- `lnbits/extensions/bitmarket/templates/bitmarket/index.html`

These paths are not stored in this repository. They are examples of the kinds of LNbits extension pages to compare against when working in an LNbits codebase.

## Quasar Docs To Read When Needed

Open only the relevant reference files:

- theme and colors:
  - `references/theme-and-colors.md`
- layout and spacing:
  - `references/layout-and-spacing.md`
- component structure:
  - `references/components.md`

Core Quasar component docs covered by this skill:

- cards
- lists and list items
- tables
- dialogs
- forms
- flex/grid utilities
- component props, slots, and model bindings for the components above

## Hard Rules

- Do not hand-paint dark mode with `bg-dark` / `text-white` unless there is a real semantic reason.
- Do not add color classes just because a page feels bland.
- Fix structure first, then spacing, then semantics.
- If LNbits already has a pattern, reuse it.

## Expected Outcome

After applying this skill, the page should:

- feel visually consistent with LNbits
- rely more on Quasar structure than custom wrappers
- use Quasar component APIs intentionally instead of reimplementing behavior in custom Vue markup
- use semantic color intentionally instead of decorating every surface
- be easier for another contributor or agent to maintain
