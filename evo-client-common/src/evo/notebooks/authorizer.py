import contextlib
import json
import warnings
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from pydantic import ValidationError

from evo import logging, oauth
from evo.common import pydantic_utils
from evo.oauth.authorizer import _BaseAuthorizer

from .env import DotEnv

__all__ = [
    "AuthorizationCodeAuthorizer",
]

logger = logging.getLogger("notebooks.oauth")

_TOKEN_KEY = "NotebookOAuth.token"

_T_token = TypeVar("_T_token", bound=oauth.AccessToken)


class _OAuthEnv(Generic[_T_token]):
    def __init__(self, env: DotEnv) -> None:
        self.__dotenv = env

    def get_token(self) -> _T_token | None:
        token_str = self.__dotenv.get(_TOKEN_KEY)
        if token_str is None:
            return None

        try:
            token_dict = json.loads(token_str)
            try:
                # Attempt to parse the token as a UserAccessToken first.
                return pydantic_utils.validate_model(token_dict, oauth.UserAccessToken)
            except ValidationError:
                # Fall back to AccessToken.
                return pydantic_utils.validate_model(token_dict, oauth.AccessToken)

        except Exception:
            # The token is invalid.
            raise ValueError(f"Invalid token found in the environment file {_TOKEN_KEY}: {token_str!r}")

    def set_token(self, token: _T_token | None) -> None:
        if token is None:
            new_value = None
        else:
            new_value = pydantic_utils.export_json(token)
        self.__dotenv.set(_TOKEN_KEY, new_value)


class _NotebookAuthorizerMixin(_BaseAuthorizer[_T_token]):
    _env: _OAuthEnv[_T_token]

    async def reuse_token(self) -> bool:
        """Attempt to reuse an existing token from the environment file.

        :returns: True if a token was found and reused, False otherwise.
        """
        async with self._mutex:
            if (token := self._env.get_token()) is not None:
                self._update_token(token)
                return True
            return False

    def _get_token(self) -> _T_token | None:
        return self._env.get_token()

    def _update_token(self, new_token: _T_token) -> None:
        super()._update_token(new_token)
        self._env.set_token(new_token)


class AuthorizationCodeAuthorizer(_NotebookAuthorizerMixin[oauth.UserAccessToken], oauth.AuthorizationCodeAuthorizer):
    """An authorization code authorizer for use in Jupyter notebooks.

    This authorizer is not secure, and should only ever be used in jupyter notebooks. It stores the access token in the
    environment file, which is not secure. It is intended for use in a development environment only. The environment
    file must not be committed to source control.
    """

    def __init__(
        self,
        oidc_connector: oauth.OIDCConnector,
        redirect_url: str,
        scopes: oauth.OAuthScopes,
        env: DotEnv,
    ) -> None:
        """
        :param oidc_connector: The OIDC connector to use for authentication.
        :param redirect_url: The local URL to redirect the user back to after authorisation.
        :param scopes: The OAuth scopes to request.
        :param env: The environment to store the OAuth token in.
        """
        warnings.warn(
            "The evo.notebooks.AuthorizationCodeAuthorizer is not secure, and should only ever be used in jupyter"
            "notebooks in a private environment."
        )
        super().__init__(oidc_connector=oidc_connector, redirect_url=redirect_url, scopes=scopes)
        self._env = _OAuthEnv(env)

    @contextlib.asynccontextmanager
    async def _unwrap_token(self) -> AsyncIterator[oauth.UserAccessToken]:
        # Overrides the parent implementation so that we can automatically login at startup.
        async with self._mutex:
            if (token := self._env.get_token()) is None:
                token = await self._handle_login(
                    scopes=oauth.OAuthScopes.all_evo | oauth.OAuthScopes.offline_access,
                    timeout_seconds=60,
                )
                self._update_token(token)
            yield token

    async def refresh_token(self) -> bool:
        succeeded = await oauth.AuthorizationCodeAuthorizer.refresh_token(self)
        if not succeeded:
            # The refresh token has expired. Clear the token from the environment.
            self._env.set_token(None)
        return succeeded


class DeviceFlowAuthorizer(_NotebookAuthorizerMixin[oauth.AccessToken], oauth.DeviceFlowAuthorizer):
    """A device flow authorizer for use in Jupyter notebooks.

    This authorizer is not secure, and should only ever be used in jupyter notebooks. It stores the access token in the
    environment file, which is not secure. It is intended for use in a development environment only. The environment
    file must not be committed to source control.
    """

    def __init__(
        self,
        oidc_connector: oauth.OIDCConnector,
        scopes: oauth.OAuthScopes,
        env: DotEnv,
    ) -> None:
        """
        :param oidc_connector: The OIDC connector to use for authentication.
        :param scopes: The OAuth scopes to request.
        :param env: The environment to store the OAuth token in.
        """
        warnings.warn(
            "The evo.notebooks.DeviceFlowAuthorizer is not secure, and should only ever be used in jupyter"
            "notebooks in a private environment."
        )
        super().__init__(oidc_connector=oidc_connector, scopes=scopes)
        self._env = _OAuthEnv(env)

    async def refresh_token(self) -> bool:
        # The access token has expired. Clear the token from the environment.
        self._env.set_token(None)
        # We are unable to refresh the access token because refresh tokens are not supported for device flow.
        return False
