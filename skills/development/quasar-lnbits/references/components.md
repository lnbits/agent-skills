# Component Structure

Use Quasar components for structure first, then fill them with data. Favor standard composition over custom wrappers.

Quasar components are also Vue APIs. Check the component props, emitted events, slots, and expected data structures before creating custom wrappers or hand-rolled behavior.

Official docs:

- https://quasar.dev/vue-components/card
- https://quasar.dev/vue-components/list-and-list-items
- https://quasar.dev/vue-components/table
- https://quasar.dev/vue-components/dialog
- https://quasar.dev/vue-components/input
- https://quasar.dev/vue-components/select

## API Mindset

Before custom code, ask:

- does the component already expose a prop for this?
- does the component already support this state through `v-model`?
- is there a scoped slot for the part I need to customize?
- should this configuration live in the Vue script instead of inline in the template?

Prefer Quasar's built-in API surface over rebuilding the same behavior in local markup.

## Cards

Use `q-card` for the main content block.

Typical structure:

- `q-card`
- `q-card-section` for title and summary
- `q-separator` if needed
- `q-card-section` for details
- `q-card-actions` for buttons

Rules:

- Do not default to `flat`.
- Do not turn cards into custom colored panels unless the color means something.
- For stat cards, keep the card simple and let typography do the work.

## Lists

Use `q-list` and `q-item` for repeated key/value details, status rows, and compact metadata.

Patterns:

- `q-item-section` for the label/value layout
- `q-item-label` for hierarchy
- `caption` for secondary detail

Good for:

- run facts
- agent summaries
- payout details
- status blocks inside cards

## Tables

Use `q-table` for admin data and large collections.

Rules:

- Define column labels, fields, and `format` functions in the `.js` file.
- Keep table-cell rendering minimal in `.vue`.
- Use scoped slots only when the default column formatting is not enough.
- Prefer chips/badges in status cells instead of custom colored text blocks.

Useful component API pattern:

```js
columns: [
  {
    name: 'amount',
    label: 'Amount',
    field: 'amount',
    align: 'left',
    sortable: true,
    format: value => LNbits.utils.formatSat(value)
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status'
  }
]
```

```vue
<q-table
  :rows="payments"
  :columns="columns"
  row-key="id"
  flat
>
  <template v-slot:body-cell-status="props">
    <q-td :props="props">
      <q-badge
        :color="props.value === 'paid' ? 'positive' : 'warning'"
        :label="props.value"
      />
    </q-td>
  </template>
</q-table>
```

Why this pattern works:

- columns stay declarative and easy to reuse
- formatting logic stays out of random template expressions
- scoped slots are only used where the default renderer is not enough

## Dialogs

Use `q-dialog` for focused join, confirm, and payment flows.

Typical structure:

- `q-dialog`
- `q-card`
- `q-card-section` title
- `q-card-section` body
- `q-card-actions align="right"` for actions

Rules:

- Dialogs should have one clear primary action.
- Do not over-style the dialog background.
- Keep the content vertical and readable.

Useful component API pattern:

```vue
<q-dialog v-model="showPaymentDialog">
  <q-card>
    <q-card-section class="text-h6">
      Confirm payment
    </q-card-section>
    <q-card-section>
      <div v-text="paymentSummary" />
    </q-card-section>
    <q-card-actions align="right">
      <q-btn flat label="Cancel" v-close-popup />
      <q-btn color="primary" label="Pay" @click="submitPayment" />
    </q-card-actions>
  </q-card>
</q-dialog>
```

Use `v-model` for visibility and component events for actions instead of ad hoc DOM state.

## Forms

Use:

- `q-form`
- `q-input`
- `q-select`
- `q-toggle`
- `q-checkbox`

Rules:

- Place form controls directly inside `q-card-section`.
- Use standard validation and hints.
- Prefer component props over custom input wrappers.

Useful component API pattern:

```vue
<q-form @submit="submitForm" class="q-gutter-md">
  <q-input
    v-model="form.name"
    label="Name"
    outlined
    :rules="[value => !!value || 'Name is required']"
  />
  <q-select
    v-model="form.wallet"
    :options="walletOptions"
    label="Wallet"
    emit-value
    map-options
  />
  <q-toggle v-model="form.enabled" label="Enabled" />
  <q-btn type="submit" color="primary" label="Save" />
</q-form>
```

Notes:

- use `v-model` for form state instead of manual DOM reads
- use props such as `emit-value`, `map-options`, `rules`, and `label` before custom glue code
- keep business logic in methods or script helpers, not inline expressions

## Alerts And Status

Use:

- `q-banner` for notices and guidance
- `q-chip` or `q-badge` for compact statuses

Good semantic use:

- waiting
- running
- finished
- cancelled
- paid / unpaid
