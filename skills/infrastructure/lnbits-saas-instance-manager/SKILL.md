---
name: lnbits-saas-instance-manager
description: Guide an AI through choosing, buying, launching, paying for, and managing an LNbits SaaS instance on https://my.lnbits.com using the LNbits SaaS API at https://api.lnbits.com. Use when a user wants to register/login, select a tier, create an instance, pay by one-time invoice, fiat subscription, or on-demand LNURL, and manage lifecycle actions.
---

# LNbits SaaS Instance Manager

Use this skill to help a user buy, launch, and manage an LNbits instance from `https://my.lnbits.com/` through the SaaS API at `https://api.lnbits.com`.

Use the API contract below and live API responses. If a required choice is ambiguous, stop and ask the user before proceeding.

## Base Rules

- API origin: `https://api.lnbits.com`.
- Website origin: `https://my.lnbits.com`.
- Public endpoints: `GET /`, `GET /pricing`, `POST /signup`, `GET /confirm-email`, `POST /login`, `POST /logout`, `POST /password-recovery`, `POST /reset-password`.
- Instance endpoints require authentication.
- Browser-style sessions use `withCredentials: true` and the `access_token` cookie.
- API automation may use `Authorization: Bearer <access_token>` from login.
- Do not store plaintext credentials unless the user explicitly asks for that exact storage method. Prefer using the current session token only, or ask which credential store to use.
- Signup requires email confirmation. If the AI cannot access the inbox, ask the user to complete confirmation or paste the confirmation URL/token.
- Payments require user-controlled funds or checkout approval. Do not claim payment is complete until the API shows a paid payment or an active/enabled instance.

## Required User Inputs

Collect only what is needed for the chosen path:

- Account: existing login credentials, or email/password for signup.
- Instance purpose: personal experiment, team, production, large rollout.
- Capacity needs: expected users, expected extensions, storage needs.
- Funding source: bundled/easy funding source, own funding source, or experimental release candidate.
- Domain: generated `*.lnbits.com`, requested custom subdomain, or custom domain.
- Billing mode: on-demand LNURL/hourly, one-time weekly/monthly/yearly invoice, or recurring subscription.
- Payment preference: Lightning/sats, fiat invoice if available, or fiat subscription checkout.
- Quantity: number of intervals for one-time invoices, or number of on-demand hours.

If any answer materially changes tier, instance type, payment path, or domain eligibility, ask before continuing.

## Discover Current Options

Use an `API` variable in examples:

```bash
API="https://api.lnbits.com"
```

Check service status:

```bash
curl -sS "$API/"
```

Expected shape: `{"status":"OK","version":"...","timestamp":...}`. Use this timestamp when comparing instance expiry times if needed.

Fetch live pricing:

```bash
curl -sS "$API/pricing"
```

Pricing shape:

- Top-level tiers currently follow the schema `personal`, `premium`, `business`, `enterprise`; use the live response as authoritative.
- Tier fields: `label`, `description`, `storage`, `users`, `extensions`, `custom_subdomain`, `custom_domain`, `hourly`, `weekly`, `monthly`, `yearly`.
- Interval objects expose `price`.
- Public pricing intentionally does not expose provider subscription IDs.
- Valid intervals: `hourly`, `weekly`, `monthly`, `yearly`.

