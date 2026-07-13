# Runtime Discovery

## Contents

- Target selection
- Local inspection
- Official repository fallback
- Authoritative files
- Generated contract
- Conflict rule

## Target Selection

The target is, in priority order:

1. the LNbits checkout/ref/version explicitly named by the user;
2. the LNbits process/container the user will install into;
3. a local checkout found in the workspace or a sibling directory; or
4. the official repository current default ref.

Never silently choose another ref, fork, old release, or unrelated local checkout. Record the target with:

```bash
git -C "$LNBITS_ROOT" rev-parse HEAD
git -C "$LNBITS_ROOT" describe --tags --always --dirty
```

If a running instance is the target, also record its reported version and confirm its source/container matches the inspected code.

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
lnbits/core/wasm_ext/api/models.py
lnbits/core/wasm_ext/api/permissions.py
lnbits/core/wasm_ext/storage/crud.py
lnbits/core/wasm_ext/routes/api.py
lnbits/core/wasm_ext/routes/ui.py
lnbits/core/wasm_ext/routes/security.py
lnbits/core/wasm_ext/routes/assets.py
lnbits/core/wasm_ext/wasm/events.py
lnbits/core/wasm_ext/wasm/invoke.py
lnbits/static/js/wasm-extension-component.js
tools/codegen/extension_sdk_typescript.py
```

Run the bundled inspector from the LNbits environment:

```bash
cd "$LNBITS_ROOT"
uv run python /absolute/path/to/lnbits-wasm-extension/scripts/inspect_runtime.py \
  --lnbits-root . > /tmp/lnbits-wasm-runtime.json
```

The report contains the commit, config JSON schema, registered host methods, auth requirements, permissions, request/response schemas, and proxied iframe assets.

Generate the target’s TypeScript SDK contract rather than guessing host shapes:

```bash
cd "$LNBITS_ROOT"
uv run python tools/codegen/extension_sdk_typescript.py \
  --out /absolute/path/to/extension/dev/src/lnbits-host.generated.ts
```

Use repeated `--method <method-id>` options to generate only selected host methods.

## Official Repository Fallback

Use the current default ref at `https://github.com/lnbits/lnbits`. Clone only when local source is unavailable:

```bash
git clone --filter=blob:none https://github.com/lnbits/lnbits.git /tmp/lnbits-runtime
```

Then follow the local inspection steps. If cloning is unavailable, open the repository and navigate to the authoritative paths above on its default ref. Do not hardcode a ref name. If `lnbits/core/wasm_ext` is absent, report that this target does not provide the WASM contract.

## What Each File Decides

| File | Authority |
|---|---|
| `wasm/config.py` | Accepted `config.json` keys, route verbs/auth, export visibility. |
| `api/registry.py` | Complete registered host-method contract and runtime-only permission IDs. |
| `api/host.py`, `api/utils.py` | Host behavior, auth requirement, permission per call. |
| `api/models.py` | Request/response fields and size/range constraints. |
| `api/permissions.py` | Accepted permission IDs and policy shapes. |
| `storage/crud.py` | Schema types, migration operations, owner scope, SQL conversion. |
| `routes/api.py` | HTTP payload merge rules, route mapping, errors and limits. |
| `routes/ui.py`, `routes/security.py` | iframe route context, CSP, permissions policy. |
| `routes/assets.py` | Exact `_lnbits` assets an iframe may load. |
| `wasm/events.py` | Event selection, owner resolution, exact event payload. |
| `wasm/invoke.py` | Export invocation, context and resource limits. |
| `wasm-extension-component.js` | Browser bridge messages and parent-side behavior. |
| `extension_sdk_typescript.py` | Generated source-language host contract. |

## Conflict Rule

When this skill, an online document, generated types, and runtime code disagree:

1. selected runtime code;
2. generated contract from that runtime;
3. tests shipped with that runtime;
4. official documentation for the same ref;
5. this skill.

Do not copy another extension to resolve a conflict. It may target a different runtime or contain workarounds and stale assumptions.
