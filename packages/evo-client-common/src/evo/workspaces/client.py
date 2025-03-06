from uuid import UUID

from evo.common import ApiConnector, HealthCheckType, ServiceHealth, ServiceUser
from evo.common.utils import get_service_health

from .data import Workspace, WorkspaceRole
from .endpoints import DefaultApi
from .endpoints.models import BoundingBox, CreateWorkspaceRequest, WorkspaceNonAdminResponse


class WorkspaceServiceClient:
    def __init__(self, connector: ApiConnector, org_id: UUID) -> None:
        self._connector = connector
        self._org_id = org_id
        self._default_api = DefaultApi(connector=self._connector)

    async def get_service_health(self, check_type: HealthCheckType = HealthCheckType.FULL) -> ServiceHealth:
        """Get the health of the workspace service.

        :param check_type: The type of health check to perform.

        :return: A ServiceHealth object.

        :raises EvoApiException: If the API returns an unexpected status code.
        :raises ClientValueError: If the response is not a valid service health check response.
        """
        return await get_service_health(self._connector, "workspace", check_type=check_type)

    def __parse_workspace_model(self, model: WorkspaceNonAdminResponse) -> Workspace:
        return Workspace(
            id=model.id,
            org_id=self._org_id,
            hub_url=self._connector.base_url,
            display_name=model.name,
            description=model.description,
            user_role=WorkspaceRole[str(model.current_user_role.value)],
            created_at=model.created_at,
            created_by=ServiceUser.from_model(model.created_by),
        )

    async def list_workspaces(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Workspace]:
        """List workspaces that are in the configured organization.

        :param limit: The maximum number of results to return.
        :param offset: The (zero-based) offset of the first item returned in the collection.

        :returns: a list of workspaces that the current user has permissions to see.
        """

        workspaces: list[Workspace] = []
        if offset is None:
            offset = 0

        while True:
            # For the time being, get all results at once. If there are more items, the next link will be populated
            workspace_list = await self._default_api.list_workspaces(
                org_id=str(self._org_id), limit=limit, offset=offset
            )
            workspaces += [self.__parse_workspace_model(model) for model in workspace_list.results]
            if workspace_list.links.next is not None:
                offset = len(workspaces)
            else:
                break

        return sorted(workspaces, key=lambda x: x.display_name)

    async def delete_workspace(
        self,
        workspace_id: UUID,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> None:
        """Delete workspaces by workspace id.

        :param workspace_id: The workspace id to delete.
        :param additional_headers: Additional headers to include in the request.
        :param request_timeout: The timeout for the request.

        :returns: An empty response.
        """
        await self._default_api.delete_workspace(
            org_id=str(self._org_id),
            workspace_id=str(workspace_id),
            additional_headers=additional_headers,
            request_timeout=request_timeout,
        )

    async def create_workspace(
        self,
        name: str,
        bounding_box: BoundingBox | None = None,
        default_coordinate_system: str | None = None,
        description: str | None = None,
        labels: list[str] | None = None,
    ) -> Workspace:
        """Create a new workspace.

        :param name: The name of the workspace.
        :param bounding_box: The bounding box of the workspace.
        :param default_coordinate_system: The default coordinate system of the workspace.
        :param description: The description of the workspace.
        :param labels: The labels of the workspace.

        :returns: The created workspace response.
        """
        # apply validation on the values
        if description is None:
            description = ""
        if default_coordinate_system is None:
            default_coordinate_system = ""
        if labels is not None and len(labels) > 20:
            raise ValueError("The labels field must contain 20 or fewer items.")

        create_workspace_request = CreateWorkspaceRequest(
            name=name,
            bounding_box=bounding_box,
            default_coordinate_system=default_coordinate_system,
            description=description,
            labels=labels,
        )
        model = await self._default_api.create_workspace(
            org_id=str(self._org_id), create_workspace_request=create_workspace_request
        )
        return self.__parse_workspace_model(model)
