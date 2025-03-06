from uuid import UUID

from evo.discovery import Hub, Organization

BASE_URL = "http://unittest.localhost/"
ACCESS_TOKEN = "<not-a-real-token>"

HUB = Hub(
    code="hub-code",
    display_name="Hub Name",
    url=BASE_URL,
    services=["service1", "service2"],
)
ORG = Organization(id=UUID(int=1234), display_name="Organization Name", hubs=(HUB,))
WORKSPACE_ID = UUID(int=5678)
