# --8<-- [start:ALL]
from evo.aio import AioTransport
from evo.common import ApiConnector, BaseServiceClient
from evo.common.utils import BackoffIncremental
from evo.discovery import DiscoveryApiClient
from evo.oauth import AuthorizationCodeAuthorizer, OIDCConnector
from evo.workspaces import WorkspaceServiceClient

# Configure the transport.
# --8<-- [start:Transport]
transport = AioTransport(
    user_agent="evo-client-common-poc",
    max_attempts=3,
    backoff_method=BackoffIncremental(2),
    num_pools=4,
    verify_ssl=True,
)
# --8<-- [end:Transport]

# Login to the Evo platform.
# User Login
# --8<-- [start:OAuth-AuthorizationCodeAuthorizer]
authorizer = AuthorizationCodeAuthorizer(
    redirect_url="<redirect_url>",
    oidc_connector=OIDCConnector(
        transport=transport,
        oidc_issuer="<issuer_url>",
        client_id="<client_id>",
    ),
)
await authorizer.login()
# --8<-- [end:OAuth-AuthorizationCodeAuthorizer]


# Select an Organization.
# --8<-- [start:Org-Discovery]
async with ApiConnector("https://uat-api.test.seequent.systems", transport, authorizer) as idp_connector:
    discovery_client = DiscoveryApiClient(idp_connector)
    organizations = await discovery_client.list_organizations()
# --8<-- [end:Org-Discovery]

selected_org = organizations[0]

# Select a hub and create a connector.
hub_connector = ApiConnector(selected_org.hubs[0].url, transport, authorizer)

# Select a Workspace.
# --8<-- [start:Workspace-Discovery]
async with hub_connector:
    workspace_client = WorkspaceServiceClient(hub_connector, selected_org.id)
    workspaces = await workspace_client.list_workspaces()
# --8<-- [end:Workspace-Discovery]

workspace = workspaces[0]
workspace_env = workspace.get_environment()

# Interact with a service.
# --8<-- [start:ServiceClient]
async with hub_connector:
    service_client = BaseServiceClient(workspace_env, hub_connector)
    ...
# --8<-- [end:ServiceClient]
# --8<-- [end:ALL]

# --8<-- [start:imports]
from uuid import UUID

from evo.aio import AioTransport
from evo.common import ApiConnector, BaseServiceClient, Environment
from evo.common.utils import BackoffIncremental
from evo.oauth import AuthorizationCodeAuthorizer, OIDCConnector

# --8<-- [end:imports]

authorizer: AuthorizationCodeAuthorizer = ...
transport: AioTransport = ...

# Alternatively, you can skip discovery if you already know the hub URL, Organization ID, and workspace ID.
# --8<-- [start:Skip-Discovery]
environment = Environment(
    hub_url="<hub-url>",
    org_id=UUID("<organization-id>"),
    workspace_id=UUID("<workspace-id>"),
)
hub_connector = ApiConnector(environment.hub_url, transport, authorizer)
async with hub_connector:
    service_client = BaseServiceClient(environment, hub_connector)
    ...
# --8<-- [end:Skip-Discovery]
