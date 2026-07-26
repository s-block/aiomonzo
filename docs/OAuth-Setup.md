# OAuth setup

`aiomonzo` implements Monzo's OAuth 2 authorization-code flow for confidential,
server-side applications. Your application owns the redirect route, browser
session, client-secret storage, and token persistence.

## Before you start

Read Monzo's current:

- [Developer API introduction](https://docs.monzo.com/)
- [Authentication guide](https://docs.monzo.com/#authentication)
- [Client confidentiality guidance](https://docs.monzo.com/#client-confidentiality)
- [Developer tools](https://developers.monzo.com/)

The Developer API is for personal use or a small explicitly allowed group. A
public customer-facing banking service should investigate
[Monzo Open Banking](https://docs.monzo.com/open-banking/) and its regulatory
requirements instead.

## 1. Create a Monzo OAuth client

1. Sign in to the [Monzo developer tools](https://developers.monzo.com/).
2. Create a new OAuth client.
3. Give the client a name that lets you recognize the application.
4. Register the exact callback URI handled by your application, for example
   `https://personal.example.com/oauth/monzo/callback`.
5. Choose a confidential client for a server, private service, or container
   that can keep a client secret. Monzo does not issue refresh tokens to
   non-confidential clients.
6. Save the client ID and client secret in a secret manager or encrypted
   configuration store.

The callback URI used by the application must match the URI registered with
Monzo, including scheme, host, port, path, and trailing slash behavior. Use
HTTPS outside a loopback-only development environment.

The developer-tools interface can change. Treat the values shown by Monzo as
the source of truth and never copy credentials into source control or support
messages.

## 2. Configure `aiomonzo`

```python
from aiomonzo import MonzoClient, OAuthClientConfig


oauth = OAuthClientConfig(
    client_id=load_monzo_client_id(),
    client_secret=load_monzo_client_secret(),
    redirect_uri="https://personal.example.com/oauth/monzo/callback",
)

client = MonzoClient(
    oauth=oauth,
    token_store=ApplicationTokenStore(),
)
```

`ApplicationTokenStore` is an application-owned implementation of the
`TokenStore` protocol. See [token storage](Token-Storage.md).

## 3. Start authorization

```python
authorization = client.create_authorization_request()
```

Persist `authorization.state` in a short-lived, user-bound server-side session,
then redirect the user's browser to `authorization.url`.

The default state value is generated with a cryptographically secure random
source. If you provide your own state value, it must be unpredictable and
single-use.

## 4. Handle the callback

Monzo redirects to your registered URI with `code` and `state` query
parameters. Pass both the stored state and returned state to the client:

```python
token = await client.exchange_authorization_code(
    code,
    expected_state=session.monzo_oauth_state,
    returned_state=request.query_params["state"],
)
```

The client compares state values in constant time and aborts before sending the
authorization code if they do not match.

Delete the stored state after the callback succeeds or fails. Do not log the
authorization code.

## 5. Approve access in the Monzo app

Monzo does not grant data access immediately after the browser flow. The account
owner must approve the connection in the Monzo mobile app. Until approval,
otherwise valid requests can return HTTP 403.

Use `await client.who_am_i()` to verify the token, then call a data endpoint
after mobile approval.

## Token lifecycle

- Access tokens expire after a number of hours.
- Confidential clients can receive refresh tokens.
- Monzo refresh tokens are one-time credentials: refreshing invalidates the
  previous access token and returns a replacement token set.
- Monzo permits one active access token per client and user. Acquiring another
  token can invalidate the previous token.
- `aiomonzo` refreshes shortly before expiry and once after an
  `invalid_token` response.
- `TokenStore.save` receives the complete replacement token set and must replace
  it atomically.

Use a distributed refresh lock when multiple processes or hosts share a token
record. See [multi-process coordination](Token-Storage.md#multi-process-and-multi-host-coordination).

## Explicit refresh and logout

```python
replacement = await client.refresh_access_token()
await client.logout()
```

`logout()` invalidates the current Monzo access token and then clears the
configured token store. The user must authorize again after logout.

## Non-confidential clients

Monzo's documentation says non-confidential clients do not receive refresh
tokens. `OAuthClientConfig` is designed for a confidential client with a secret.
For a client-side application that cannot protect a secret, do not embed a Monzo
client secret in distributed code. Handle reauthorization in an architecture
appropriate to that application.
