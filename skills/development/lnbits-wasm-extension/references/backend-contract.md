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
| List user wallets | `wallet.list` | Authenticated. |
| Read wallet balance | `wallet.balance.read` | Authenticated; host checks ownership. |
| Create incoming invoice | `wallet.create_invoice` | Authenticated; host checks wallet ownership. |
| Create public incoming invoice | `wallet.create_invoice_public` | Public; policy uses `table` and `wallet_field`. |
| Pay invoice | `wallet.pay_invoice` | Authenticated; high-risk, request only when required. |
| External HTTP | `http.request` | Authenticated; policy allow-lists exact HTTPS origins. |
| Other extension API | `extension.api.request` | Authenticated; policy allow-lists extension ID and read/write access. |
| Currency/server/Lightning helpers | `utils.basic` | Confirm each method’s auth flag in generated contract. |
| QR camera bridge | `ui.camera.scan_qr` | UI permission with parent approval. |

System ID/time/log methods may require no permission; confirm the generated contract. Never request a plausible permission name that is absent from `permission_ids`.

Policy examples:

```json
{"id":"ext.storage.read_public","policies":[
  {"table_name":"records","public_fields":["id","name"]}
]}
```

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

Public storage is row-by-ID and field allow-listed. It is not a public list/search/aggregation API. Design a safe projection only if the product needs one, and preserve a private authoritative record where correctness matters.

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
