"""
Workspaces API
=============
The Workspaces API enables users to organize, maintain, and store project data, but does not use or process the data. The workspace APIs allow you to manage:
- Workspaces
- User roles within workspaces
- Workspace thumbnails
There are three pre-defined roles within workspaces:
- Owner: can perform all actions in the workspace
- Editor: can perform all actions excluding deleting of a workspace
- Viewer: can view the workspace
These user roles can be assigned to users in a workspace. Once a role has been assigned it can be replaced or removed.
Users can also retrieve user roles, the role of a particular user, and their own role if applicable.
For more information on using the Workspaces API, see the [Workspaces API overview](https://developer.seequent.com/docs/guides/workspaces/), or the API references here.
This code is generated from the OpenAPI specification for Workspaces API.
API version: 1.0
"""

# Import endpoint apis.
from .api import AdminApi, GeneralApi, ThumbnailsApi, WorkspacesApi

__all__ = [
    "AdminApi",
    "GeneralApi",
    "ThumbnailsApi",
    "WorkspacesApi",
]
