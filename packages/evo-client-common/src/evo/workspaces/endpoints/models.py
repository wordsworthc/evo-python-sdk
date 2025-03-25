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

# generated by datamodel-codegen:
#   filename:  spec.yaml

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from pydantic import (
    AnyUrl,
    Field,
    RootModel,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
)

from .._model_config import CustomBaseModel


class BaseInstanceUserRoleResponse(CustomBaseModel):
    description: Annotated[StrictStr, Field(title="Description")]
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[StrictStr, Field(title="Name")]


class Coordinate(RootModel[list[StrictFloat | StrictInt]]):
    root: Annotated[list[StrictFloat | StrictInt], Field(max_length=2, min_length=2)]
    """
    Coordinate as [longitude, latitude]. First one MUST be the longitude.
    """


class CoordinateSystemEntry(CustomBaseModel):
    title: Annotated[StrictStr, Field(title="Title")]
    well_known_id: Annotated[StrictStr, Field(title="Well Known Id")]


class Label(RootModel[StrictStr]):
    root: StrictStr


class ErrorInvalidParam(CustomBaseModel):
    name: Annotated[StrictStr, Field(title="Name")]
    reason: Annotated[StrictStr, Field(title="Reason")]


class ErrorResponse(CustomBaseModel):
    detail: Annotated[StrictStr | None, Field(title="Detail")] = None
    invalid_params: Annotated[
        list[ErrorInvalidParam] | None,
        Field(alias="invalid-params", title="Invalid-Params"),
    ] = None
    status: Annotated[StrictInt, Field(title="Status")]
    title: Annotated[StrictStr, Field(title="Title")]
    type: Annotated[StrictStr, Field(title="Type")]


class GeometryTypeEnum(Enum):
    Polygon = "Polygon"


class OrganizationSettingsFieldResponse(CustomBaseModel):
    ml_enabled: Annotated[StrictBool, Field(title="Ml Enabled")] = False


class OrganizationSettingsResponse(CustomBaseModel):
    created_at: Annotated[datetime | None, Field(title="Created At")] = None
    created_by: Annotated[UUID | None, Field(title="Created By")] = None
    id: Annotated[UUID, Field(title="Id")]
    settings: Annotated[OrganizationSettingsFieldResponse, Field()] = {"ml_enabled": False}
    updated_at: Annotated[datetime | None, Field(title="Updated At")] = None
    updated_by: Annotated[UUID | None, Field(title="Updated By")] = None


class PaginationLinks(CustomBaseModel):
    count: Annotated[StrictInt, Field(title="Count")]
    first: Annotated[AnyUrl, Field(title="First")]
    last: Annotated[AnyUrl, Field(title="Last")]
    next: Annotated[AnyUrl | None, Field(title="Next")] = None
    previous: Annotated[AnyUrl | None, Field(title="Previous")] = None
    total: Annotated[StrictInt, Field(title="Total")]


class PaginationLinksWithoutTotal(CustomBaseModel):
    count: Annotated[StrictInt, Field(title="Count")]
    first: Annotated[AnyUrl, Field(title="First")]
    next: Annotated[AnyUrl | None, Field(title="Next")] = None
    previous: Annotated[AnyUrl | None, Field(title="Previous")] = None


