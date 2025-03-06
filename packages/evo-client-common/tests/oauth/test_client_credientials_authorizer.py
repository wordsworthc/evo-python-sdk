from evo.common.pydantic_utils import export_json
from evo.common.test_tools import MockResponse
from evo.oauth import ClientCredentialsAuthorizer
from evo.oauth.data import AccessToken, OAuthScopes, OIDCConfig
from oauth._helpers import CLIENT_ID, CLIENT_SECRET, TestWithOIDCConnector, get_access_token


class TestClientCredentialsAuthorizer(TestWithOIDCConnector):
    def setUp(self):
        super().setUp()
        self.connector._config = OIDCConfig(
            issuer=self.connector.issuer,
            authorization_endpoint=f"{self.connector.issuer}/authorization",
            token_endpoint=f"{self.connector.issuer}/token",
            response_types_supported=set(["code"]),
            grant_types_supported=set(["client_credentials"]),
        )
        self.authorizer = ClientCredentialsAuthorizer(oidc_connector=self.connector, scopes=OAuthScopes.all_evo)
        self.first_token = get_access_token(access_token="first_token")
        self.second_token = get_access_token(access_token="second_token")

        self.transport.request.side_effect = [
            MockResponse(status_code=200, content=export_json(self.first_token)),
            MockResponse(status_code=200, content=export_json(self.second_token)),
        ]

    def assert_token_equals(self, expected_token: AccessToken | None) -> None:
        """Check that the access token is as expected."""
        actual_token: AccessToken | None = self.authorizer._BaseAuthorizer__token
        self.assertEqual(expected_token, actual_token)

    async def test_authorize(self):
        await self.authorizer.authorize()
        self.assert_token_equals(self.first_token)
        self.assert_fetched_token(
            grant_type="client_credentials",
            scope="openid profile organization email evo.discovery evo.workspace evo.blocksync evo.object evo.file",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )

    async def test_refresh_token(self):
        await self.authorizer.authorize()

        result = await self.authorizer.refresh_token()

        self.assertTrue(result)
        self.assert_fetched_token(
            grant_type="client_credentials",
            scope="openid profile organization email evo.discovery evo.workspace evo.blocksync evo.object evo.file",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        self.assert_token_equals(self.second_token)

    async def test_get_default_headers(self):
        await self.authorizer.authorize()

        headers = await self.authorizer.get_default_headers()

        self.assertEqual(headers, {"Authorization": "Bearer first_token"})

    async def test_get_default_headers_authorize_not_explicitly_called(self):
        headers = await self.authorizer.get_default_headers()

        self.assertEqual(headers, {"Authorization": "Bearer first_token"})
