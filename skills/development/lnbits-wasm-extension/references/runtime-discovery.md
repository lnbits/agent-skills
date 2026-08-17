# Runtime Discovery

## Contents

- Target selection
- Local inspection
- Missing runtime
- Authoritative files
- Generated contract
- Conflict rule

## Target Selection

The target is, in priority order:

1. the LNbits checkout/ref/version explicitly named by the user;
2. the LNbits process/container the user will install into;
3. a local checkout found in the workspace or a sibling directory.

Never silently choose another ref, fork, old release, or unrelated local checkout. Record the target with:

```bash
git -C "$LNBITS_ROOT" rev-parse HEAD
git -C "$LNBITS_ROOT" describe --tags --always --dirty
```

If a running instance is the target, also record its reported version and confirm its source/container matches the inspected code.

Do not assume an installed WASM extension lives under the Python extension directory. Resolve `settings.wasm_extensions_dir` and its validators from the selected runtime, then inspect the actual installed tree.

## Local Inspection

Locate candidates without scanning the entire machine:

```bash
find .. "$HOME/Work" -maxdepth 4 \
  -path '*/lnbits/core/wasm_ext/wasm/config.py' -print 2>/dev/null
```

Require these paths:

```text
lnbits/core/wasm_ext/wasm/config.py
lnbits/core/wasm_ext/api/registry.py
lnbits/core/wasm_ext/api/host.py
lnbits/core/wasm_ext/api/background_payments.py
lnbits/core/wasm_ext/api/lnurl.py
lnbits/core/wasm_ext/api/models.py
lnbits/core/wasm_ext/api/permissions.py
lnbits/core/wasm_ext/api/websockets.py
lnbits/core/wasm_ext/client/http.py
lnbits/core/wasm_ext/client/extensions.py
lnbits/core/wasm_ext/storage/crud.py
lnbits/core/wasm_ext/routes/api.py
lnbits/core/wasm_ext/routes/open_api.py
lnbits/core/wasm_ext/routes/ui.py
lnbits/core/wasm_ext/routes/security.py
lnbits/core/wasm_ext/routes/assets.py
lnbits/core/wasm_ext/wasm/events.py
lnbits/core/wasm_ext/wasm/invoke.py
lnbits/core/wasm_ext/wasm/component.py
lnbits/core/wasm_ext/wasm/loader.py
lnbits/static/js/wasm-extension-component.js
lnbits/core/views/extension_api.py
lnbits/core/views/websocket_api.py
lnbits/core/models/extensions.py
lnbits/core/services/extensions.py
lnbits/settings.py
tools/codegen/extension_sdk_typescript.py
```

Run the bundled inspector from the LNbits environment:

```bash
cd "$LNBITS_ROOT"
uv run python /absolute/path/to/lnbits-wasm-extension/scripts/inspect_runtime.py \
  --lnbits-root . > /tmp/lnbits-wasm-runtime.json
```

The report contains the commit, config JSON schema, registered host methods, auth requirements, permissions, request/response schemas, and proxied iframe assets.

Treat a host method's `required_permission: null` as “no unconditional decorator permission,” not “permission-free.” Some methods enforce permissions conditionally inside their implementation. Inspect that method in `api/host.py`; current payment methods choose between an authenticated `wallet.pay_invoice` grant and an unauthenticated `wallet.pay_invoice_background` grant.

Generate the target’s TypeScript SDK contract rather than guessing host shapes:

```bash
cd "$LNBITS_ROOT"
uv run python tools/codegen/extension_sdk_typescript.py \
  --out /absolute/path/to/extension/dev/src/lnbits-host.generated.ts
```

Use repeated `--method <method-id>` options to generate only selected host methods.

## Missing Runtime

If no local checkout or running target is available, stop and ask the user for its location. Do not browse, clone, or substitute a different LNbits ref. If the supplied target lacks `lnbits/core/wasm_ext`, report that it does not provide the WASM contract.

## What Each File Decides

| File | Authority |
|---|---|
| `wasm/config.py` | Accepted `config.json` keys, route verbs/auth, export visibility. |
| `api/registry.py` | Complete registered host-method contract and runtime-only permission IDs. |
| `api/host.py`, `api/utils.py`, `api/lnurl.py`, `api/background_payments.py` | Host behavior, conditional permissions, LNURL handling, and background-payment grants. |
| `api/models.py` | Request/response fields and size/range constraints. |
| `api/permissions.py` | Accepted permission IDs and policy shapes. |
| `client/http.py`, `client/extensions.py` | Outbound HTTP/cross-extension origin, method, header, redirect, timeout, and response-limit enforcement. |
| `api/websockets.py`, `views/websocket_api.py` | Extension websocket endpoint, channel isolation, message limits, and subscribe enforcement. |
| `storage/crud.py` | Schema types, migration operations, owner scope, SQL conversion. |
| `routes/api.py` | HTTP payload merge rules, route mapping, owner-context resolution, errors and limits. |
| `routes/open_api.py` | OpenAPI document paths, route fragment lookup, local `$ref` handling, and generated examples. |
| `routes/ui.py`, `routes/security.py` | iframe route context, CSP, permissions policy. |
| `routes/assets.py` | Exact `_lnbits` assets an iframe may load. |
| `wasm/events.py` | Event selection, owner resolution, exact event payload. |
| `wasm/invoke.py`, `wasm/component.py`, `wasm/loader.py` | Export invocation, component caching/loading, context, and resource limits. |
| `wasm-extension-component.js` | Browser bridge actions, permission prompts, session storage, navigation, and websocket lifecycle. |
| `views/extension_api.py`, `models/extensions.py` | Per-user background-payment and wallet-payment-watch grants. |
| `models/extensions.py`, `settings.py` | WASM install archive layout, installed-WASM directory, manifest sources, release lookup, archive selection, and hash behavior. Trace `_extension_manifest_sources`, release constructors/lookups, `load_archive_config`, validation, and extraction. |
| `extension_sdk_typescript.py` | Generated source-language host contract. |

## Conflict Rule

When this skill, generated types, runtime-local guidance, and runtime code disagree:

1. selected runtime code;
2. generated contract from that runtime;
3. tests shipped with that runtime;
4. guidance bundled with the selected runtime;
5. this skill.

Do not copy another extension to resolve a conflict. It may target a different runtime or contain workarounds and stale assumptions.
