# Getting started

This guide covers installation, a short-lived API Playground token, client
lifecycle, and the first API requests.

## Requirements

- Python 3.12, 3.13, or 3.14.
- A Monzo account.
- Access to the [Monzo developer tools](https://developers.monzo.com/).

The Monzo Developer API is intended for your own account or a small explicitly
allowed group. It is not the API for a public banking application.

## Install

```bash
python -m pip install aiomonzo
```

Or:

```bash
uv add aiomonzo
```

## Create a development token

For a quick local experiment:

1. Sign in to the [Monzo developer tools](https://developers.monzo.com/).
2. Open the API Playground.
3. Generate or reveal an access token.
4. Complete any approval requested by the Monzo mobile app.
5. Put the token in a local secret source. Do not commit it.

For example, in a temporary shell:

```bash
export MONZO_ACCESS_TOKEN='replace-with-your-playground-token'
```

Avoid placing real credentials in shell history, screenshots, bug reports,
tests, or example files. Prefer your operating system keychain or a secret
manager for anything beyond a short local experiment.

## Make the first request

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

        print(identity.user_id)
        for account in accounts:
            balance = await monzo.get_balance(account.id)
            print(account.description, balance.balance, balance.currency)


asyncio.run(main())
```

Amounts are integer minor units. For GBP, `1250` means £12.50.

## Client lifecycle

When `MonzoClient` creates its own `httpx.AsyncClient`, use an async context
manager or call `await client.aclose()`.

If you inject an existing `httpx.AsyncClient`, your application owns that HTTP
client and must close it. Closing `MonzoClient` will not close an injected
client.

## List transactions

```python
from datetime import UTC, datetime, timedelta

since = datetime.now(UTC) - timedelta(days=30)
transactions = await monzo.list_transactions(
    account.id,
    since=since,
    limit=100,
    expand=("merchant",),
)
```

`list_transactions` returns one page. The default page size is 30 and the
maximum is 100. Use the last transaction ID or an aware datetime as `since` to
request subsequent pages.

Monzo applies a strong-customer-authentication restriction to transaction
history: shortly after authorization the client can fetch the full history,
then it can generally synchronize only the most recent 90 days. See
[Monzo's transaction documentation](https://docs.monzo.com/#list-transactions).

## Next steps

- Use [OAuth setup](OAuth-Setup.md) for durable access.
- Review [token storage](Token-Storage.md) before persisting credentials.
- See the complete [API reference](API-Reference.md).
- Read the [security guide](Security.md) before deployment.
