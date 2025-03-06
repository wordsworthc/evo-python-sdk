from __future__ import annotations

__all__ = [
    "FileMetadata",
    "FileVersion",
]

from dataclasses import dataclass
from datetime import datetime

from evo.common import ResourceMetadata, ServiceUser


@dataclass(frozen=True, kw_only=True)
class FileMetadata(ResourceMetadata):
    """Metadata about a file in the File API."""

    parent: str
    """The parent path of the file."""

    version_id: str
    """An arbitrary identifier for the file version."""

    size: int
    """The size of the file in bytes."""

    @property
    def path(self) -> str:
        """The full path of the file, formed by joining the parent and name, separated by a slash ('/')."""
        return f"{self.parent.removesuffix('/')}/{self.name.removeprefix('/')}"

    @property
    def url(self) -> str:
        """The URL of the file in the File API."""
        return (
            "{hub_url}/file/v2/orgs/{org_id}/workspaces/{workspace_id}/files/{file_id}?version_id={version_id}".format(
                hub_url=self.environment.hub_url.rstrip("/"),
                org_id=self.environment.org_id,
                workspace_id=self.environment.workspace_id,
                file_id=self.id,
                version_id=self.version_id,
            )
        )


@dataclass(frozen=True, kw_only=True)
class FileVersion:
    """Represents a version of a file."""

    version_id: str
    """An arbitrary identifier for the file version."""

    created_at: datetime
    """The date and time when the file version was created."""

    created_by: ServiceUser | None
    """The user who uploaded the file version."""
