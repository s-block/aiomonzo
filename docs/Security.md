# Security

This guide describes the security boundary of `aiomonzo`. Applications remain
responsible for authentication to their own service, authorization, tenant
isolation, credential storage, logging, deployment, and webhook handling.

## Project and API scope

`aiomonzo` is unofficial and is not affiliated with or endorsed by Monzo Bank.
Monzo states that the Developer API is not suitable for public applications and
is limited to your own account or a small explicitly allowed group.

Use the [Monzo Open Banking API](https://docs.monzo.com/open-banking/) and obtain
the necessary authorization if building a regulated public product.

## Credential handling

- Keep the Monzo client secret in a server-side secret manager.
- Never ship a confidential client secret in browser, mobile, desktop, or other
  distributed client code.
- Encrypt access and refresh tokens at rest.
- Restrict token records to the authenticated application user.
- Do not log tokens, authorization codes, full provider responses, or financial
  models.
- Do not place credentials in URLs, screenshots, test fixtures, issue reports,
  or Git history.
- Rotate a client secret immediately if exposure is suspected.

Pydantic `SecretStr` reduces accidental representation but does not replace
encryption, access control, or safe logging.

## OAuth state

`create_authorization_request()` generates an unpredictable state value unless
the caller supplies one. Store it in a short-lived, server-side session bound to
the user who started the flow.

Always call `exchange_authorization_code()` with both the expected and returned
state. Delete state after use. Reject missing, mismatched, replayed, or expired
callbacks.

## Refresh tokens

Monzo refresh tokens rotate and are single-use. Durable stores must atomically
replace the complete `OAuthToken`. Multiple processes sharing a record must use
one distributed lock key through `refresh_lock_factory`.

See [token storage](Token-Storage.md).

## Transport

The default API base URL is `https://api.monzo.com`, and the authorization URL
is fixed to Monzo's HTTPS origin.

Only override `api_base_url` for a trusted test server or explicitly controlled
proxy. A custom origin receives bearer tokens and, when using built-in OAuth,
client and refresh credentials at its token endpoint.

The internally-created HTTP client uses bounded timeouts, connection limits,
and redirects disabled by HTTPX's default behavior. Review equivalent settings
when injecting your own client.

## Webhooks

Register HTTPS webhook URLs under your control. Monzo webhook payloads contain
financial transaction data.

- Keep the handler private to its intended ingress path.
- Apply network controls and event authentication appropriate to your design.
- Treat all payload fields as untrusted input.
- Make processing idempotent because deliveries can be retried.
- Avoid recording complete payloads in access or application logs.
- Return promptly and move slow processing to a bounded background queue.

Consult [Monzo's webhook documentation](https://docs.monzo.com/#webhooks) for
the current delivery contract.

## Errors and observability

The client does not retain raw provider bodies in its exceptions. Applications
should still sanitize error messages before exposing them and should log only
the minimum request identifiers required for support.

Metrics should use endpoint names, status families, and bounded timing data—not
account IDs, transaction IDs, user IDs, tokens, or financial values.

## Dependency and release controls

The repository:

- locks development dependencies with `uv`;
- audits supported Python dependency resolutions in CI;
- runs Ruff security rules, strict mypy, tests, package checks, dependency
  review, and CodeQL;
- pins GitHub Actions to full commit SHAs;
- publishes through PyPI Trusted Publishing with narrowly scoped OIDC
  permissions;
- scans for private keys and secrets before release.

## Reporting a vulnerability

Do not include real Monzo credentials or financial data in a report. Use
[GitHub private vulnerability reporting](https://github.com/s-block/aiomonzo/security/advisories/new)
when it is available for the repository.
