from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from evo.common import Environment, ServiceUser

from .exceptions import UserPermissionTypeError

__all__ = [
    "ServiceUser",
    "UserPermission",
    "WorkspaceRole",
    "Workspace",
]


class UserPermission(enum.Flag):
    """Effective user permissions within a workspace."""

    read = enum.auto()
    """The user can read data within the workspace."""

    write = enum.auto()
    """The user can write data within the workspace."""

    manage = enum.auto()
    """The user can manage the workspace itself."""


class WorkspaceRole(enum.Flag):
    """The role of the user within a workspace."""

    viewer = UserPermission.read.value
    """A read-only user."""

    editor = UserPermission.write.value | viewer
    """A user that can read and write data."""

    owner = UserPermission.manage.value | editor
    """A user that can read and write, and manage the workspace."""

    def __contains__(self, item: UserPermission | WorkspaceRole) -> bool:
        if isinstance(item, (UserPermission, WorkspaceRole)):
            return (item.value & self.value) == item.value
        else:
            raise UserPermissionTypeError(
                f"The required permission is invalid, "
                f"expected UserPermission or WorkspaceRole but got type {type(item).__name__}"
            )


@dataclass(frozen=True, kw_only=True)
class Workspace:
    """Metadata about a workspace environment."""

    id: UUID
    """The workspace UUID."""

    display_name: str
    """The workspace display name."""

    description: str | None
    """The workspace description."""

    user_role: WorkspaceRole
    """The role of the current user in the workspace."""

    org_id: UUID
    """UUID of the organization the workspace belongs to."""

    hub_url: str
    """The URL of the hub the workspace resides in."""

    created_at: datetime
    """A timestamp representing when the workspace was created."""

    created_by: ServiceUser
    """The info of the user that created the workspace."""

    def user_has_permission(self, required_permission: UserPermission | WorkspaceRole) -> bool:
        """Test whether the current user has at least the given permission for this workspace.

        :param required_permission: the minimum role or permission the user must have

        :returns: whether the user has sufficient permissions for this workspace - any `user_role` with all the required
          permissions will return True.
        """
        return required_permission in self.user_role

    def get_environment(self) -> Environment:
        """Return an environment that can be used to interact with the workspace."""
        return Environment(hub_url=self.hub_url, org_id=self.org_id, workspace_id=self.id)

    def __hash__(self) -> int:
        return hash(self.id)
