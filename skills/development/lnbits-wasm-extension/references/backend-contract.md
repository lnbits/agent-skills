# Backend Contract

## Contents

- Config
- Routes and payloads
- Host methods and permissions
- Storage and migrations
- WIT and JavaScript components
- Export structure

## Config

Generate the accepted schema from the selected runtime; do not infer keys. A typical minimal shape is:

```json
{
  "id": "exampleext",
  "name": "Example Extension",
  "short_description": "One sentence.",
  "version": "0.1.0",
  "extension_type": "wasm",
  "wasm": {
    "module": "wasm/module.wasm",
    "wit": "wasm/lnbits-extension.wit",
    "world": "exampleext",
    "exports": [
      {"name": "create-record", "visibility": "authenticated"}
    ]
  },
  "ui_routes": [
    {"path": "/exampleext", "entrypoint": "ui/admin.html", "auth": "user"}
  ],
  "api_routes": [
    {"method": "POST", "path": "/records", "export": "create-record", "auth": "user"}
  ],
  "permissions": []
}
```

Include `wasm.wit` and `wasm.world` when accepted by the target. Add `min_lnbits_version` only after identifying the first compatible release; never ship a placeholder. Use extension IDs safe for paths and WIT identifiers. The installed directory name and `config.id` must match.

Valid export visibility and route auth are separate vocabularies:

- export: `authenticated`, `public`, `event`;
- API route auth: `user`, `public`;
- UI route auth: `user`, `public`.

An API route may invoke only a non-event export with matching public/private intent. An event export is invoked only by a declared event.

For a public route that must operate on the owner of a private source row, use the selected runtime's `ownerContext`; it resolves the source row owner and invokes the component with that owner scope. It is not an authorization bypass: use it only for a route whose source ID is mapped from a path/body field and whose operation is safe for public callers.

## Routes and Payloads

Configured API paths are mounted below `/api/v1/ext/<extension-id>`. UI paths are mounted below `/ext`. Static assets are served below `/ext-assets/<extension-id>`.

Map every path placeholder explicitly:

```json
{
  "method": "GET",
  "path": "/records/{record_id}",
  "export": "get-record",
  "auth": "user",
  "path_params": {"record_id": "recordId"}
}
```

The runtime converts unmapped query keys from snake_case to camelCase. Inspect `routes/api.py` for the selected ref to confirm merge order between path, query, and JSON body. Never rely on a client-supplied identifier for authorization; load through owner-scoped storage or validate the relationship explicitly.

Use only accepted verbs from `WasmAPIRouteConfig`. Body-bearing routes accept JSON objects, not arrays or form data, and runtime request-size limits apply.

## Host Methods and Permissions

Obtain the complete method list from `scripts/inspect_runtime.py`. For each method record:

- method ID and SDK name;
- `require_auth`;
- required permission;
- request/response schema and limits;
- policy shape, if policy-aware.

Common capabilities include:

| Host need | Permission | Context/policy |
|---|---|---|
| Owner row read/list | `ext.storage.read` | Authenticated; owner scoped. |
| Owner row create/update/delete | `ext.storage.write` | Authenticated or event with resolved owner. |
| Allow-listed row-by-ID read | `ext.storage.read_public` | Public; policies use `table_name` and `public_fields`. |
| Source-scoped public list/search/sort | `ext.storage.read_public` | Public; policy must also set `source_id_field`; queries may use only public fields plus that fixed source field. |
| Public child-row append | `ext.storage.append_public` | Public; policy fixes target/source tables, source field, allowed fields, and a per-source row cap. |
| List user wallets | `wallet.list` | Authenticated. |
| Read wallet balance | `wallet.balance.read` | Authenticated; host checks ownership. |
| Create incoming invoice | `wallet.create_invoice` | Authenticated; host checks wallet ownership. |
| Create public incoming invoice | `wallet.create_invoice_public` | Public; policy uses `table` and `wallet_field`. |
| Pay invoice | `wallet.pay_invoice` | Authenticated; high-risk, request only when required. |
| External HTTP | `http.request` | Authenticated; policy allow-lists exact HTTPS origins. |
| Other extension API | `extension.api.request` | Authenticated; policy allow-lists extension ID and read/write access. |
| Currency/server/Lightning helpers | `utils.basic` | Confirm each method’s auth flag in generated contract. |
| QR camera bridge | `ui.camera.scan_qr` | UI permission with parent approval. |
| Publish extension-local WebSocket data | `websocket.publish` | Public/auth/event; policy sets `max_messages_per_second` (1–100). |
| Subscribe/send on an extension-local WebSocket | `websocket.subscribe` | UI bridge permission; no host import. |
| Pay without an authenticated component context | `wallet.pay_invoice_background` | Per-user, per-wallet bridge grant with amount and destination policy. |
| Watch a user's wallet payments | `wallet.payments.watch` | Per-user, per-wallet bridge grant. |

