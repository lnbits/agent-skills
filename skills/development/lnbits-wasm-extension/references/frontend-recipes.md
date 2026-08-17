# Standalone Frontend Recipes

Use these patterns after confirming the selected runtime exposes the named `_lnbits` assets. Replace `exampleext` and route methods with the product contract. Do not consult another extension.

## Choose One Page Model

Use static HTML for a small public form or status page. Use Vue/Quasar for admin pages, dialogs, dynamic lists, and repeated actions. Do not mix Vue-owned nodes with manual listeners.

## Vue/Quasar Entrypoint

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="/ext-assets/exampleext/_lnbits/bundle.min.css" />
    <link rel="stylesheet" href="/ext-assets/exampleext/_lnbits/material-icons.css" />
    <link rel="stylesheet" href="/ext-assets/exampleext/app.css" />
  </head>
  <body data-theme="bitcoin" class="body--dark">
    <div id="app" v-cloak></div>
    <script src="/ext-assets/exampleext/_lnbits/vue.global.prod.js"></script>
    <script src="/ext-assets/exampleext/_lnbits/quasar.umd.prod.js"></script>
    <script src="/ext-assets/exampleext/lnbits-extension-sdk.js"></script>
    <script src="/ext-assets/exampleext/admin.js"></script>
  </body>
</html>
```

If the runtime exposes a parent-theme bridge, use it. Otherwise keep the iframe internally coherent: the body theme and every Quasar `dark` prop must agree. Do not attempt to read parent DOM or globals.

Mount only after defining the whole app:

```js
const client = window.createLNbitsExtensionClient({extensionId: 'exampleext'})
const app = Vue.createApp({
  data: () => ({
    dialogOpen: false,
    loading: false,
    selected: null,
    form: {name: ''}
  }),
  computed: {
    canSave() {
      return this.form.name.trim().length > 0 && !this.loading
    }
  },
  methods: {
    closeDetail() {
      this.selected = null
    },
    async save() {
      if (!this.canSave) return
      this.loading = true
      try {
        await client.createRecord({name: this.form.name.trim()})
        this.dialogOpen = false
      } catch (error) {
        await client
          .notifyError(error instanceof Error ? error.message : String(error))
          .catch(() => {})
      } finally {
        this.loading = false
      }
    }
  },
  render() {
    const h = Vue.h
    const QBtn = Vue.resolveComponent('q-btn')
    const QCard = Vue.resolveComponent('q-card')
    const QCardSection = Vue.resolveComponent('q-card-section')
    const QDialog = Vue.resolveComponent('q-dialog')
    const QInput = Vue.resolveComponent('q-input')
    const QSpace = Vue.resolveComponent('q-space')

    const detail = this.selected
      ? h(QCard, {dark: true, flat: true, bordered: true, class: 'q-mt-md'}, {
          default: () => [
            h(QCardSection, {class: 'row items-center q-pb-none'}, {
              default: () => [
                h('h2', {class: 'text-h6 q-my-none'}, this.selected.name),
                h(QSpace),
                h(QBtn, {
                  flat: true, round: true, dense: true, icon: 'close',
                  type: 'button', 'aria-label': 'Close details',
                  onClick: this.closeDetail
                })
              ]
            }),
            h(QCardSection, {}, {default: () => [h('p', 'Details')]})
          ]
        })
      : null

    return h('main', {class: 'shell q-pa-md'}, [
      h(QBtn, {
        color: 'primary', label: 'Create', type: 'button',
        onClick: () => { this.dialogOpen = true }
      }),
      detail,
      h(QDialog, {
        modelValue: this.dialogOpen,
        'onUpdate:modelValue': value => { this.dialogOpen = value }
      }, {
        default: () => h(QCard, {dark: true, class: 'full-width'}, {
          default: () => [
            h(QCardSection, {}, {
              default: () => h(QInput, {
                dark: true, filled: true, label: 'Name',
                modelValue: this.form.name,
                'onUpdate:modelValue': value => { this.form.name = value }
              })
            }),
            h(QCardSection, {class: 'row justify-end q-gutter-sm'}, {
              default: () => [
                h(QBtn, {
                  flat: true, label: 'Cancel', type: 'button',
                  onClick: () => { this.dialogOpen = false }
                }),
                h(QBtn, {
                  color: 'primary', label: 'Save', type: 'button',
                  disable: !this.canSave, loading: this.loading,
                  onClick: this.save
                })
              ]
            })
          ]
        })
      })
    ])
  }
})
app.use(Quasar)
app.mount('#app')
```

Render-function slots are the third `h()` argument. Passing `default` in component props can render an empty card without throwing. For a method used as a handler, pass the function (`onClick: this.save`), not its result (`this.save()`).

## Static Page

```html
<div id="create-form">
  <label>Name <input id="name" required maxlength="80" /></label>
  <button id="create-button" type="button" disabled>Create</button>
</div>
<p id="error" role="alert" hidden></p>
```

```js
const client = window.createLNbitsExtensionClient({extensionId: 'exampleext'})
let loading = false

document.addEventListener('DOMContentLoaded', () => {
  const name = document.querySelector('#name')
  const button = document.querySelector('#create-button')
  const update = () => { button.disabled = loading || !name.value.trim() }
  name.addEventListener('input', update)
  button.addEventListener('click', create)
  update()
})

async function create(event) {
  event.preventDefault()
  const button = document.querySelector('#create-button')
  if (button.disabled) return
  loading = true
  button.disabled = true
  try {
    await client.createRecord({name: document.querySelector('#name').value.trim()})
  } catch (error) {
    showError(error)
  } finally {
    loading = false
    button.disabled = !document.querySelector('#name').value.trim()
  }
}
```

`addEventListener` is required here because static HTML owns the page. In a Vue-owned page use `onClick` instead.

## Layout and Tables

- Wrap the page in `shell q-pa-md`.
- Separate sibling cards/sections with `q-mt-md` or a `q-gutter-*` parent.
- Use `row q-col-gutter-md` and `col-12 col-md-*` for responsive summaries.
- Use `QMarkupTable` for repeated rows, payment history, errors, and row actions.
- Use plain responsive fields for four or fewer one-off status values.
- Use `text-h*`, `text-subtitle*`, `text-caption`, `text-grey-*`, and Quasar colors before custom typography or color CSS.
- Keep `app.css` for product-specific width, artwork, game canvas, or behavior Quasar cannot express.

## Rendered Interaction Test

Test the rendered tree/DOM, not just methods:

1. Mount the app with a fake bridge client.
2. Find the primary button and invoke its `onClick`.
3. Assert the dialog becomes visible.
4. Update each `modelValue` through `onUpdate:modelValue`.
5. Invoke the dialog action and assert the exact API payload.
6. Select a record, assert the detail body rendered, invoke Close, and assert it disappeared.
7. Force the client to reject and assert loading clears and the action is usable again.

Then repeat in the target LNbits instance with a real browser.
