# aiomonzo documentation

`aiomonzo` is a typed, fully asynchronous Python client for the Monzo Developer
API.

> [!IMPORTANT]
> `aiomonzo` is an unofficial community project and is not developed,
> maintained, supported, approved, or endorsed by Monzo Bank.
>
> Monzo states that its Developer API is not suitable for public applications.
> It may be used with your own account or a small set of users you explicitly
> allow. See the [official API introduction](https://docs.monzo.com/).

## Guides

- [Getting started](Getting-Started.md)
- [OAuth setup](OAuth-Setup.md)
- [Token storage and refresh coordination](Token-Storage.md)
- [API reference](API-Reference.md)
- [Errors and retries](Errors-and-Retries.md)
- [Security](Security.md)
- [Troubleshooting](Troubleshooting.md)
- [Development and releases](Development.md)

## Choosing an authentication mode

| Use case | Recommended mode |
| --- | --- |
| Short-lived personal experiment | API Playground token |
| Long-running personal server or container | Confidential OAuth client with a durable `TokenStore` |
| Multi-process service sharing one token record | OAuth plus a distributed `refresh_lock_factory` |
| Existing credential broker or gateway | Custom `AccessTokenProvider` |

## Supported Python versions

Python 3.12, 3.13, and 3.14 are tested in CI.

## Official Monzo resources

- [Developer tools and API Playground](https://developers.monzo.com/)
- [Developer API reference](https://docs.monzo.com/)
- [Authentication](https://docs.monzo.com/#authentication)
- [Pagination](https://docs.monzo.com/#pagination)
- [Webhooks](https://docs.monzo.com/#webhooks)
- [Open Banking API](https://docs.monzo.com/open-banking/)

The Open Banking API is a separate product for appropriately authorised
providers. `aiomonzo` implements the personal-use Developer API at
`https://api.monzo.com`.
