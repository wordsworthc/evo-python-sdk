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
import contextlib
import hashlib
import hmac
import json
import unittest
from base64 import urlsafe_b64encode
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from unittest import mock
from urllib.parse import urlencode

from aiohttp.client import ClientSession

from evo.common import RequestMethod
from evo.common.test_tools import TestTransport, utc_datetime
from evo.oauth import AccessToken, OAuthScopes, OIDCConnector
from evo.oauth.data import OIDCConfig, UserAccessToken

ACCESS_TOKEN = "TestAccessToken"
ISSUER_URL = "https://auth.unittest.test"
CLIENT_ID = "TestClientID"
CLIENT_SECRET = "TestClientSecret"
REFRESH_TOKEN = "TestRefreshToken"
EXPIRES_IN = 3600
ISSUED_AT = utc_datetime(2024, 4, 1)

REDIRECT_URL = "http://localhost:1234"
STATE_TOKEN = "TestStateToken"
VERIFIER_TOKEN = "TestVerifierToken"
AUTHORIZATION_CODE = "TestAuthorizationCode"
OAUTH_SCOPES = OAuthScopes.all_evo


def _jwt_encode(**data: Any) -> str:
    return urlsafe_b64encode(json.dumps(data).encode("utf-8")).decode("utf-8").rstrip("=")


def _get_jwt(issuer: str, subject: str, audience: str | list[str], expiry: int, issued_at: int) -> str:
    header = _jwt_encode(typ="JWT", alg="HS256")
    payload = _jwt_encode(iss=issuer, sub=subject, aud=audience, exp=expiry, iat=issued_at)
    token = f"{header}.{payload}"
    digest = hmac.new(b"secret", token.encode("utf-8"), "sha256").digest()
    return token + "." + urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def get_user_access_token(
    access_token: str = ACCESS_TOKEN,
    id_issuer: str = ISSUER_URL,
    id_audience: str | list[str] = CLIENT_ID,
    id_issued_at: datetime = ISSUED_AT,
    refresh_token: str | None = REFRESH_TOKEN,
    expires_in: int = EXPIRES_IN,
    issued_at: datetime = ISSUED_AT,
) -> UserAccessToken:
    iat = round(id_issued_at.timestamp())
    exp = iat + expires_in
    return UserAccessToken(
        token_type="Bearer",
        access_token=access_token,
        id_token=_get_jwt(id_issuer, "TestSubject", id_audience, exp, iat),
        refresh_token=refresh_token,
        expires_in=expires_in,
        issued_at=issued_at,
        scope=str(OAUTH_SCOPES),
    )


def get_access_token(
    access_token: str = ACCESS_TOKEN,
    expires_in: int = EXPIRES_IN,
    issued_at: datetime = ISSUED_AT,
) -> AccessToken:
    return AccessToken(
        token_type="Bearer",
        access_token=access_token,
        expires_in=expires_in,
        issued_at=issued_at,
        scope=str(OAUTH_SCOPES),
    )


def oidc_config(
    issuer: str | None = ISSUER_URL,
    authorization_endpoint: str | None = f"{ISSUER_URL}/auth",
    token_endpoint: str | None = f"{ISSUER_URL}/token",
    response_types: list[str] | None = ["code"],
    grant_types: list[str] | None = ["authorization_code", "refresh_token", "client_credentials"],
) -> dict:
    config = {
        "issuer": issuer,
        "authorization_endpoint": authorization_endpoint,
        "token_endpoint": token_endpoint,
        "response_types_supported": response_types,
        "grant_types_supported": grant_types,
    }
    for key, value in config.copy().items():
        if value is None:
            del config[key]
    return config


def oidc_config_response(
    issuer: str | None = ISSUER_URL,
    authorization_endpoint: str | None = f"{ISSUER_URL}/auth",
    token_endpoint: str | None = f"{ISSUER_URL}/token",
    response_types: list[str] | None = ["code"],
    grant_types: list[str] | None = ["authorization_code", "refresh_token", "client_credentials"],
) -> str:
    return json.dumps(
        oidc_config(
            issuer=issuer,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            response_types=response_types,
            grant_types=grant_types,
        )
    )


