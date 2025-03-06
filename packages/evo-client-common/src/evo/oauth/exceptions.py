from evo.common.exceptions import EvoClientException

__all__ = [
    "OAuthError",
    "OIDCError",
]


class OAuthError(EvoClientException):
    """Base class for OAuth errors."""


class OIDCError(OAuthError):
    """Base class for OpenID Connect errors."""
