# Sandboxed Frontend

## Contents

- Boundary
- Core assets
- Bridge
- CSP-safe architecture
- Forms and dialogs
- Notifications, QR, and payment watching
- Frontend verification

## Boundary

The extension UI is a document inside an iframe with `sandbox="allow-scripts"`. Without `allow-same-origin`, it has an opaque origin even though URLs use the LNbits host. Parent CSS does not inherit. Parent `window`, cookies, `LNbits`, `window.g`, Vue app, stores, registered components, and DOM are not extension APIs.

All privileged behavior must cross the parent bridge. Direct extension API `fetch` is blocked by CSP (`connect-src 'none'`) and bypasses route allow-listing. HTML submission is blocked (`form-action 'none'`).

## Core Assets

Read `routes/assets.py` or the inspector output. Load only listed files through:

```text
/ext-assets/<extension-id>/_lnbits/<asset-name>
```

Typical runtimes expose LNbits/Quasar CSS, material icons, Vue, Quasar UMD, and a QR renderer, but the selected runtime’s asset map is authoritative. Extension assets use:

```text
/ext-assets/<extension-id>/<relative-static-path>
```

Loading CSS/JS into the iframe creates iframe-local styles/runtime objects. It does not expose parent-registered LNbits components. If a core component is not provided as a standalone iframe asset, reproduce only the necessary behavior locally or request a core asset/API addition.

## Bridge

Read `lnbits/static/js/wasm-extension-component.js` for the selected ref. Implement a single extension-owned browser SDK instead of duplicating message code per page.

Connection protocol:

1. Create a `MessageChannel` and request ID.
2. Send `window.parent.postMessage({type: 'lnbits-extension:connect', id}, parentOrigin, [port2])`.
3. Wait on `port1` for `{type: 'lnbits-extension:connected', id}`.
4. Send requests as `{type: 'lnbits-extension:request', id, action, ...payload}`.
5. Resolve/reject matching `{type: 'lnbits-extension:response', id, ok, data/error}`.
6. Receive subscriptions as `{type: 'lnbits-extension:event', subscriptionId, ...}`.
7. Apply timeouts, remove listeners, close ports, and unsubscribe on page/dialog teardown.

Derive `parentOrigin` from `new URL(window.location.href).origin`; never use `*` for the connect target. Validate message type, request/subscription ID, and expected port. Do not accept window-wide messages as trusted bridge responses after the port is established.

Current bridge actions commonly include:

| Action | Purpose |
|---|---|
| `context` | Extension ID, public flag, mapped route parameters, query. |
| `api` | Call one declared and context-allowed extension API route. |
| `ui.notify` | Render parent LNbits Quasar notification (`positive`, `negative`, `warning`, `info`). |
| `ui.scan_qr` | Parent scanner; requires `ui.camera.scan_qr` permission/approval. |
| `payment.subscribe` | Watch a payment hash returned by this extension’s API. |
| `payment.unsubscribe` | Stop a subscription and clean parent resources. |
| `navigation.replace` | Replace the route within this extension only. |
| `navigation.open_new_tab` | Ask the user before opening an HTTP(S) URL in a new tab. |
| `storage.session.get` / `storage.session.set` | Extension-namespaced parent session storage; keys are limited to 128 safe characters and values to 4 KiB. |
| `websocket.subscribe` / `websocket.unsubscribe` / `websocket.send` | Subscribe, close, or send on an extension-local WebSocket; requires `websocket.subscribe`. |
| `permissions.request` | Request supported per-user grants from an authenticated page. |
| `permissions.request_background_payment` | Request the declared `wallet.pay_invoice_background` grant. |
| `permissions.request_wallet_payment_watch` | Request the declared `wallet.payments.watch` grant. |

Confirm action names and payloads in the selected runtime before use.

API client methods must call only configured routes below `/api/v1/ext/<extension-id>`. Parse the runtime envelope once. Preserve HTTP method and JSON body exactly. Log useful method/path/error context without logging secrets.

