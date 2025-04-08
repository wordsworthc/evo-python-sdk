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

import asyncio
from datetime import timedelta
from unittest import mock
from urllib.parse import parse_qs, urlparse

from parameterized import parameterized

from evo.common.test_tools import long_test
from evo.oauth import OAuthError, OAuthRedirectHandler, OAuthScopes, OIDCConnector
from evo.oauth.data import AccessToken, OIDCConfig

from ._helpers import (
    AUTHORIZATION_CODE,
    CLIENT_ID,
    CLIENT_SECRET,
    ISSUED_AT,
    ISSUER_URL,
    REDIRECT_URL,
    STATE_TOKEN,
    VERIFIER_TOKEN,
    TestWithMockOIDCConnector,
    TestWithOIDCConnector,
    get_redirect,
    get_user_access_token,
    patch_urlsafe_tokens,
    patch_webbrowser_open,
)


class TestOAuthRedirectHandlerWithMockOIDC(TestWithMockOIDCConnector):
    def setUp(self) -> None:
        super().setUp()
        self.handler = OAuthRedirectHandler(oidc_connector=self.connector, redirect_url=REDIRECT_URL)
        self.handler.get_token = mock.AsyncMock(return_value=get_user_access_token())

    async def authenticate(self) -> None:
        """Authenticate and return the access token."""
        async with self.handler:
            response_text = await get_redirect(state=STATE_TOKEN, code=AUTHORIZATION_CODE)

        self.handler.get_token.assert_called_once_with(STATE_TOKEN, AUTHORIZATION_CODE)
        self.assertEqual(OAuthRedirectHandler._REDIRECT_HTML.decode("utf-8"), response_text)

    async def test_pending_with_success(self) -> None:
        """Test that the handler is pending until authentication is successful"""
        self.assertTrue(self.handler.pending)
        await self.authenticate()
        self.assertFalse(self.handler.pending)

    async def test_pending_with_failed(self) -> None:
        """Test that the handler is pending until authentication fails"""
        self.assertTrue(self.handler.pending)

        class SomeError(Exception): ...

        self.handler.get_token.side_effect = SomeError("Test error")
        await self.authenticate()
        self.assertFalse(self.handler.pending)

        with self.assertRaises(OAuthError):
            await self.handler.get_result()

    async def test_get_result(self) -> None:
        """Test that the handler returns the access token"""
        with self.assertRaises(OAuthError):
            await self.handler.get_result()

        async with self.handler:
            auth = asyncio.create_task(self.handler.get_result())
            redirect = get_redirect()
            self.assertFalse(auth.done())
            result, _ = await asyncio.gather(auth, redirect)
            self.assertTrue(auth.done())

        self.handler.get_token.assert_called_once_with(STATE_TOKEN, AUTHORIZATION_CODE)
        self.assertEqual(get_user_access_token(), result)

    @parameterized.expand(
        [
            ("no delay", 0),
            ("short delay", 1),
            ("longer delay", 5),
        ]
    )
    @long_test
    async def test_get_result_timeout(self, _label: str, delay: int) -> None:
        """Test that the handler times out waiting for the result."""
        async with self.handler:
            auth = asyncio.create_task(self.handler.get_result(delay))
            self.assertFalse(auth.done())
            with self.assertRaises(OAuthError):
                await auth
            self.assertTrue(auth.done())

    async def test_reentering_context(self) -> None:
        """Test that re-entering the context raises an error."""
        async with self.handler:
            with self.assertRaises(OAuthError):
                async with self.handler:
                    pass

    async def test_exiting_unentered_context(self) -> None:
        """Test that exiting an unentered context raises an error."""
        with self.assertRaises(OAuthError):
            await self.handler.__aexit__(None, None, None)

    async def test_login(self) -> None:
        """Test logging in with the handler."""
        expect_auth_url = "http://unit.test"
        self.handler.create_authorization_url = mock.Mock(return_value=expect_auth_url)

        async with self.handler:
            with patch_webbrowser_open(authenticate=True) as mock_webbrowser_open:
                result = await self.handler.login(OAuthScopes.all_evo)

        mock_webbrowser_open.assert_called_once_with(expect_auth_url)
        self.handler.get_token.assert_called_once_with(STATE_TOKEN, AUTHORIZATION_CODE)
        self.assertEqual(get_user_access_token(), result)

    @parameterized.expand(
        [
            ("no delay", 0),
            ("short delay", 1),
            ("longer delay", 5),
        ]
    )
    @long_test
    async def test_login_timeout(self, _label: str, delay: int) -> None:
        """Test that the handler times out waiting for the user to authenticate."""
        expect_auth_url = "http://unit.test"
        self.handler.create_authorization_url = mock.Mock(return_value=expect_auth_url)

        async with self.handler:
            with patch_webbrowser_open(authenticate=False) as mock_webbrowser_open:
                auth = asyncio.create_task(self.handler.login(OAuthScopes.all_evo, delay))
                self.assertFalse(auth.done())
                with self.assertRaises(OAuthError):
                    await auth
                self.assertTrue(auth.done())

        mock_webbrowser_open.assert_called_once_with(expect_auth_url)
        self.handler.get_token.assert_not_called()

    async def test_create_authorization_url_fails_if_unconfigured(self) -> None:
        """Test creating the authorization URL fails if OIDC Discovery has not been run"""
        with self.assertRaises(OAuthError):
            await self.handler.login(OAuthScopes.default)

    def test_create_authorization_url(self) -> None:
        """Test creating the authorization URL"""
        expected_url = self.get_expected_auth_url(
            state=STATE_TOKEN, verifier=VERIFIER_TOKEN, scopes=OAuthScopes.default
        )
        with patch_urlsafe_tokens(state=STATE_TOKEN, verifier=VERIFIER_TOKEN):
            actual_url = self.handler.create_authorization_url(OAuthScopes.default)

        # Check the auth URL and query parameters.
        self.assertEqual(expected_url, actual_url)

    def test_create_authorization_url_generates_unique_tokens(self) -> None:
        """Test creating the authorization URL generates unique state and verifier tokens."""

        uri_one = self.handler.create_authorization_url(OAuthScopes.default)
        query_one = parse_qs(urlparse(uri_one).query)

        uri_two = self.handler.create_authorization_url(OAuthScopes.default)
        query_two = parse_qs(urlparse(uri_two).query)

        self.assertNotEqual(query_one["state"], query_two["state"])
        self.assertNotEqual(query_one["code_challenge"], query_two["code_challenge"])


