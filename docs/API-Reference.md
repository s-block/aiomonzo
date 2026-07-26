# API reference

This page documents the public `aiomonzo` API. Monzo remains the authority for
provider behavior and response semantics:
[Monzo Developer API reference](https://docs.monzo.com/).

## MonzoClient

```python
MonzoClient(
    *,
    access_token=None,
    access_token_provider=None,
    oauth=None,
    token_store=None,
    http_client=None,
    api_base_url="https://api.monzo.com",
    timeout=None,
    limits=None,
    retry_policy=None,
    refresh_skew=timedelta(seconds=30),
    refresh_lock_factory=None,
    clock=None,
)
```

### Authentication parameters

| Parameter | Purpose |
| --- | --- |
| `access_token` | Static string, `SecretStr`, or `OAuthToken` |
| `access_token_provider` | Application-owned request-time token provider |
| `oauth` | `OAuthClientConfig` for code exchange and refresh |
| `token_store` | Application-owned `TokenStore` |
| `refresh_skew` | Refresh window before token expiry |
| `refresh_lock_factory` | Optional shared async lock for cross-process refresh |

Pass one token source. A custom `AccessTokenProvider` cannot be combined with
the built-in OAuth manager.

### HTTP parameters

| Parameter | Purpose |
| --- | --- |
| `http_client` | Injected `httpx.AsyncClient`; the caller retains ownership |
| `api_base_url` | API origin; defaults to Monzo production |
| `timeout` | HTTPX timeout used only for an internally-created client |
| `limits` | HTTPX pool limits used only for an internally-created client |
| `retry_policy` | Bounded `RetryPolicy` for safe replays |
| `clock` | Aware-datetime source, primarily for deterministic testing |

The internal HTTP client defaults to 5-second connect and pool timeouts and
10-second read and write timeouts.

## OAuth methods

| Method | Result | Notes |
| --- | --- | --- |
| `create_authorization_request(state=None)` | `AuthorizationRequest` | Creates the Monzo URL and CSRF state |
| `exchange_authorization_code(code, expected_state=..., returned_state=...)` | `OAuthToken` | Validates state, exchanges code, saves token |
| `refresh_access_token()` | `OAuthToken` | Explicitly rotates the current token set |
| `logout()` | `None` | Invalidates access and clears the token store |

These methods require the built-in OAuth manager. They are unavailable when a
custom `AccessTokenProvider` is supplied.

## Accounts and balances

| Method | Result | Monzo endpoint |
| --- | --- | --- |
| `who_am_i()` | `WhoAmI` | `GET /ping/whoami` |
| `list_accounts(account_type=None)` | `list[Account]` | `GET /accounts` |
| `get_balance(account_id)` | `Balance` | `GET /balance` |
| `list_pots(account_id)` | `list[Pot]` | `GET /pots` |

`account_type` can be used for provider-supported account filtering. Account
and pot behavior can change as Monzo adds account products.

## Pot transfers

```python
await client.deposit_into_pot(
    pot_id,
    source_account_id=account_id,
    amount=2500,
    dedupe_id="stable-operation-id",
)

await client.withdraw_from_pot(
    pot_id,
    destination_account_id=account_id,
    amount=2500,
    dedupe_id="another-stable-operation-id",
)
```

Amounts are positive integer minor units. The dedupe ID must be stable for the
same logical transfer. Pot transfer requests are replayable because Monzo
defines that deduplication contract.

## Transactions

| Method | Result |
| --- | --- |
| `get_transaction(transaction_id, expand=())` | `Transaction` |
| `list_transactions(account_id, since=None, before=None, limit=30, expand=())` | `list[Transaction]` |
| `annotate_transaction(transaction_id, metadata)` | `Transaction` |

`expand=("merchant",)` requests expanded merchant data. Without expansion,
`Transaction.merchant` may contain a merchant ID rather than a `Merchant`.

`since` accepts an aware datetime or a Monzo object ID cursor. `before` accepts
an aware datetime. `limit` must be between 1 and 100.

`list_transactions` returns one page and does not silently fetch an unbounded
history. See [Monzo pagination](https://docs.monzo.com/#pagination).

Annotation values must be strings or `None`. `None` removes that metadata key.
Annotation requests are not automatically retried because replay safety is not
guaranteed.

## Webhooks

| Method | Result |
| --- | --- |
| `register_webhook(account_id, url)` | `Webhook` |
| `list_webhooks(account_id)` | `list[Webhook]` |
| `delete_webhook(webhook_id)` | `None` |

Use an HTTPS callback under your control. Monzo sends transaction data to the
registered URL and retries failed deliveries. Authenticate or otherwise verify
the events according to your application's threat model, minimize logged
payload data, and make handlers idempotent.

See [Monzo webhooks](https://docs.monzo.com/#webhooks).

## Public models

- `OAuthClientConfig`, `AuthorizationRequest`, `OAuthToken`
- `WhoAmI`
- `Account`, `AccountOwner`, `Balance`, `Pot`
- `Transaction`, `TransactionCounterparty`, `Merchant`, `MerchantAddress`
- `Webhook`
- `RetryPolicy`

Models are strict, immutable Pydantic models. Known fields are validated while
unknown provider additions are preserved for forward compatibility.

Financial amounts are integer minor units. Timestamps are timezone-aware.
An unsettled transaction's empty `settled` value is normalized to `None`.

## Public protocols

- `TokenStore`
- `AccessTokenProvider`
- `RefreshLockFactory`

See [token storage](Token-Storage.md) for their responsibilities.
