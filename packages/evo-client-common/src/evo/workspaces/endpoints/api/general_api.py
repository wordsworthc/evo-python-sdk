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

from evo.common.connector import ApiConnector
from evo.common.data import EmptyResponse, RequestMethod  # noqa: F401

from ..models import *  # noqa: F403

__all__ = ["GeneralApi"]


class GeneralApi:
    """Api client for the General endpoint.

    NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    :param connector: Client for communicating with the API.
    """

    def __init__(self, connector: ApiConnector):
        self.connector = connector

    async def health_check_workspace_health_check_get(
        self,
        full: bool | None = None,
        check_dependencies: bool | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> dict:
        """Health check

        Checks if the service is healthy and able to response to requests

        :param full: (optional)
            Example: `False`
        :param check_dependencies: (optional)
            Example: `False`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseTypedError: If the server responds with any other HTTP status between
            400 and 599, and the body of the response has a type.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not have a type.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the query parameters.
        _query_params = {}
        if full is not None:
            _query_params["full"] = full
        if check_dependencies is not None:
            _query_params["check_dependencies"] = check_dependencies

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": dict,
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/workspace/health_check",
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def list_coordinate_systems(
        self,
        org_id: str,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> ListCoordinateSystemsResponse:  # noqa: F405
        """List coordinate systems

        Returns a list of coordinate systems for an organization.

        :param org_id:
            Format: `uuid`
            Example: `'org_id_example'`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseTypedError: If the server responds with any other HTTP status between
            400 and 599, and the body of the response has a type.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not have a type.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "org_id": org_id,
        }

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": ListCoordinateSystemsResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/workspace/orgs/{org_id}/coordinate_systems",
            path_params=_path_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def openapi_spec(
        self,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> dict:
        """Get OpenAPI schema

        Returns the OpenAPI schema for the Workspace Service API.

        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseTypedError: If the server responds with any other HTTP status between
            400 and 599, and the body of the response has a type.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not have a type.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": dict,
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/workspace/openapi.json",
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )
