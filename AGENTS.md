# aiomonzo Project Guide

Keep this asynchronous banking client typed, minimal, reusable, and
secret-safe.

## Architecture

- `src/aiomonzo/client.py` owns the public `MonzoClient`.
- `src/aiomonzo/auth.py` owns token-provider and caller-owned token-store
  contracts plus Monzo OAuth refresh coordination.
- `src/aiomonzo/transport.py` owns bounded asynchronous HTTP behavior.
- `src/aiomonzo/models.py` validates provider responses and public values.
- `src/aiomonzo/exceptions.py` maps failures to typed, secret-safe exceptions.
- Mirror these boundaries under `tests/`.

This is a client library. Do not add an MCP server, web application, token
database, command-line login flow, Docker image, or provider credential store.

## Public And Security Contracts

- Treat exports in `aiomonzo.__all__` as the supported public API.
- Never log or include OAuth secrets, access tokens, refresh tokens,
  authorization codes, or response bodies in exceptions.
- `TokenStore` implementations belong to callers. Refresh-token replacement
  must be atomic in durable implementations.
- `AccessTokenProvider` permits storage, tenancy, and broker policy to remain
  outside this package.
- Keep OAuth state validation constant-time. Serialize refreshes within one
  provider by default and through the injected refresh-lock factory when token
  state is shared across processes or hosts.
- Retry mutations only when replay is demonstrably safe.

## Python And Packaging

- Support Python 3.12 through 3.14.
- Keep network paths asynchronous, bounded, cancellation-safe, and fully typed.
- Preserve ownership rules for injected versus internally-created HTTP clients.
- Use `uv`, Hatchling, Ruff, strict mypy, pytest, and committed public-PyPI
  locks.
- Pin GitHub Actions to full commit SHAs.
- Publish only through the protected OIDC workflow; never add a PyPI token.

## Validation

```bash
uv sync --dev --frozen
make check
uv run pre-commit run --all-files
```

`make check` validates formatting, linting, typing, tests, wheel/sdist metadata,
artifact contents, and an isolated installation of the built wheel.
