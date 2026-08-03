# Token storage and refresh coordination

`aiomonzo` deliberately does not provide a token database. The application
chooses how credentials are encrypted, isolated by user, persisted, rotated,
and deleted.

## TokenStore

Implement the async `TokenStore` protocol:

```python
from aiomonzo import OAuthToken, TokenStore


class ApplicationTokenStore(TokenStore):
    async def load(self) -> OAuthToken | None: ...

    async def save(self, token: OAuthToken) -> None: ...

    async def clear(self) -> None: ...
```

The store is responsible for one logical Monzo token set. A durable
implementation should:

- encrypt access and refresh tokens at rest;
- isolate records by the authenticated application user and Monzo client;
- use authenticated encryption context tied to the record owner;
- restrict database and key-management permissions;
- atomically replace the complete token set during `save`;
- delete or make credentials unusable during `clear`;
- avoid returning stale cached tokens after another worker saves a replacement;
- never log plaintext credentials or include them in exceptions.

`OAuthToken` uses Pydantic `SecretStr`, which protects routine representation.
The store still receives the plaintext values when it encrypts or transmits
them.

## In-memory storage

If no `TokenStore` is passed, the client creates an `InMemoryTokenStore`.

This is appropriate for:

- a short-lived script;
- an API Playground token;
- a single-process personal container where reauthorization after restart is
  acceptable.

It does not survive a restart and is not shared between processes.

## Refresh rotation

Monzo refresh tokens are single-use. A successful refresh returns a new access
token and a new refresh token. `aiomonzo` refuses to overwrite the old stored
token if a refresh response omits the replacement refresh token.

Within one client instance, refreshes are serialized automatically. After
acquiring the lock, the provider reloads the token and skips refresh if another
request already replaced it.

## Multi-process and multi-host coordination

When multiple clients share one durable token record, pass the same distributed
lock through `refresh_lock_factory`:

```python
from contextlib import AbstractAsyncContextManager

from aiomonzo import MonzoClient


def refresh_lock_factory() -> AbstractAsyncContextManager[None]:
    return application_locks.monzo_oauth(
        application_user_id=current_user_id,
        monzo_client_id=oauth.client_id,
    )


client = MonzoClient(
    oauth=oauth,
    token_store=ApplicationTokenStore(),
    refresh_lock_factory=refresh_lock_factory,
)
```

The lock implementation should:

1. Use a stable key for the same application user, Monzo client, and token
   record.
2. Be shared by every process and host that can refresh that record.
3. Remain held across the reload, Monzo refresh request, and atomic save.
4. Have bounded acquisition and failure behavior appropriate to the
   application.
5. Avoid placing tokens or client secrets in the lock key.

A PostgreSQL advisory lock, transactional row lock, or Redis-backed distributed
lock can implement this contract. The package remains storage-agnostic and does
not add one of those dependencies.

## Custom AccessTokenProvider

Applications that already own token retrieval and refresh can inject the narrow
`AccessTokenProvider` protocol:

```python
from aiomonzo import AccessTokenProvider, MonzoClient


class BrokerAccessTokenProvider(AccessTokenProvider):
    async def get_access_token(self) -> str:
        return await broker.get_usable_monzo_access_token()

    async def refresh_after_rejection(self, rejected_access_token: str) -> str:
        return await broker.replace_rejected_monzo_access_token(rejected_access_token)


client = MonzoClient(
    access_token_provider=BrokerAccessTokenProvider(),
)
```

In this mode, the provider owns storage, tenant isolation, locking, refresh, and
auditing. Do not also pass `oauth` or a `TokenStore`.