After login, fetch instance types:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/types"
```

Instance type shape:

```json
{
  "tag": "lnbits_spark_latest",
  "label": "Spark L2 (easy)",
  "description": "...",
  "has_sidecar": true
}
```

Use the returned list as authoritative. If the user wants "easy" or has no funding source, choose an option whose label/description supports that and preferably has `has_sidecar: true`. If the user has their own funding source, choose a non-sidecar LNbits type only if available. For release-candidate or experimental images, ask for explicit confirmation.

## Tier Selection

Use live `GET /pricing` data. Choose the lowest tier that satisfies all stated constraints:

- Users must fit `users`; `0` means no configured limit in this API schema.
- Extensions must fit `extensions`; `0` means no configured limit in this API schema.
- Storage must satisfy the user's storage requirement.
- Custom `*.lnbits.com` subdomain requires `custom_subdomain: true`.
- Custom non-`lnbits.com` domain requires `custom_domain: true`.
- If the user does not specify users/extensions/storage/domain and the choice matters, ask rather than guessing.

If multiple tiers fit and the user has not given a preference, present the tradeoff and ask them to choose. Do not select solely because a label says "most popular" unless the user asked for that heuristic.

## Signup And Login

Signup request:

```bash
curl -sS -X POST "$API/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"USER_EMAIL","password":"PASSWORD","password_repeat":"PASSWORD"}'
```

Signup fields:

- `email`: required, valid email, 3-50 chars.
- `username`: optional, 3-50 chars, alphanumeric plus `._%+-`.
- `password` and `password_repeat`: required, 8-50 chars, must match.
- New users are inactive until email confirmation.

Email confirmation:

```bash
curl -sS "$API/confirm-email?email_confirmation_token=TOKEN_FROM_EMAIL"
```

Login uses form data, not JSON. Send `email`, `username`, and `password`; the API authenticates against the `username` form field, so set `username` to the email/username being used to log in.

```bash
curl -sS -X POST "$API/login" \
  -F "email=EMAIL_OR_USERNAME" \
  -F "username=EMAIL_OR_USERNAME" \
  -F "password=PASSWORD"
```

Login returns:

```json
{"access_token":"...","token_type":"bearer"}
```

Use the token:

```bash
TOKEN="..."
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance"
```

If using a browser or HTTP client with cookies, preserve the `access_token` cookie and send credentials on later calls.

## Create Instance

Create the instance record before payment:

```bash
curl -sS -X POST "$API/instance" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_plan_tier": "personal",
    "payment_plan_interval": "weekly",
    "instance_type": "lnbits_spark_latest",
    "domain": null
  }'
```

Request fields:

- `payment_plan_tier`: one of the live pricing tiers.
- `payment_plan_interval`: `hourly`, `weekly`, `monthly`, or `yearly`; use `weekly/monthly/yearly` for `/instance/buy` and `/instance/subscribe`.
- `instance_type`: optional; if omitted, the API uses the first configured image.
- `domain`: optional valid domain. If omitted, the API generates a unique `*.lnbits.com` domain.

Validation behavior:

- Invalid `instance_type`, tier, or interval returns `400`.
- Requested subdomains ending in the configured SaaS suffix require tier support for `custom_subdomain`.
- Custom domains outside the SaaS suffix require tier support for `custom_domain`.
- Duplicate or excluded domains return `400`.

Response is an instance record with fields including `id`, `domain`, `lnurl`, `installtoken`, `is_active`, `is_enabled`, `timestamp`, `timestamp_start`, and `timestamp_stop`. Newly created instances start inactive and disabled until payment is processed.

Useful instance links:

- Instance wallet: `https://<domain>/wallet`
- First install: `https://<domain>/first_install?token=<installtoken>`
- Backup API: `https://<domain>/admin/api/v1/backup`

## Pay And Launch

Launch is completed by payment processing. After payment, the service extends `timestamp_stop`, marks the payment paid, then deploys a new instance or enables an existing inactive instance. Launch time after payment depends on the tier and current load; ask the user to wait and check instance status/logs if the instance is not active/enabled within about a couple minutes after payment.

### One-Time Weekly/Monthly/Yearly Invoice

Use this for prepaid weekly/monthly/yearly intervals. Do not use this flow for `hourly`.

```bash
curl -sS -X PUT "$API/instance/buy" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instance_id":123,"quantity":1,"is_fiat":false}'
```

Request fields:

- `instance_id`: integer instance id.
- `quantity`: number of selected intervals to buy.
- `is_fiat`: boolean; when true, the payment request uses the configured fiat provider if supported.

Some clients may include `payment_plan_name`, but the API determines the plan from the instance tier and interval. Do not rely on `payment_plan_name` to change the plan.

Response shape:

```json
{
  "payment_hash": "...",
  "payment_request": "...",
  "amount": 12345,
  "memo": "..."
}
```

Present `payment_request` to the user for payment. After payment, poll instance and payment reads until `paid: true` and `is_active/is_enabled: true`.

### Recurring Fiat Subscription

Use this when the user explicitly wants recurring billing.

```bash
curl -sS -X PUT "$API/instance/subscribe" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instance_id":123}'
```