@contextlib.contextmanager
def patch_urlsafe_tokens(state: str = STATE_TOKEN, verifier: str = VERIFIER_TOKEN) -> Iterator[None]:
    with mock.patch("secrets.token_urlsafe", side_effect=[state, verifier]):
        yield


async def get_redirect(state: str = STATE_TOKEN, code: str = AUTHORIZATION_CODE) -> str:
    async with ClientSession() as session:
        async with session.get(REDIRECT_URL, params={"state": state, "code": code}) as response:
            response.raise_for_status()
            return await response.text()


@contextlib.contextmanager
def patch_webbrowser_open(authenticate: bool) -> Iterator[mock.Mock]:
    """Patch the `webbrowser.open` function and optionally authenticate the user."""

    def webbrowser_open(_url: str) -> None:
        if authenticate:
            asyncio.ensure_future(get_redirect(state=STATE_TOKEN, code=AUTHORIZATION_CODE))

    with mock.patch("webbrowser.open", side_effect=webbrowser_open) as mock_open:
        yield mock_open


class TestWithOIDCConnector(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.transport = TestTransport(base_url=ISSUER_URL)
        self.connector = OIDCConnector(self.transport, ISSUER_URL, CLIENT_ID, CLIENT_SECRET)

    def get_expected_auth_url(
        self, state: str = STATE_TOKEN, verifier: str = VERIFIER_TOKEN, scopes: OAuthScopes = OAuthScopes.default
    ) -> str:
        base_url = self.connector.issuer + self.connector.config.authorization_endpoint

        # urlsafe base64 encoded sha256 hash of the verifier token.
        expect_challenge = (
            urlsafe_b64encode(
                hashlib.sha256(verifier.encode()).digest(),
            )
            .decode()
            .strip("=")
        )

        query = {
            "response_type": "code",
            "client_id": self.connector.client_id,
            "redirect_uri": REDIRECT_URL,
            "state": state,
            "scope": str(scopes),
            "code_challenge": expect_challenge,
            "code_challenge_method": "S256",
        }
        return base_url + "?" + urlencode(sorted(query.items()))

    def assert_fetched_token(self, path: str = "/token", **data: str) -> None:
        """Assert that a token was fetched with the given data"""
        self.transport.assert_any_request_made(
            RequestMethod.POST,
            path,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            post_params=list(data.items()),
        )


class MockOIDCConnector(mock.AsyncMock):
    def __init__(self, issuer=ISSUER_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, **kwargs):
        super().__init__(kwargs=kwargs)
        self._issuer = issuer
        self._client_id = client_id
        self._client_secret = client_secret
        self._config = None

    @property
    def issuer(self):
        return ISSUER_URL

    @property
    def config(self) -> OIDCConfig:
        return self._config

    @property
    def client_id(self):
        return self._client_id


class TestWithMockOIDCConnector(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.transport = TestTransport(base_url=ISSUER_URL)
        self.connector = MockOIDCConnector(spec=OIDCConnector)
        self.connector._config = OIDCConfig(
            issuer=self.connector.issuer,
            authorization_endpoint=f"{self.connector.issuer}/authorization",
            token_endpoint=f"{self.connector.issuer}/token",
            response_types_supported=set(["code"]),
        )

    def get_expected_auth_url(
        self, state: str = STATE_TOKEN, verifier: str = VERIFIER_TOKEN, scopes: OAuthScopes = OAuthScopes.default
    ) -> str:
        base_url = self.connector.issuer + self.connector._config.authorization_endpoint

        # urlsafe base64 encoded sha256 hash of the verifier token.
        expect_challenge = (
            urlsafe_b64encode(
                hashlib.sha256(verifier.encode()).digest(),
            )
            .decode()
            .strip("=")
        )

        query = {
            "response_type": "code",
            "client_id": self.connector.client_id,
            "redirect_uri": REDIRECT_URL,
            "state": state,
            "scope": str(scopes),
            "code_challenge": expect_challenge,
            "code_challenge_method": "S256",
        }
        return base_url + "?" + urlencode(sorted(query.items()))

    def assert_fetched_token(self, path: str = "/token", **data: str) -> None:
        """Assert that a token was fetched with the given data"""
        self.transport.assert_any_request_made(
            RequestMethod.POST,
            path,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            post_params=list(data.items()),
        )
