# Verification and Release

## Contents

- Structural checks
- Behavioral checks
- Runtime checks
- Debugging ownership
- Packaging and release

## Structural Checks

Automate checks that fail on contract drift:

- parse every JSON file;
- compare config export names with WIT and source exports;
- ensure every API/event target exists and has compatible visibility/auth;
- ensure every path placeholder has an intentional mapping;
- compare host calls in source with requested permissions;
- validate policy keys/fields against the selected runtime;
- compare every documented API operation with its configured route, validation boundary, and response mapper;
- compare schema tables/fields with cumulative migrations;
- verify every static/UI path exists and stays inside the extension root;
- reject runtime Vue templates, `eval`, `new Function`, direct extension API `fetch`, and secret logging;
- inspect public response mappers for private fields; and
- verify `module.wasm` starts with `\0asm` and loads as a component.

Do not test only source text or isolated methods. Execute the route-to-export, button-to-client, and event-to-storage paths with fakes or the runtime.

## Behavioral Checks

Derive tests from the product contract, not a fixed example. Cover:

- every input boundary and state transition;
- authenticated owner isolation and foreign IDs;
- public field filtering and relationship checks;
- missing/malformed host responses;
- partial multi-row failure strategy;
- destructive action preconditions;
- idempotency/replay for events and retries;
- permission denial and absent optional capability;
- external/cross-extension response validation when used; and
- persisted state after restart.

Use injected in-memory host adapters for fast domain/export tests. Keep one runtime-level test that invokes the built component with the real WIT bindings; mocks can otherwise hide field-name and component ABI errors.

For browser tests, run the shipped JS under a CSP-equivalent environment that disables string code generation. Traverse the rendered tree/DOM and invoke the actual button handler. Confirm the exact API payload and disabled/loading states.

## Build Checks

Use a single documented build command backed by a pinned local tool. Delete/rebuild the artifact to prove it is not stale. Record tool versions and lock dependencies. Do not accept a build because source or bundle timestamps changed: require successful componentization, a changed `module.wasm` timestamp/hash, and a component load against the selected WIT.

Useful checks:

```bash
node --check static/admin.js
node --check static/public.js
node --test dev/test/*.test.js
xxd -l 4 wasm/module.wasm
```

Use the selected language’s component tooling to inspect/load the component. A core WASM module and a WebAssembly Component share magic bytes; successful component loading against the WIT world is the meaningful check. Capture the target loader/activation evidence that proves the installed bytes—not merely the source-tree bytes—were accepted as a component.

## Runtime Checks

Install into the exact target LNbits instance. Verify server startup accepts:

- config schema;
- permissions/policies;
- storage migrations;
- component/WIT imports and exports;
- API/UI route registration; and
- resource limits.

Inspect the selected runtime's loader/registration lifecycle to determine when a rebuilt component becomes active. If it loads or caches the component at server startup, restart after every `module.wasm` rebuild; a browser reload is insufficient.

Run at least one authenticated flow and every public flow signed out. Restart LNbits and verify persistence. When payments/events are present, create an unpaid invoice first, then settle one and replay its event where the environment permits.

Use headed Chromium for the final interaction/visual pass when available; do not install another browser unnecessarily. Exercise actual buttons and bridge dialogs. Confirm parent-side prompts such as external navigation instead of bypassing them. If an LNbits disclaimer blocks automation, inspect how the selected target records legitimate acceptance and seed that state only for the test user. Keep credentials in environment variables, never scripts or the repository.

Test SQLite and PostgreSQL whenever the extension uses storage types, filters, sorting, timestamps, lists, or migrations. Unit fakes do not catch SQL dialect errors.

## Debugging Ownership

Identify the failing layer before editing:

| Evidence | Likely owner |
|---|---|
| Button has no request/log | UI event wiring/validation. |
| CSP `unsafe-eval` violation | Runtime template compilation in extension UI. |
| Bridge rejects route | Config route/auth mismatch or client path mismatch. |
| Export returns `{ok:false}` | Extension validation/domain/host adapter. |
| Server fails before export log | LNbits config/router/component/host runtime. |
| SQL traceback in `core/wasm_ext/storage` | Runtime adapter or invalid extension schema/data; trace exact failing value. |
| Event arrives but wrong owner/no write | Event owner-resolution policy or extension event validation. |

Do not mask a confirmed core failure inside extension code. Produce a minimal core reproduction and ask before changing core.

## Packaging and Release

Read `_archive_config_name`, `load_archive_config`, `validate_archive`, and the WASM extraction path in `core/models/extensions.py` before packaging. Reproduce exactly the archive nesting, top-level-entry assumptions, and forbidden-file rules enforced by the selected runtime. Independently reject absolute paths, parent traversal, unsafe symlinks, and ambiguous/multiple roots if the loader does not. Ensure the configured module and every referenced UI/static/storage/OpenAPI path are included, while source caches, dependencies, test data, secrets, local databases, and editor files are excluded. Keep source/build files in the repository for reproducibility; include them in the install archive only when the target distribution contract permits them.

For repository-backed discovery, `manifest.json` is separate metadata. A single-repository entry commonly uses:

```json
{"repos":[{"id":"exampleext","organisation":"owner","repository":"repo"}]}
```

The manifest ID must match `config.id` and the installed extension ID. Do not copy runtime fields into this manifest. Confirm this shape against the selected runtime's manifest models.

Trace the selected distribution channel end to end. Repository-backed, explicit-archive, central-catalog, and custom-manifest flows may choose different archive URLs, release metadata, and hash enforcement. Determine whether the installer downloads a generated source archive or a named release asset, whether the installable tree must be at repository root, and whether a published digest is actually verified. Do not claim supply-chain pinning when the chosen channel does not enforce the digest.

Before release:

1. bump `config.version`;
2. rebuild the component from clean source;
3. run all focused and runtime checks;
4. verify a clean install and upgrade from the previous released schema;
5. tag the exact tested commit;
6. publish release notes listing permissions, migrations, behavior changes, and target compatibility; and
7. verify LNbits can discover/download/install the published archive.

Add `manifest.json` only when the chosen distribution channel needs repository discovery metadata. It does not replace `config.json` and its organization/repository values must match the actual release host.

Inspect the finished archive before upload: verify its paths against the target loader, compare the archived component bytes/hash with the tested `module.wasm`, then install through the real discovery channel. Preserve an evidence chain containing the source/tag commit, resolved archive URL, downloaded archive hash, archived component hash, installed component hash, installed config/version, approved permissions, activation/component-load evidence, and post-restart behavioral results. The tested, archived, and installed component hashes must match.