Response shape:

```json
{
  "ok": true,
  "subscription_request_id": "...",
  "checkout_session_url": "...",
  "error_message": null
}
```

If `checkout_session_url` is present, send the user there to approve checkout. Store `subscription_request_id` for unsubscribe. The subscription is recorded immediately, but becomes enabled only after the first subscription payment webhook is processed.

Some clients may include `payment_plan_name`, but the API determines the plan from the instance tier and interval.

### On-Demand Hourly/LNURL

The SaaS API creates an `lnurl` for each instance. This API contract does not expose a dedicated endpoint for creating arbitrary hourly invoices from that LNURL.

For user-facing on-demand purchase:

1. Create the instance with the selected tier and type.
2. Use the instance `lnurl` as the payment target.
3. Ask the user how many hours they want to fund.
4. Pay at least the configured minimum. The service enforces the minimum from tier hourly price and minimum hours.
5. After payment, poll until the payment webhook marks the instance active/enabled.

If an automated hourly invoice is required and the user has not provided a supported UI flow or payment automation path, stop and ask how they want the invoice generated.

## Polling And Verification

List instances:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance"
```

Read payments:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/payments"
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/123/payments"
```

Read logs:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/logs"
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/123/logs"
```

Read subscriptions:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/subscriptions"
curl -sS -H "Authorization: Bearer $TOKEN" "$API/instance/123/subscriptions"
```

Completion criteria:

- Payment record has `paid: true`.
- Instance has `is_active: true` and `is_enabled: true`.
- `timestamp_stop` is in the future.
- Logs include `update_payment`; first launch should also produce a deploy-related log.
- The instance domain works. If admin access is not visible yet, wait and re-check logs; first launch may take about 45-60 seconds after payment.

Frontend status mapping:

- `!is_active`: `Not Paid`
- `is_active && !is_enabled`: `Disabled`
- `is_active && is_enabled`: `Running`
- Expired when `timestamp_stop < serverTime`.

## Manage Instance

Lifecycle action endpoint:

```bash
curl -sS -X PUT "$API/instance" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instance_id":123,"action":"disable"}'
```

Valid public actions: `enable`, `disable`, `reset`, `destroy`.

Action behavior:

- `enable`: enables a paid, unexpired instance deployment.
- `disable`: clears the admin user and disables the deployment.
- `reset`: rotates `installtoken` and resets the superuser.
- `destroy`: deletes the instance record, drops the instance database if possible, and destroys the deployment.

Rules:

- Only the owner can mutate an instance.
- Expired instances cannot be enabled, disabled, or reset; only `destroy` is allowed.
- `destroy` is destructive. Ask for explicit confirmation immediately before calling it.
- Do not attempt to call internal deploy behavior through the public action endpoint; public launch happens through payment processing.

Unsubscribe:

```bash
curl -sS -X PUT "$API/instance/unsubscribe" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instance_id":123,"subscription_request_id":"SUBSCRIPTION_REQUEST_ID"}'
```

Only unsubscribe a subscription belonging to that instance and user. If the request succeeds, the API ends the local subscription record.

Logout:

```bash
curl -sS -X POST "$API/logout"
```

For browser-style use, clear local session state after logout.

## Error Handling

Handle these API responses directly:

- `401` on login: invalid credentials or inactive user.
- `401` on authenticated reads: missing/expired token; re-login.
- `400 Invalid instance type`: re-fetch `/instance/types`.
- `400 Invalid payment plan interval/tier`: re-fetch `/pricing`.
- `400 Custom domains/subdomains are not allowed`: choose a tier that supports the requested domain mode or ask the user to change domain.
- `400 Custom domain is already in use`: ask for a different domain.
- `400 Not your instance`: stop; do not retry with guessed ids.
- `404 Instance does not exist`: re-list instances and ask if the user selected the wrong instance.
- `400 Invalid payment plan`: the selected tier/interval cannot be bought/subscribed through that endpoint; re-check interval and use the correct payment flow.

Frontend error mapping accepts plain string errors, `detail` strings, or validation arrays in `detail[].msg`; surface those messages directly to the user.

When in doubt, stop and ask a precise question with the smallest missing fact needed to continue.
