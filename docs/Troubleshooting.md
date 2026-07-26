# Troubleshooting

## HTTP 403 or “access is not approved”

Completing the browser OAuth flow does not immediately grant access to account
data. Open the Monzo mobile app and approve the connection. Then retry the
request.

If approval is already complete, confirm that the token belongs to the expected
client and account.

## `MonzoReauthenticationRequired`

The token store returned no token, the access token expired without a refresh
token, or the current refresh path is no longer usable.

Start a new authorization-code flow. Non-confidential Monzo clients do not
receive refresh tokens.

## `invalid_grant` during refresh

Common causes include:

- another process already used the one-time refresh token;
- the durable store did not atomically save the replacement refresh token;
- another authorization created a new active token for the same client and
  user;
- the user logged out or revoked access;
- the client ID or secret is incorrect.

Use a shared `refresh_lock_factory` for multi-process deployments and verify
that every worker reloads from the same durable token store after acquiring the
lock.

## OAuth callback state failure

Confirm that:

- the state saved before redirect is loaded for the same signed-in application
  user;
- the callback passes Monzo's returned state unchanged;
- session cookies survive the redirect;
- the state has not expired or already been consumed;
- multiple concurrent sign-in attempts are not overwriting one state value.

Never bypass state validation to make the callback succeed.

## Redirect URI mismatch

The redirect URI in `OAuthClientConfig` must match the URI registered in
[Monzo developer tools](https://developers.monzo.com/). Compare the scheme,
host, port, path, and trailing slash.

The same URI is used in both the authorization request and authorization-code
exchange.

## Only recent transactions are returned

Monzo's strong-customer-authentication rules allow full transaction-history
access only briefly after authorization. After that initial window, the
Developer API generally allows synchronization of the most recent 90 days.

If a personal application needs older history, fetch it immediately after
authorization and store only what the application genuinely needs, with
appropriate encryption and retention controls.

See [Monzo's transaction documentation](https://docs.monzo.com/#list-transactions).

## An older token suddenly returns HTTP 401

Monzo permits one active access token per client and user. Creating another
access token can invalidate the previous one. Check whether the API Playground,
another container, or a second authorization flow issued a new token.

## Rate limiting

Catch `MonzoRateLimitError` and inspect `retry_after`. The built-in retry policy
will only wait within its configured per-delay and total elapsed bounds.

Do not add unbounded retries. Reduce request frequency, cache non-sensitive
derived results where appropriate, and paginate deliberately.

## Timeout or transport errors

The default client uses bounded timeouts. Check Monzo service availability,
local DNS, egress rules, proxies, and TLS interception before increasing those
bounds.

When injecting `httpx.AsyncClient`, verify its timeout, connection-pool, proxy,
and redirect configuration.

## Response validation errors

`MonzoResponseDecodeError` means a successful response was not valid JSON.
`MonzoResponseValidationError` means the JSON did not satisfy required fields.

Record the exception class, model name, status, and Monzo request ID where
available. Do not log the full response body because it may contain financial
data.

Check the installed `aiomonzo` version and open a private security report or
minimal sanitized issue if Monzo changed its response contract.

## Naive clock error

An injected `clock` must return a timezone-aware `datetime`. Production code
normally omits `clock`; it exists primarily for deterministic tests.