System ID/time/log methods may require no permission; confirm the generated contract. Never request a plausible permission name that is absent from `permission_ids`.

Policy examples:

```json
{"id":"ext.storage.read_public","policies":[
  {"table_name":"records","source_id_field":"project_id","public_fields":["id","name"]}
]}
```

`getPublic` remains a row-by-ID read. `getPublicPaginated` requires `sourceId`, forcibly filters by the declared `source_id_field`, and permits filters/search/sort only on public fields. Do not use public pagination as an unbounded directory/search API.

```json
{"id":"ext.storage.append_public","policies":[
  {"table":"messages","source_table":"threads","source_id_field":"thread_id",
   "allowed_fields":["body","display_name"],"max_rows_per_source":100}
]}
```

The host generates the child row ID, resolves ownership from the source row, injects the source ID, and enforces the cap. Never accept `id`, the owner field, the source field, or any private/moderation field from a public append.

```json
{"id":"wallet.create_invoice_public","policies":[
  {"table":"records","wallet_field":"wallet_id"}
]}
```

```json
{"id":"http.request","policies":[
  {"host":"https://api.example.com"}
]}
```

```json
{"id":"extension.api.request","policies":[
  {"id":"target-extension","access":["read"]}
]}
```

```json
{"id":"websocket.publish","policies":[
  {"max_messages_per_second":10}
]}
```

Use exact policy keys from `api/permissions.py`; similar-looking keys are not interchangeable.

## Storage and Migrations

Every table requires an `id` field. Supported field types and operations come from `storage/crud.py`. At the current contract baseline:

- types: `string`, `integer`, `number`, `boolean`, `datetime`;
- optional modifiers: `nullable`, `default`, `list`;
- migration operations: `create_table`, `add_field`, `create_index`.

`list: true` values are JSON-encoded into text storage. Datetime values cross the component boundary as Unix timestamps and are converted by the database adapter. Validate against both SQLite and PostgreSQL; do not emit database-specific timestamp strings.

Schema:

```json
{
  "version": 1,
  "tables": {
    "records": {
      "fields": [
        {"name":"id","type":"string"},
        {"name":"name","type":"string"},
        {"name":"created_at","type":"datetime"}
      ]
    }
  },
  "indexes": []
}
```

Initial migration:

```json
{
  "version": 1,
  "operations": [
    {
      "op": "create_table",
      "table": "records",
      "fields": [
        {"name":"id","type":"string"},
        {"name":"name","type":"string"},
        {"name":"created_at","type":"datetime"}
      ]
    },
    {"op":"create_index","table":"records","name":"records_by_name","field":"name"}
  ]
}
```

Keep field definitions identical between migration and schema. Do not define `__lnbits_owner_id__`; LNbits creates, filters, and removes it. `set` is an owner-protected upsert by `id`. A normal index is not a uniqueness constraint. Use deterministic IDs for natural uniqueness and test replay/races when uniqueness matters.

