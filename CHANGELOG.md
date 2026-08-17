# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Improved the README quick start and project positioning, and added package and
  repository discovery metadata.

## [0.1.0] - 2026-07-26

### Added

- Fully asynchronous, typed access to Monzo accounts, balances, pots,
  transactions, annotations, and webhooks.
- Static bearer, caller-owned OAuth token-store, and custom access-token
  provider modes.
- Caller-injected refresh locks for safely coordinating rotating OAuth tokens
  across processes or hosts.
- Comprehensive package documentation and a synchronized GitHub Wiki, including
  Monzo OAuth client setup, token storage, security, and troubleshooting guides.
- Bounded retry, timeout, validation, resource-lifecycle, and secret-safe error
  behavior.
- Python 3.12, 3.13, and 3.14 support with a `py.typed` marker.

[Unreleased]: https://github.com/s-block/aiomonzo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/s-block/aiomonzo/releases/tag/v0.1.0
