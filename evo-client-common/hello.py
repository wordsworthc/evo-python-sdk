from evo.aio import AioTransport
from evo.common.utils import BackoffIncremental
from evo.oauth import OIDCConnector, AuthorizationCodeAuthorizer
from evo.common import ApiConnector
from evo.discovery import DiscoveryApiClient

import asyncio


ISSUER_URI = "https://qa-ims.bentley.com"
REDIRECT_URL = "http://localhost:3000/signin-oidc"
CLIENT_NAME = "EvoPythonSDK"
CLIENT_ID = CLIENT_NAME.lower()

async def main():
    print("Hello from evo-client-common!")
    # Configure the transport.
    transport = AioTransport(
        user_agent="evo-client-common-poc",
        max_attempts=3,
        backoff_method=BackoffIncremental(2),
        num_pools=4,
        verify_ssl=True,
    )

    # We can open the transport outside a context manager so that the underlying session is left open. This can save
    # time if we are going to make multiple batches of requests in the same area of code. Ideally, the transport should
    # be closed when it is no longer needed.
    await transport.open()

    authorizer = AuthorizationCodeAuthorizer(
        redirect_url=REDIRECT_URL,
        oidc_connector=OIDCConnector(
            transport=transport,
            oidc_issuer=ISSUER_URI,
            client_id=CLIENT_ID,
        ),
    )

    # Login to the Evo platform.
    await authorizer.login()

    # Select an Organization.
    async with ApiConnector("https://uat-api.test.seequent.systems", transport, authorizer) as idp_connector:
        discovery_client = DiscoveryApiClient(idp_connector)
        organizations = await discovery_client.list_organizations()

    # Select the first organization for this example.
    selected_organization = organizations[0]
    print("Selected organization:", selected_organization.display_name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
