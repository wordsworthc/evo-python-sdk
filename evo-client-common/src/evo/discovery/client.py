from collections.abc import Sequence
from uuid import UUID

from evo.common import ApiConnector, RequestMethod
from evo.common.pydantic_utils import BaseModel, validator

from .data import Hub, Organization

__all__ = ["DiscoveryApiClient"]


class _ServiceDiscoveryHub(BaseModel):
    url: str
    code: str
    display_name: str


class _ServiceDiscoveryOrganization(BaseModel):
    id: UUID
    display_name: str


class _ServiceDiscoveryAccess(BaseModel):
    hub_code: str
    org_id: UUID
    services: list[str]


class _ServiceDiscoveryResult(BaseModel):
    organizations: list[_ServiceDiscoveryOrganization]
    hubs: list[_ServiceDiscoveryHub]
    service_access: list[_ServiceDiscoveryAccess]

    @validator("organizations", "hubs")
    def _sort_by_display_name(cls, v: list) -> list:
        # Sort organizations and hubs alphanumerically by display name.
        return sorted(v, key=lambda i: i.display_name)

    def __contains__(self, item: tuple[_ServiceDiscoveryOrganization, _ServiceDiscoveryHub]) -> bool:
        assert isinstance(item, tuple) and len(item) == 2, "Expected a tuple containing organization and hub."
        org, hub = item
        assert isinstance(org, _ServiceDiscoveryOrganization), (
            "Expected organization to be an instance of _ServiceDiscoveryOrganization."
        )
        assert isinstance(hub, _ServiceDiscoveryHub), "Expected hub to be an instance of _ServiceDiscoveryHub."

        for access in self.service_access:
            if access.org_id == org.id and access.hub_code == hub.code:
                return True
        return False

    def get_service_access_services(self, org: _ServiceDiscoveryOrganization, hub: _ServiceDiscoveryHub) -> list[str]:
        assert (org, hub) in self, "Expected a service access entry for the specified organization and hub."
        return next(
            service_access
            for service_access in self.service_access
            if service_access.hub_code == hub.code and service_access.org_id == org.id
        ).services


class _DiscoveryResult(BaseModel):
    discovery: _ServiceDiscoveryResult


class DiscoveryApiClient:
    """Simple client for interacting with the Discovery API."""

    def __init__(self, connector: ApiConnector) -> None:
        """
        :param connector: The API connector to use for making requests.
        """
        self._connector = connector

    async def list_organizations(self, service_codes: Sequence[str] = ("evo",)) -> list[Organization]:
        """Get organizations with access to the specified services.

        :param service_codes: The service codes to use in the query.
        """
        result = await self._connector.call_api(
            RequestMethod.GET,
            "/evo/identity/v2/discovery",
            query_params={"service": service_codes},
            collection_formats={"service": "multi"},
            response_types_map={"200": _DiscoveryResult},
        )
        discovered = result.discovery
        return [
            Organization(
                id=org.id,
                display_name=org.display_name,
                hubs=tuple(
                    Hub(
                        url=hub.url,
                        code=hub.code,
                        display_name=hub.display_name,
                        services=tuple(discovered.get_service_access_services(org, hub)),
                    )
                    for hub in discovered.hubs
                    if (org, hub) in discovered
                ),
            )
            for org in discovered.organizations
        ]
