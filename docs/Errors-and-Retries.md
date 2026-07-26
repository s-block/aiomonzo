# Errors and retries

All package exceptions derive from `MonzoClientError`.

## Exception hierarchy

| Exception | Meaning |
| --- | --- |
| `MonzoConfigurationError` | Missing, conflicting, or invalid client configuration |
| `MonzoRequestValidationError` | Invalid public method argument |
| `MonzoClosedError` | Request attempted after the client was closed |
| `MonzoTokenStoreError` | Injected token store failed |
| `MonzoTransportError` | Network request failed before a response |
| `MonzoTimeoutError` | Connect, read, write, or pool timeout |
| `MonzoResponseDecodeError` | Successful response was not valid JSON |
| `MonzoResponseValidationError` | Successful response did not match its model |
| `MonzoHTTPError` | Monzo returned an unsuccessful HTTP response |
| `MonzoAuthenticationError` | Access token, client, or OAuth grant rejected |
| `MonzoReauthenticationRequired` | No usable token or refresh path remains |
| `MonzoPermissionError` | Authenticated but not approved or permitted |
| `MonzoRateLimitError` | Monzo returned HTTP 429 |

`MonzoHTTPError` provides `status_code`, `message`, `code`, `oauth_error`, and
`request_id` where Monzo supplies them. `MonzoRateLimitError` also exposes
`retry_after`.

Exceptions deliberately do not retain raw response bodies, access tokens,
refresh tokens, authorization codes, or client secrets.

## Catching errors

```python
from aiomonzo import (
    MonzoPermissionError,
    MonzoRateLimitError,
    MonzoReauthenticationRequired,
)

try:
    transactions = await client.list_transactions(account_id)
except MonzoPermissionError:
    # Ask the account owner to approve the connection in the Monzo app.
    raise
except MonzoReauthenticationRequired:
    # Restart the authorization-code flow.
    raise
except MonzoRateLimitError as error:
    # Schedule bounded retry according to application policy.
    print(error.retry_after)
```

Do not return provider exception text directly to untrusted clients without
considering information disclosure and user experience.

## Default retry policy

```python
RetryPolicy(
    max_attempts=3,
    base_delay_seconds=0.25,
    max_delay_seconds=5.0,
    max_elapsed_seconds=10.0,
    jitter_ratio=0.2,
)
```

Retryable statuses are 408, 429, 500, 502, 503, and 504. Network failures and
timeouts can also be retried when the operation is safe to replay.

The client respects a valid `Retry-After` value only when it remains inside the
configured delay and total elapsed-time bounds.

## Replay safety

Read-only requests are retryable. Mutations are not retried unless their
contract makes replay safe:

- Pot deposits and withdrawals are retryable because the caller supplies a
  stable Monzo dedupe ID.
- Webhook deletion is retryable because repeated deletion is treated as safe by
  the client contract.
- Transaction annotations, webhook registration, OAuth code exchange, logout,
  and explicit refresh are not automatically retried.

An `invalid_token` response can trigger one token refresh and one replay. The
client will not enter an infinite refresh loop if the replacement is also
rejected.

## Cancellation

Async task cancellation propagates immediately and is not converted into a
transport error or retried.
