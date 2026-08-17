# Payments and Events

Read this file only when the requested product creates invoices, pays invoices, reacts to payment settlement, or consumes another LNbits event.

## Incoming Invoice: Authenticated

Use `wallet.create_invoice` only in authenticated context. Accept a wallet ID only from an authenticated owner flow, validate it as a bounded string, and rely on the host’s wallet ownership check. Validate positive amount/currency/memo/tag/extra before the host call. Creating the invoice does not prove settlement.

## Incoming Invoice: Public

Public callers must not choose a wallet ID. Store the receiving wallet ID in a private field on an owner-scoped row and declare a `wallet.create_invoice_public` policy:

```json
{
  "id": "wallet.create_invoice_public",
  "description": "Create public invoices for approved records.",
  "policies": [{"table":"records","wallet_field":"wallet_id"}]
}
```

The public export accepts a bounded `sourceId`, loads the public source row, checks current product state and requested amount/action, then calls `createInvoicePublic({sourceId, amount, currency, memo, extra})`. LNbits privately resolves the wallet field from the source row.

Do not expose the wallet field through `ext.storage.read_public`. Do not accept a public override for amount unless the product explicitly allows and bounds it. Put only minimal routing metadata in `extra`; the runtime nests it under an extension-specific payment key.

## Paid Event

Declare all three links:

```json
"wasm": {
  "exports": [{"name":"handle-invoice-paid","visibility":"event"}]
},
"events": {"onInvoicePaid":"handle-invoice-paid"}
```

and the matching WIT/source export.

Read `wasm/events.py` for the exact selected-runtime payload. Do not guess nesting. Validate at least extension/tag association, source ID, extension-specific extra, payment hash, amount/status, and any referenced entity relationship.

For public invoices, the runtime can resolve the storage owner from the public-invoice source policy and dispatch the event with that owner scope. Confirm this path in the selected runtime before relying on event storage writes. For other invoice paths, verify how owner context reaches the event; do not assume an authenticated request’s user automatically survives into a later event.

Use the payment hash or another runtime-guaranteed natural key as a deterministic storage row ID. Check for an existing record before side effects, and make a replay return success without a second effect. Because a read-then-write sequence may race, avoid irreversible duplicate effects; use deterministic upsert semantics where one stored record is sufficient and test concurrent/repeated delivery.

Closing/disabling a resource blocks new invoice creation. Decide explicitly whether already-issued invoices remain valid; do not accidentally discard paid events merely because current state changed after issuance.

Return no wallet IDs, raw payment records, hashes, preimages, or internal extra structures from public endpoints.

## Outgoing Payment

Generate the wallet payment methods and types from the selected runtime. It may expose separate invoice and LNURL/Lightning-address payment calls, with conditional permissions for authenticated and background contexts. Read the host implementation, LNURL helper, background-payment enforcement, and generated contract before choosing a flow.

For an authenticated outgoing payment, request the permission enforced by that host branch and apply these checks before calling it:

- validate and decode the invoice when helpers exist;
- enforce product-specific amount and fee limits server-side in the component;
- confirm the selected wallet belongs to the authenticated user (the host also checks);
- prevent accidental resubmission with UI loading state and a backend idempotency strategy where possible;
- never log the invoice/preimage; and
- return only data the owner UI needs.

Do not expose outgoing payment through a public export or request the permission for a product that only receives funds.

For background payment, declare the runtime's background permission and obtain the per-user, per-wallet grant through the authenticated browser bridge first. Enforce the approved amount/destination policy and treat denial, revocation, or a missing grant as normal control flow. A public HTTP route must never become a generic payment trigger merely because the component can run without user context.

## Payment Tests

Test the paths applicable to the product:

- invalid/zero/negative/excess amount;
- foreign or missing public source;
- private wallet field absent from public output;
- invoice creation leaves paid state unchanged;
- malformed or unrelated event ignored safely;
- correct paid event applies exactly one effect;
- duplicate and concurrent delivery do not duplicate effects;
- current-state transition behavior for an already-issued invoice;
- wrong owner/wallet denied;
- outgoing amount/fee ceiling; and
- malformed/unsupported LNURL or Lightning address and success-action handling, when used;
- missing, denied, revoked, wrong-wallet, over-limit, or wrong-destination background grants, when used; and
- browser subscription closes and cleans up after settlement/error/dialog close.