Released migrations are immutable. Add `0002_*.json`, `0003_*.json`, and so on, and advance the schema. Do not assume rollback or arbitrary SQL operations exist.

Public storage is field allow-listed. Row-by-ID reads need `ext.storage.read_public`; source-scoped pagination additionally needs an exact `source_id_field`, and public append needs a separate allow-list/cap policy. Preserve a private authoritative record where correctness matters.

## Extension-local WebSockets

Use only for transient extension-local collaboration or UI updates, not authoritative writes. Add both permissions when the component publishes and the iframe subscribes:

```json
[
  {"id":"websocket.publish","policies":[{"max_messages_per_second":10}]},
  {"id":"websocket.subscribe"}
]
```

The component host call is `websocket.publish({itemId, data})`; generate its exact WIT/SDK type. The iframe connects only through the parent bridge to `/api/v1/ext/ws/<extension-id>/<item-id>`, never directly. Item IDs are extension-namespaced and must match `^[A-Za-z0-9][A-Za-z0-9:_-]{0,127}$`; JSON publishes are limited to 64 KiB, clients to 8 KiB/message and 60 messages/second, and the approved publish rate is capped at 100 messages/second. Treat received client messages as untrusted and validate them in the UI/component before changing state.

## Per-user Wallet Grants

`wallet.pay_invoice_background` and `wallet.payments.watch` are declared in `config.json`, but use is authorized by a user through bridge actions. Background payment is enforced when the existing wallet payment host call runs without an authenticated component context; payment watch is a bridge capability. Do not request either at install time unless the product reaches its corresponding bridge action.

- `permissions.request_background_payment` requests a user's wallet, positive `maxAmount`, and `destinationPolicy` (`own_wallets_only` or `external_allowed`). Background payments reject shared/non-sendable wallets and enforce the saved grant per wallet.
- `permissions.request_wallet_payment_watch` requests one user-owned wallet. It enables the bridge's wallet-payment subscription for that wallet.

Use only on authenticated UI routes, handle refusal, and make the wallet/action/limit explicit in the product UI. Read `extension_api.py`, `models/extensions.py`, and `wasm-extension-component.js` for the selected ref before constructing request payloads.

## WIT and JavaScript Components

WIT import interfaces must match `host_interface`, kebab-case host names, request records, and response records from the generated runtime contract. Import only the interfaces used by the source. WIT record fields are kebab-case; JavaScript bindings usually expose camelCase. Confirm generated bindings rather than guessing conversions.

The world exports every configured function:

```wit
package lnbits:extension;

world exampleext {
  import host;
  export create-record: func(request-json: string) -> string;
}
```

For JavaScript, keep host bindings in `dev/src/lnbits-sdk.js` and domain exports in `dev/src/index.js`. Bundle them deterministically, then componentize:

```bash
npx --yes @bytecodealliance/jco componentize \
  dev/dist/index.bundle.js \
  --disable all --enable clocks --enable random --enable stdio \
  --wit wasm/lnbits-extension.wit \
  --world-name exampleext \
  -o wasm/module.wasm
```

Pin the build dependency/version in the actual project lockfile for reproducible releases. Enable only WASI features the component build requires. The host capabilities still require WIT imports and approved LNbits permissions.

## Export Structure

Use one wrapper for all exports:

```js
function runJson(operation) {
  try {
    return JSON.stringify({ok: true, data: operation()})
  } catch (error) {
    return JSON.stringify({ok: false, error: publicError(error)})
  }
}
```

Log unexpected failures through the generated `system.log` request shape (`{level: "warning", message: "..."}`), or an explicitly tested local wrapper; do not guess argument order. Do not log full request/event payloads. Split expected validation errors from unexpected failures if the user-facing message could reveal internals. Validate pure product rules before host mutation. For multi-row changes, remember the host API may not provide a transaction; order writes to minimize partial state and design repair/idempotency where consistency is critical.