class RoleEnum(Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class User(CustomBaseModel):
    email: Annotated[StrictStr | None, Field(title="Email")] = None
    full_name: Annotated[StrictStr | None, Field(title="Full Name")] = None
    role: RoleEnum
    user_id: Annotated[UUID, Field(title="User Id")]


class UserModel(CustomBaseModel):
    email: Annotated[StrictStr | None, Field(title="Email")] = None
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[StrictStr | None, Field(title="Name")] = None


class UserRole(CustomBaseModel):
    role: RoleEnum
    user_id: Annotated[UUID, Field(title="User Id")]


class UserRoleAssignmentRequest(CustomBaseModel):
    role: RoleEnum
    user_id: Annotated[UUID, Field(title="User Id")]
    workspace_id: Annotated[UUID, Field(title="Workspace Id")]


class UserRoleViaEmail(CustomBaseModel):
    email: Annotated[StrictStr, Field(title="Email")]
    role: RoleEnum


class WorkspaceMlEnablementRequest(CustomBaseModel):
    ml_enabled: Annotated[StrictBool, Field(title="Ml Enabled")]
    workspace_id: Annotated[UUID, Field(title="Workspace Id")]


class AssignRoleRequest(RootModel[UserRole | UserRoleViaEmail]):
    root: Annotated[UserRole | UserRoleViaEmail, Field(title="AssignRoleRequest")]


class BaseInstanceUserResponse(CustomBaseModel):
    email: Annotated[StrictStr, Field(title="Email")]
    full_name: Annotated[StrictStr, Field(title="Full Name")]
    id: Annotated[UUID, Field(title="Id")]
    roles: Annotated[list[BaseInstanceUserRoleResponse], Field(title="Roles")]


class BoundingBox(CustomBaseModel):
    coordinates: Annotated[list[list[Coordinate]], Field(title="Coordinates")]
    type: GeometryTypeEnum


class BulkUserRoleAssignmentsRequest(CustomBaseModel):
    role_assignments: Annotated[list[UserRoleAssignmentRequest], Field(max_length=100, title="Role Assignments")]


class CoordinateSystemCategory(CustomBaseModel):
    items: Annotated[list[CoordinateSystemCategory | CoordinateSystemEntry], Field(title="Items")]
    title: Annotated[StrictStr, Field(title="Title")]


class CreateWorkspaceRequest(CustomBaseModel):
    bounding_box: BoundingBox | None = None
    default_coordinate_system: Annotated[StrictStr, Field(title="Default Coordinate System")] = ""
    description: Annotated[StrictStr, Field(title="Description")] = ""
    labels: Annotated[list[Label] | None, Field(max_length=20, title="Labels")] = None
    """
    A list of labels
    """
    name: Annotated[StrictStr, Field(title="Name")]
    """
    The name of the workspace, unique within an organization and hub
    """


class ListCoordinateSystemsResponse(CustomBaseModel):
    links: Annotated[dict[str, Any], Field(title="Links")]
    results: Annotated[list[CoordinateSystemCategory], Field(title="Results")]


class ListInstanceUsersResponse(CustomBaseModel):
    links: PaginationLinksWithoutTotal
    results: Annotated[list[BaseInstanceUserResponse], Field(title="Results")]


class ListUserRoleResponse(CustomBaseModel):
    links: Annotated[dict[str, Any], Field(title="Links")]
    results: Annotated[list[User], Field(title="Results")]


class MlEnablementRequest(CustomBaseModel):
    ml_enablements: Annotated[
        list[WorkspaceMlEnablementRequest],
        Field(max_length=100, title="Ml Enablements"),
    ]


class UpdateWorkspaceRequest(CustomBaseModel):
    bounding_box: BoundingBox | None = None
    default_coordinate_system: Annotated[StrictStr | None, Field(title="Default Coordinate System")] = None
    description: Annotated[StrictStr | None, Field(title="Description")] = None
    labels: Annotated[list[Label] | None, Field(max_length=20, title="Labels")] = None
    """
    A list of labels
    """
    name: Annotated[StrictStr | None, Field(max_length=60, min_length=1, title="Name")] = None


class UserWorkspaceResponse(CustomBaseModel):
    bounding_box: BoundingBox | None = None
    created_at: Annotated[datetime, Field(title="Created At")]
    created_by: UserModel
    default_coordinate_system: Annotated[StrictStr, Field(title="Default Coordinate System")] = ""
    description: Annotated[StrictStr, Field(title="Description")] = ""
    id: Annotated[UUID, Field(title="Id")]
    labels: Annotated[list[StrictStr], Field(title="Labels")] = []
    ml_enabled: Annotated[StrictBool, Field(title="Ml Enabled")] = False
    name: Annotated[StrictStr, Field(title="Name")]
    """
    The name of the workspace, unique within an organization and hub
    """
    self_link: Annotated[AnyUrl, Field(title="Self Link")]
    updated_at: Annotated[datetime, Field(title="Updated At")]
    updated_by: UserModel
    user_role: RoleEnum


class WorkspaceRoleOptionalResponse(CustomBaseModel):
    bounding_box: BoundingBox | None = None
    created_at: Annotated[datetime, Field(title="Created At")]
    created_by: UserModel
    current_user_role: RoleEnum | None = None
    default_coordinate_system: Annotated[StrictStr, Field(title="Default Coordinate System")] = ""
    description: Annotated[StrictStr, Field(title="Description")] = ""
    id: Annotated[UUID, Field(title="Id")]
    labels: Annotated[list[StrictStr], Field(title="Labels")] = []
    ml_enabled: Annotated[StrictBool, Field(title="Ml Enabled")] = False
    name: Annotated[StrictStr, Field(title="Name")]
    """
    The name of the workspace, unique within an organization and hub
    """
    self_link: Annotated[AnyUrl, Field(title="Self Link")]
    updated_at: Annotated[datetime, Field(title="Updated At")]
    updated_by: UserModel


class WorkspaceRoleRequiredResponse(CustomBaseModel):
    bounding_box: BoundingBox | None = None
    created_at: Annotated[datetime, Field(title="Created At")]
    created_by: UserModel
    current_user_role: RoleEnum
    default_coordinate_system: Annotated[StrictStr, Field(title="Default Coordinate System")] = ""
    description: Annotated[StrictStr, Field(title="Description")] = ""
    id: Annotated[UUID, Field(title="Id")]
    labels: Annotated[list[StrictStr], Field(title="Labels")] = []
    ml_enabled: Annotated[StrictBool, Field(title="Ml Enabled")] = False
    name: Annotated[StrictStr, Field(title="Name")]
    """
    The name of the workspace, unique within an organization and hub
    """
    self_link: Annotated[AnyUrl, Field(title="Self Link")]
    updated_at: Annotated[datetime, Field(title="Updated At")]
    updated_by: UserModel


class ListUserWorkspacesResponse(CustomBaseModel):
    links: PaginationLinks
    results: Annotated[list[UserWorkspaceResponse], Field(title="Results")]


class ListWorkspacesResponse(CustomBaseModel):
    links: PaginationLinks
    results: Annotated[
        list[WorkspaceRoleRequiredResponse] | list[WorkspaceRoleOptionalResponse],
        Field(title="Results"),
    ]


CoordinateSystemCategory.model_rebuild()
