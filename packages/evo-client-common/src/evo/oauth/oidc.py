#  Copyright © 2025 Bentley Systems, Incorporated
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import warnings
from types import TracebackType
from typing import Type, TypeVar
from urllib.parse import urlparse

from pydantic import ValidationError

from evo import logging
from evo.common import APIConnector, RequestMethod
from evo.common.exceptions import EvoAPIException
from evo.common.interfaces import ITransport

from .data import AccessToken, DeviceFlowResponse, OAuthScopes, OIDCConfig
from .exceptions import OAuthError, OIDCError

logger = logging.getLogger("oauth")

__all__ = ["OIDCConnector"]

T = TypeVar("T", bound=AccessToken)


class OIDCConnector:
    """OpenID Connect client with endpoint discovery.

    This client is used to authenticate with an OpenID Connect provider and obtain an access token.
    OAuth 2.0 endpoints are discovered using the OpenID Connect Discovery protocol.

    https://openid.net/specs/openid-connect-discovery-1_0.html
    """

    def __init__(
        self,
        transport: ITransport,
        oidc_issuer: str,
        client_id: str,
        client_secret: str | None = None,
    ) -> None:
        """
        :param transport: The transport to use for making requests.
        :param oidc_issuer: The OpenID Connect issuer URL.
        :param redirect_url: The local URL to redirect the user back to after authorisation.
        :param client_id: The OAuth client ID, as registered with the OAuth provider.
        :param client_secret: The OAuth client secret, as registered with the OAuth provider.

        :raises OIDCError: If the issuer URL is invalid.
        """
        if not isinstance(oidc_issuer, str):
            raise OIDCError("OIDC issuer must be a string.")

        issuer = urlparse(oidc_issuer)
        if issuer.scheme != "https":
            raise OIDCError("OIDC issuer must use HTTPS.")

        if issuer.port is not None:
            raise OIDCError("OIDC issuer must not specify a port.")

        if issuer.query != "":
            raise OIDCError("OIDC issuer must not specify a query.")

        if issuer.fragment != "":
            raise OIDCError("OIDC issuer must not specify a fragment.")

        if issuer.path.endswith("/.well-known/openid-configuration"):
            issuer = issuer._replace(path=issuer.path.removesuffix("/.well-known/openid-configuration"))
            warnings.warn(
                f"OIDC issuer should not include the .well-known path. Assuming the issuer is {issuer.geturl()}."
            )

        self._connector = APIConnector(issuer.geturl(), transport)  # No authorization for OIDC discovery.
        self.__client_id = client_id
        self.__client_secret = client_secret

        self._config: OIDCConfig | None = None

    @property
    def config(self) -> OIDCConfig:
        return self._config

    @property
    def issuer(self) -> str:
        return self._connector.base_url.rstrip("/")

    @property
    def client_id(self) -> str:
        return self.__client_id

    async def __aenter__(self) -> OIDCConnector:
        await self._connector.open()
        await self.load_config()
        return self

    async def __aexit__(
        self, exc_type: type[Exception] | None, exc_value: Exception | None, traceback: TracebackType | None
    ) -> None:
        await self._connector.close()

    async def load_config(self):
        """Fetch the OIDC configuration from the issuer.

        https://openid.net/specs/openid-connect-discovery-1_0.html

        :raises OIDCError: If the configuration cannot be fetched or is invalid.
        """
        if self.config is not None:
            logger.debug("OpenID Connect configuration has already been fetched.")
            return

        logger.info(f"Fetching OpenID Connect configuration from {self.issuer}...")
        async with self._connector:
            try:
                self._config = await self._connector.call_api(
                    RequestMethod.GET,
                    ".well-known/openid-configuration",
                    header_params={"Accept": "application/json"},
                    response_types_map={"200": OIDCConfig},
                )

                if self.config.issuer != self.issuer:
                    raise OIDCError("OIDC issuer does not match the issuer in the configuration.")
            except EvoAPIException as e:
                raise OIDCError("Failed to fetch OIDC configuration.") from e

    async def begin_device_flow(self, scopes: OAuthScopes) -> DeviceFlowResponse:
        if self.config.device_authorization_endpoint is None:
            raise OIDCError("Device flow authorization is not supported by this auth provider.")

        data = {
            "client_id": self.client_id,
            "scope": str(scopes),
        }
        if self.__client_secret is not None:
            data["client_secret"] = self.__client_secret
        try:
            async with self._connector:
                try:
                    response = await self._connector.call_api(
                        RequestMethod.POST,
                        self.config.device_authorization_endpoint,
                        header_params={
                            "Accept": "application/json",
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        post_params=data,
                        response_types_map={"200": DeviceFlowResponse},
                    )
                except EvoAPIException as e:
                    error_json: dict = e.content
                    title = error_json.get("error", "Unexpected response from server")
                    detail = error_json.get("error_description", str(e))
                    raise OAuthError(f"{title}: {detail}")
                except ValidationError as e:
                    raise OAuthError("Invalid device flow response from server.") from e
            return response
        except OAuthError:
            raise  # Re-raise OAuthError exceptions.
        except Exception as exc:  # noqa: E722
            # Catch any other exceptions and raise OAuthError.
            raise OAuthError("Unable to begin device flow.") from exc

    async def fetch_token(self, data: dict, expected_response_model: Type[T]) -> T:
        """Fetch an access token from the server.

        :param data: The data to send to the server.

        :return: The token response.

        :raises OAuthError: If the token response cannot be fetched.
        """
        data["client_id"] = self.client_id
        if self.__client_secret is not None:
            data["client_secret"] = self.__client_secret

        try:
            async with self._connector:
                try:
                    response = await self._connector.call_api(
                        RequestMethod.POST,
                        self.config.token_endpoint,
                        header_params={
                            "Accept": "application/json",
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        post_params=data,
                        response_types_map={"200": expected_response_model},
                    )
                except EvoAPIException as e:
                    error_json: dict = e.content
                    title = error_json.get("error", "Unexpected response from server")
                    detail = error_json.get("error_description", str(e))
                    raise OAuthError(f"{title}: {detail}")
                except ValidationError as e:
                    raise OAuthError("Invalid token response from server.") from e
            return response
        except OAuthError:
            raise  # Re-raise OAuthError exceptions.
        except Exception as exc:  # noqa: E722
            # Catch any other exceptions and raise OAuthError.
            raise OAuthError("Unable to fetch access token." + str(exc)) from exc
