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

Use a single documented build command. Delete/rebuild the artifact to prove it is not stale. Record tool versions and lock dependencies.

Useful checks:

```bash
node --check static/admin.js
node --check static/public.js
node --test dev/test/*.test.js
xxd -l 4 wasm/module.wasm
```

Use the selected language’s component tooling to inspect/load the component. A core WASM module and a WebAssembly Component share magic bytes; successful component loading against the WIT world is the meaningful check.

## Runtime Checks

Install into the exact target LNbits instance. Verify server startup accepts:

- config schema;
- permissions/policies;
- storage migrations;
- component/WIT imports and exports;
- API/UI route registration; and
- resource limits.

Run at least one authenticated flow and every public flow signed out. Restart LNbits and verify persistence. When payments/events are present, create an unpaid invoice first, then settle one and replay its event where the environment permits.

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

The install archive must place `config.json`, `wasm/module.wasm`, and referenced directories at archive root—not inside an extra build directory. Exclude source caches, dependencies, test data, secrets, local databases, and editor files. Include source/build files in the repository for reproducibility unless the distribution policy says otherwise.

Before release:

1. bump `config.version`;
2. rebuild the component from clean source;
3. run all focused and runtime checks;
4. verify a clean install and upgrade from the previous released schema;
5. tag the exact tested commit;
6. publish release notes listing permissions, migrations, behavior changes, and target compatibility; and
7. verify LNbits can discover/download/install the published archive.

Add `manifest.json` only when the chosen distribution channel needs repository discovery metadata. It does not replace `config.json` and its organization/repository values must match the actual release host.