class TestOAuthRedirectHandler(TestWithOIDCConnector):
    def setUp(self) -> None:
        super().setUp()
        self.handler = OAuthRedirectHandler(oidc_connector=self.connector, redirect_url=REDIRECT_URL)
        self.connector._config = OIDCConfig(
            issuer=self.connector.issuer,
            authorization_endpoint=f"{self.connector.issuer}/authorization",
            token_endpoint=f"{self.connector.issuer}/token",
            response_types_supported=set(["code"]),
        )

    async def test_get_token_fails_if_unconfigured(self) -> None:
        """Test getting an access token fails if OIDC Discovery has not been run"""
        self.connector._config = None
        with self.assertRaises(OAuthError):
            await self.handler.get_token(STATE_TOKEN, AUTHORIZATION_CODE)

    async def test_get_token_fails_without_state(self) -> None:
        """Test getting an access token fails if the state token has not been generated"""
        with self.assertRaises(OAuthError):
            await self.handler.get_token(AUTHORIZATION_CODE, VERIFIER_TOKEN)

    @parameterized.expand(
        [
            ("happy day", ISSUER_URL, get_user_access_token()),
            ("no refresh token", ISSUER_URL, get_user_access_token(refresh_token=None)),
            (
                "sqid wrong issuer still works",
                # *.seequent.com issuer urls are not validated because the issuer ID in the ID token does not match the
                # openid configuration (which is not compliant with the OIDC spec). This has been acknowledged and is
                # not considered an issue because Seequent ID login with Evo is deprecated - use Bentley ID.
                "https://sqid.wrong.seequent.com",
                get_user_access_token(id_issuer="https://sqid.wrong.issuer.test"),
            ),
            (
                "nearly expired",
                ISSUER_URL,
                get_user_access_token(id_issued_at=ISSUED_AT - timedelta(minutes=4, seconds=59)),
            ),
            (
                "max allowable clock drift",
                ISSUER_URL,
                get_user_access_token(id_issued_at=ISSUED_AT + timedelta(minutes=4, seconds=59)),
            ),
            ("multiple audiences", ISSUER_URL, get_user_access_token(id_audience=["other", CLIENT_ID])),
        ]
    )
    async def test_get_token(self, _label: str, issuer_url: str, expect_token: AccessToken) -> None:
        """Test getting an access token"""
        # Replace the connector so that we can use a new issuer URL.
        self.connector = OIDCConnector(self.transport, issuer_url, CLIENT_ID, CLIENT_SECRET)
        self.connector._config = OIDCConfig(
            issuer=self.connector.issuer,
            authorization_endpoint=f"{self.connector.issuer}/authorization",
            token_endpoint=f"{self.connector.issuer}/token",
            response_types_supported=set(["code"]),
        )

        self.handler = OAuthRedirectHandler(oidc_connector=self.connector, redirect_url=REDIRECT_URL)
        with patch_urlsafe_tokens(state=STATE_TOKEN, verifier=VERIFIER_TOKEN):
            self.handler.create_authorization_url(OAuthScopes.default)

        with self.transport.set_http_response(200, expect_token.model_dump_json(by_alias=True, exclude_unset=True)):
            token = await self.handler.get_token(STATE_TOKEN, AUTHORIZATION_CODE)
        self.assert_fetched_token(
            path=issuer_url + "/token",
            grant_type="authorization_code",
            code=AUTHORIZATION_CODE,
            code_verifier=VERIFIER_TOKEN,
            redirect_uri=REDIRECT_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        self.assertEqual(expect_token, token)

    @parameterized.expand(
        [
            ("wrong issuer", get_user_access_token(id_issuer="https://wrong.issuer.test")),
            ("wrong audience", get_user_access_token(id_audience=["wrong", "audience"])),
            ("expired id token", get_user_access_token(id_issued_at=ISSUED_AT - timedelta(minutes=5))),
            ("id token from the future", get_user_access_token(id_issued_at=ISSUED_AT + timedelta(minutes=5))),
        ]
    )
    async def test_get_token_fails_with_invalid_id_token(self, _label: str, access_token: AccessToken) -> None:
        """Test getting an access token fails if the ID token is invalid"""
        with patch_urlsafe_tokens(state=STATE_TOKEN, verifier=VERIFIER_TOKEN):
            self.handler.create_authorization_url(OAuthScopes.default)

        with self.transport.set_http_response(200, access_token.model_dump_json(by_alias=True, exclude_unset=True)):
            with self.assertRaises(OAuthError):
                await self.handler.get_token(STATE_TOKEN, AUTHORIZATION_CODE)
        self.assert_fetched_token(
            grant_type="authorization_code",
            code=AUTHORIZATION_CODE,
            code_verifier=VERIFIER_TOKEN,
            redirect_uri=REDIRECT_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
