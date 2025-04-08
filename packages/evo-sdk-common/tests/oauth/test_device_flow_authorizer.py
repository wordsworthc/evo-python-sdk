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

from evo.common import HTTPHeaderDict
from evo.common.data import RequestMethod
from evo.common.test_tools import AbstractTestRequestHandler, MockResponse, TestHTTPHeaderDict
from evo.oauth import DeviceFlowAuthorizer, OAuthError
from evo.oauth.data import DeviceFlowResponse, OAuthScopes, OIDCConfig

from ._helpers import (
    CLIENT_ID,
    CLIENT_SECRET,
    TestWithOIDCConnector,
    get_access_token,
)


class DeviceFlowHandler(AbstractTestRequestHandler):
    def __init__(self, base_url: str) -> None:
        self.oidc_config = OIDCConfig(
            issuer=base_url,
            authorization_endpoint=f"{base_url}/authorization",
            token_endpoint=f"{base_url}/token",
            device_authorization_endpoint=f"{base_url}/device_authorization",
            response_types_supported=set(["code"]),
            grant_types_supported=set(["urn:ietf:params:oauth:grant-type:device_code"]),
        )
        self.flow = DeviceFlowResponse(
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            expires_in=5,
        )
        self.token = get_access_token(access_token="access_token")

    def _handle_device_authorization(self) -> MockResponse:
        return MockResponse(
            status_code=200,
            content=self.flow.model_dump_json(by_alias=True, exclude_unset=True),
        )

    def _handle_token(self, params: dict) -> MockResponse:
        if self.flow is not None and params.get("device_code") == self.flow.device_code:
            return MockResponse(
                status_code=200,
                content=self.token.model_dump_json(by_alias=True, exclude_unset=True),
            )
        return self.bad_request()

    def _handle_post(self, url: str, params: dict) -> MockResponse:
        match url.removeprefix(self.oidc_config.issuer):
            case "/device_authorization":
                return self._handle_device_authorization()
            case "/token":
                return self._handle_token(params)
            case _:
                return self.not_found()

    async def request(
        self,
        method: RequestMethod,
        url: str,
        headers: HTTPHeaderDict | None = None,
        post_params: list[tuple[str, str | bytes]] | None = None,
        body: object | str | bytes | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> MockResponse:
        match method:
            case RequestMethod.POST:
                return self._handle_post(url, dict(post_params))
            case _:
                return self.not_found()


class TestDeviceFlowAuthorizer(TestWithOIDCConnector):
    def setUp(self) -> None:
        super().setUp()
        self.handler = DeviceFlowHandler(base_url=self.connector.issuer)
        self.connector._config = self.handler.oidc_config
        self.transport.set_request_handler(self.handler)
        self.authorizer = DeviceFlowAuthorizer(oidc_connector=self.connector)

    async def test_login(self) -> None:
        """Test the login method of the DeviceFlowAuthorizer."""
        async with self.authorizer.login() as flow:
            self.transport.assert_any_request_made(
                RequestMethod.POST,
                "/device_authorization",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                post_params=[
                    ("client_id", CLIENT_ID),
                    ("scope", str(OAuthScopes.default)),
                    ("client_secret", CLIENT_SECRET),
                ],
            )
            self.assertEqual(flow, self.handler.flow)

        self.assert_fetched_token(
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            device_code=flow.device_code,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )

    async def test_refresh_token(self) -> None:
        """Test the refresh_token method of the DeviceFlowAuthorizer."""
        # Device flow does not support refresh tokens.
        self.assertFalse(await self.authorizer.refresh_token())

    async def test_get_default_headers(self) -> None:
        """Test the get_default_headers method of the DeviceFlowAuthorizer."""
        async with self.authorizer.login():
            pass

        headers = await self.authorizer.get_default_headers()
        self.assertIs(type(headers), HTTPHeaderDict, "The default headers should be an HTTPHeaderDict.")
        self.assertEqual(
            TestHTTPHeaderDict({"Authorization": f"Bearer {self.handler.token.access_token}"}),
            TestHTTPHeaderDict(headers),
        )

    async def test_get_default_headers_before_login_fails(self) -> None:
        """Test that the get_default_headers method of the DeviceFlowAuthorizer fails before logging in."""
        with self.assertRaises(OAuthError):
            await self.authorizer.get_default_headers()
