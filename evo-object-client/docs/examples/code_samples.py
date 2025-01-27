# --8<-- [start:ALL]
from evo.aio import AioTransport
from evo.common import ApiConnector
from evo.common.utils import BackoffIncremental
from evo.discovery import DiscoveryApiClient
from evo.oauth import AuthorizationCodeAuthorizer, OIDCConnector
from evo.object import ObjectServiceClient
from evo.workspaces import WorkspaceServiceClient

# Configure the transport.
# --8<-- [start:Transport]
transport = AioTransport(
    user_agent="evo-object-client",
    max_attempts=3,
    backoff_method=BackoffIncremental(2),
    num_pools=4,
    verify_ssl=True,
)
# --8<-- [end:Transport]

# Login to the Evo platform.
# --8<-- [start:OAuth]
authorizer = AuthorizationCodeAuthorizer(
    OIDCConnector(
        transport=transport,
        oidc_issuer="<issuer_url>",
        client_id="<client_id>",
    ),
    "https://example.com/signin-oidc",
)
await authorizer.login()
# --8<-- [end:OAuth]

# Select an Organization.
# --8<-- [start:Org-Discovery]
async with ApiConnector("https://example.com", transport, authorizer) as idp_connector:
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
service_client = ObjectServiceClient(workspace_env, hub_connector)
service_health = await service_client.get_service_health()
service_health.raise_for_status()
...
# --8<-- [end:ServiceClient]
# --8<-- [end:ALL]

# --8<-- [start:imports]
from uuid import UUID

from evo.aio import AioTransport
from evo.common import ApiConnector, Environment
from evo.oauth import AuthorizationCodeAuthorizer
from evo.object import ObjectServiceClient

# --8<-- [end:imports]

authorizer: AuthorizationCodeAuthorizer = ...
transport: AioTransport = ...

# Alternatively, you can skip discovery if you already know the hub URL, Organization ID, and workspace ID.
# --8<-- [start:Skip-Discovery]
hub_connector = ApiConnector("<hub-url>", transport, authorizer)
environment = Environment(
    hub_url="https://example.com",
    org_id=UUID("<organization-id>"),
    workspace_id=UUID("<workspace-id>"),
)
service_client = ObjectServiceClient(environment, hub_connector)
service_health = await service_client.get_service_health()
service_health.raise_for_status()
...
# --8<-- [end:Skip-Discovery]
