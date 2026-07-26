# aiomonzo

> [!IMPORTANT]
> **Personal-use, unofficial package.** `aiomonzo` is an independent community
> project. It is not developed, maintained, supported, approved, or endorsed by
> Monzo Bank.
>
> Monzo states that its Developer API is not suitable for public applications
> and may be used only with your own account or a small set of users you
> explicitly allow. This package is therefore intended for personal projects and
> small private integrations, not public customer-facing banking applications.
> See the [Monzo Developer API introduction](https://docs.monzo.com/).

`aiomonzo` is an unofficial, fully asynchronous and typed Python client for the
[Monzo Developer API](https://docs.monzo.com/). It provides API, OAuth, retry,
validation, and resource-lifecycle primitives while leaving credential storage,
tenancy, user interfaces, and deployment policy to the application using it.

The package supports Python 3.12, 3.13, and 3.14.

## Features

- Fully asynchronous API and OAuth operations using `httpx`.
- Strict, frozen Pydantic models that preserve new provider fields.
- Static tokens, caller-owned OAuth token storage, and custom token providers.
- Automatic refresh with rotated refresh-token replacement.
- Optional distributed refresh locking for multi-process deployments.
- Bounded timeouts and retries that respect mutation idempotency.
- Typed, secret-safe exceptions that do not retain provider response bodies.
- Explicit async resource ownership and a `py.typed` marker.

## Installation

```bash
python -m pip install aiomonzo
```

With `uv`:

```bash
uv add aiomonzo
```

## Documentation

| Guide | Contents |
| --- | --- |
| [Getting started](docs/Getting-Started.md) | Installation, API Playground tokens, and first requests |
| [OAuth setup](docs/OAuth-Setup.md) | Creating a Monzo client and completing authorization |
| [Token storage](docs/Token-Storage.md) | Durable storage, refresh rotation, and multi-process locking |
| [API reference](docs/API-Reference.md) | Constructor options, methods, models, and pagination |
| [Errors and retries](docs/Errors-and-Retries.md) | Exception hierarchy, retry behavior, and recovery |
| [Security](docs/Security.md) | Credential, state, transport, webhook, and logging guidance |
| [Troubleshooting](docs/Troubleshooting.md) | Common Monzo authorization and API failures |
| [Development](docs/Development.md) | Local setup, validation, packaging, and release workflow |

The same guides are published in the
[GitHub Wiki](https://github.com/s-block/aiomonzo/wiki).

## Static access token

A static token is useful for short-lived development and API Playground
experiments. Generate one in the
[Monzo developer tools](https://developers.monzo.com/), approve access in the
Monzo mobile app when prompted, and avoid hard-coding or committing it.

```python
import asyncio
import os

from aiomonzo import MonzoClient


async def main() -> None:
    async with MonzoClient(
        access_token=os.environ["MONZO_ACCESS_TOKEN"],
    ) as monzo:
        identity = await monzo.who_am_i()
        accounts = await monzo.list_accounts()
        print(identity.user_id, [account.id for account in accounts])


asyncio.run(main())
```

For long-lived access, follow the [OAuth setup guide](docs/OAuth-Setup.md).

## OAuth with caller-owned storage

Applications using Monzo OAuth supply an `OAuthClientConfig` and a `TokenStore`.
The store controls encryption, tenant isolation, persistence, and atomic token
replacement. `aiomonzo` never creates durable token storage.

```python
from aiomonzo import MonzoClient, OAuthClientConfig, OAuthToken, TokenStore


class ApplicationTokenStore(TokenStore):
    async def load(self) -> OAuthToken | None:
        ...  # Load and decrypt for the current application user.

    async def save(self, token: OAuthToken) -> None:
        ...  # Atomically replace access and rotated refresh tokens.

    async def clear(self) -> None:
        ...  # Remove the current user's token set.


oauth = OAuthClientConfig(
    client_id="monzo-client-id",
    client_secret=load_monzo_client_secret(),
    redirect_uri="https://app.example.com/oauth/monzo/callback",
)
client = MonzoClient(oauth=oauth, token_store=ApplicationTokenStore())

authorization = client.create_authorization_request()
# Store authorization.state in a user-bound, short-lived session before
# redirecting the browser to authorization.url.
```

At the callback, pass the code and both state values to
`exchange_authorization_code`. State comparison is constant-time. When a token
expires or Monzo rejects it, refresh is serialized within the provider and the
complete replacement token set is passed to `TokenStore.save`.

Monzo can rotate refresh tokens. A durable `save` implementation must replace
the complete token set atomically; saving only the access token can make the
next refresh impossible.

### Multi-process refresh coordination

By default, `aiomonzo` serializes refreshes within one process. If multiple
processes or hosts share the same durable token record, pass a
`refresh_lock_factory` backed by a distributed lock, such as a database
advisory lock or Redis lock. The lock must be scoped to the same user and OAuth
client as the token record and remain held while the token is reloaded,
refreshed, and atomically replaced.

The factory returns an async context manager:

```python
from contextlib import AbstractAsyncContextManager

from aiomonzo import MonzoClient


def refresh_lock_factory() -> AbstractAsyncContextManager[None]:
    return application_locks.monzo_oauth(user_id)


client = MonzoClient(
    oauth=oauth,
    token_store=ApplicationTokenStore(),
    refresh_lock_factory=refresh_lock_factory,
)
```

All processes sharing that token record must use the same lock key. A
single-process application can omit this option.

## Custom access-token providers

For multi-user applications, gateways, or private credential brokers, implement
the narrow `AccessTokenProvider` protocol:

```python
from aiomonzo import AccessTokenProvider, MonzoClient


class BrokerAccessTokenProvider(AccessTokenProvider):
    async def get_access_token(self) -> str:
        return await obtain_short_lived_token()

    async def refresh_after_rejection(self, rejected_access_token: str) -> str:
        return await replace_rejected_token(rejected_access_token)


client = MonzoClient(access_token_provider=BrokerAccessTokenProvider())
```

The provider owns storage and refresh policy. `MonzoClient` requests a token
only when sending a Monzo API request and never exposes it through model data.

## Supported operations

`MonzoClient` currently provides:

- `who_am_i`
- `list_accounts`
- `get_balance`
- `list_pots`
- `deposit_into_pot`
- `withdraw_from_pot`
- `get_transaction`
- `list_transactions`
- `annotate_transaction`
- `register_webhook`
- `list_webhooks`
- `delete_webhook`
- `create_authorization_request`
- `exchange_authorization_code`
- `refresh_access_token`
- `logout`

Amounts use Monzo's integer minor units. Transaction listing returns one bounded
page and accepts `since`, `before`, `limit`, and merchant expansion controls;
the caller owns pagination policy.

## HTTP client ownership

By default, `MonzoClient` owns one pooled `httpx.AsyncClient`. Close it with an
async context manager or `await client.aclose()`. If an application injects an
existing `httpx.AsyncClient`, the application retains ownership and must close
it.

Default connection limits, timeouts, redirects, and retries are bounded.
Read-only requests can be retried for transient failures. Mutating requests are
not replayed unless the operation has an idempotency contract.

## Errors

Failures derive from `MonzoClientError`, with typed subclasses for
configuration, request validation, authentication, permission, rate limiting,
timeouts, transport, provider response decoding, provider response validation,
and token-store failures.

Exceptions deliberately avoid access tokens, OAuth secrets, provider bodies,
and credential-bearing URLs. Applications should still avoid logging arbitrary
financial model data.

## Development

```bash
uv sync --dev --frozen
make check
uv run pre-commit run --all-files
```

`make check` runs Ruff, strict mypy, the full test suite, distribution metadata
checks, artifact-content checks, and a clean installation smoke test.

## Security

Do not report vulnerabilities with real Monzo credentials or financial data.
Use [GitHub private vulnerability reporting](https://github.com/s-block/aiomonzo/security/advisories/new)
when available.

Read the [security guide](docs/Security.md) before deploying OAuth token storage
or using the client in a multi-process service.

## Official Monzo resources

- [Monzo Developer tools](https://developers.monzo.com/)
- [Monzo Developer API reference](https://docs.monzo.com/)
- [Monzo authentication documentation](https://docs.monzo.com/#authentication)
- [Monzo Open Banking documentation](https://docs.monzo.com/open-banking/)

## License

MIT. This project is not affiliated with or endorsed by Monzo Bank.
