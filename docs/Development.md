# Development and releases

## Repository setup

```bash
git clone https://github.com/s-block/aiomonzo.git
cd aiomonzo
uv sync --dev --frozen
uv run pre-commit install
```

Python 3.12 through 3.14 are supported. `uv.lock` is committed and resolves only
from public PyPI.

## Project layout

```text
src/aiomonzo/
├── auth.py        OAuth, token-provider, token-store, and refresh-lock contracts
├── client.py      Public MonzoClient
├── exceptions.py Typed, secret-safe exceptions
├── models.py      Public and wire-response Pydantic models
└── transport.py   Bounded authenticated HTTP transport

tests/             Mirrored behavior and contract tests
docs/              Repository documentation and GitHub Wiki source
scripts/           Distribution validation
```

## Commands

```bash
make help
make format
make lint
make type-check
make test
make test-cov
make build
make check-dist
make check
```

`make check` is the complete local gate. It runs formatting checks, Ruff,
strict mypy, all tests, wheel and source-distribution builds, Twine metadata
validation, artifact-content checks, and an isolated wheel installation.

Before committing:

```bash
make check
uv run pre-commit run --all-files
```

## Design expectations

- Keep all network paths asynchronous and cancellation-safe.
- Preserve explicit ownership for injected HTTP clients.
- Keep secrets out of exceptions, logs, fixtures, and repository history.
- Add typed models and focused tests for response-contract changes.
- Retry writes only when the provider contract makes replay safe.
- Preserve unknown provider response fields for forward compatibility.
- Do not add application storage, UI, MCP, Docker, or tenant policy to this
  client library.

## Documentation and Wiki

The Markdown files in `docs/` are the source for the GitHub Wiki. When behavior
changes:

1. Update the relevant docs and README links.
2. Run the package and documentation checks.
3. Synchronize the reviewed pages to the repository Wiki.

## Releasing

The package version lives in `src/aiomonzo/_version.py`.

The intended release flow is:

1. Update the version and changelog.
2. Run `make check`.
3. Commit and push the release.
4. Create and publish a GitHub release tagged exactly `v<version>`.
5. Let `.github/workflows/publish.yml` build and publish through PyPI Trusted
   Publishing.

The GitHub `pypi` environment and matching PyPI Trusted Publisher must be
configured before the first workflow release. Do not add a long-lived PyPI API
token to repository secrets.
