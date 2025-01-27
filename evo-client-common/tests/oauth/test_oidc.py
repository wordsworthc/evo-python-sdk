from parameterized import parameterized

from evo.common import RequestMethod
from evo.oauth.exceptions import OIDCError

from ._helpers import (
    TestWithOIDCConnector,
    oidc_config_response,
)


class TestOIDCConnector(TestWithOIDCConnector):
    async def test_load_config(self) -> None:
        """Test OIDC Discovery"""
        self.transport.assert_no_requests()

        with self.transport.set_http_response(200, oidc_config_response()):
            await self.connector.load_config()

        self.transport.assert_request_made(
            RequestMethod.GET, "/.well-known/openid-configuration", headers={"Accept": "application/json"}
        )

    @parameterized.expand(
        [
            # Missing fields.
            ("missing issuer", oidc_config_response(issuer=None)),
            # Fields with invalid values.
            ("wrong issuer", oidc_config_response(issuer="https://wrong.issuer.test")),
        ]
    )
    async def test_invalid_configuration(
        self,
        _label: str,
        config_response: str,
    ) -> None:
        """Test OIDC Discovery failure conditions"""
        self.transport.assert_no_requests()

        with self.transport.set_http_response(200, config_response), self.assertRaises(OIDCError):
            await self.connector.load_config()

        self.transport.assert_request_made(
            RequestMethod.GET, "/.well-known/openid-configuration", headers={"Accept": "application/json"}
        )

    async def test_aenter(self) -> None:
        """Test entering the context manager triggers OIDC Discovery"""
        self.transport.assert_no_requests()

        with self.transport.set_http_response(200, oidc_config_response()):
            async with self.connector:
                self.transport.assert_request_made(
                    RequestMethod.GET, "/.well-known/openid-configuration", headers={"Accept": "application/json"}
                )
