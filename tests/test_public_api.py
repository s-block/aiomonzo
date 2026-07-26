"""Tests for the supported top-level package API."""

from importlib.metadata import version

import aiomonzo

_EXPECTED_PUBLIC_API = {
    "AccessTokenProvider",
    "Account",
    "AccountOwner",
    "AuthorizationRequest",
    "Balance",
    "InMemoryTokenStore",
    "Merchant",
    "MerchantAddress",
    "MonzoAuthenticationError",
    "MonzoClient",
    "MonzoClientError",
    "MonzoClosedError",
    "MonzoConfigurationError",
    "MonzoHTTPError",
    "MonzoPermissionError",
    "MonzoRateLimitError",
    "MonzoReauthenticationRequired",
    "MonzoRequestValidationError",
    "MonzoResponseDecodeError",
    "MonzoResponseValidationError",
    "MonzoTimeoutError",
    "MonzoTokenStoreError",
    "MonzoTransportError",
    "OAuthAccessTokenProvider",
    "OAuthClientConfig",
    "OAuthToken",
    "Pot",
    "RefreshLockFactory",
    "RetryPolicy",
    "TokenStore",
    "Transaction",
    "TransactionCounterparty",
    "Webhook",
    "WhoAmI",
    "__version__",
    "validate_oauth_state",
}


def test_public_api_is_explicit_and_importable() -> None:
    assert set(aiomonzo.__all__) == _EXPECTED_PUBLIC_API
    for name in aiomonzo.__all__:
        assert getattr(aiomonzo, name) is not None
    assert aiomonzo.__version__ == version("aiomonzo")