## CSP-Safe Architecture

Preferred choices:

1. Static HTML owns markup; JavaScript attaches listeners and updates DOM.
2. Vue/Quasar app uses handwritten render functions.
3. Vue templates are precompiled during the build and only render functions ship.

Forbidden runtime paths include `template: '<...>'`, mounting DOM templates containing directives, `new Function`, and `eval`. Test with VM/browser string code generation disabled.

Use `textContent`, DOM properties, or escaped framework children for untrusted values. Never interpolate user content into HTML, selectors, style strings, or URLs without validation/encoding.

## Forms and Dialogs

Do not rely on native form navigation. Use an explicit click handler or prevent default and call the same action method. A submit button without a working handler is not wired.

Compute validity from the actual mutable form state. Disable the primary action when invalid, loading, or already submitted. Revalidate inside the action before calling the API. Test the rendered button’s click handler, not merely the method in isolation.

For modal behavior, implement:

- backdrop and explicit Close action;
- `role="dialog"`, `aria-modal`, title association, and live status text;
- keyboard/focus behavior appropriate to complexity;
- bottom action row consistent with LNbits;
- cleanup on close; and
- immediate close or clear state after successful completion when requested.

Use native elements plus Quasar utility classes for small pages. Load Quasar JS and create an iframe-local app only when actual Quasar components/plugins reduce code or improve accessibility.

## Notifications, QR, and Payment Watching

Use `ui.notify` for core-looking toasts; the parent renders its own Quasar Notify. Notify after confirmed state changes, on meaningful waiting states, and on errors. Avoid duplicate inline error plus toast unless the inline message remains necessary for accessibility.

To match LNbits QR behavior without accessing `lnbits-qrcode`:

- render the QR with the exposed QR library;
- encode the validated scheme/value;
- wrap actionable invoices in `href="lightning:<bolt11>"` when wallet opening is intended;
- provide a labeled Copy action using clipboard write;
- never put secrets other than the explicitly displayed transferable value in the QR; and
- keep QR click and copy keyboard accessible.

For payment watching, subscribe only to a payment hash returned through the same extension API, handle settled/error events, tolerate duplicate settled events in UI, and unsubscribe when the dialog/page closes. UI confirmation is not the authoritative paid-state write; backend event processing is.

## Extension-local WebSockets and User Grants

Do not create a WebSocket directly from the sandboxed iframe. With `websocket.subscribe` declared and approved, use the bridge actions above. A subscription is scoped to this extension and an `itemId` matching `^[A-Za-z0-9][A-Za-z0-9:_-]{0,127}$`; listen for bridge event `websocket.message`, validate its JSON payload, and unsubscribe on teardown. The parent forwards client messages to other peers on the same item, so a client message is never trusted state.

Use `permissions.request_background_payment` and `permissions.request_wallet_payment_watch` only from an authenticated page and only after explaining the selected wallet and action. Handle a denial as normal control flow. These grants are per user and wallet; they are not proof that another user, route, or component invocation may use the wallet.

## Frontend Verification

Test at least:

- scripts parse without runtime compilation;
- bridge connection/request timeout and error paths;
- rendered invalid action is disabled;
- rendered valid action invokes the expected client method/payload;
- user-controlled strings use text nodes/escaped bindings;
- public pages cannot call authenticated routes through the bridge;
- dialog cleanup unsubscribes and unmounts local apps;
- payment settlement updates/closes UI exactly once;
- WebSocket subscription validates the item ID, handles close/error, and closes on teardown;
- user-grant denial leaves payment/watch UI safe and usable;
- clipboard/QR actions carry the correct value; and
- errors produce a safe parent notification.

Browser warnings about unsupported feature-policy names or early layout are not proof of extension failure. Prioritize failed bridge responses, CSP violations, server tracebacks, and observed state.
