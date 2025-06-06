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

from evo.common.connector import APIConnector
from evo.common.data import EmptyResponse, RequestMethod  # noqa: F401

from ..models import *  # noqa: F403

__all__ = ["DiscoveryApi"]


class DiscoveryApi:
    """API client for the Discovery endpoint.

    NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    :param connector: Client for communicating with the API.
    """

    def __init__(self, connector: APIConnector):
        self.connector = connector

    async def v1_discovery_workspace_evo_identity_v1_discovery_get(
        self,
        service: list[str] | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> dict:
        """V1 Discovery


        :param service: (optional)
            Example: `['service_example']`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseTypedError: If the server responds with any other HTTP status between
            400 and 599, and the body of the response contains a descriptive `type` parameter.
        :raise evo.common.exceptions.EvoAPIException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not contain a `type` parameter.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the query parameters.
        _query_params = {}
        if service is not None:
            _query_params["service"] = service

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {
            "service": "multi",
        }

        _response_types_map = {
            "200": dict,
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/workspace/evo/identity/v1/discovery",
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def v2_discovery_workspace_evo_identity_v2_discovery_get(
        self,
        service: list[str] | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> dict:
        """V2 Discovery


        :param service: (optional)
            Example: `['service_example']`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseTypedError: If the server responds with any other HTTP status between
            400 and 599, and the body of the response contains a descriptive `type` parameter.
        :raise evo.common.exceptions.EvoAPIException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not contain a `type` parameter.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the query parameters.
        _query_params = {}
        if service is not None:
            _query_params["service"] = service

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {
            "service": "multi",
        }

        _response_types_map = {
            "200": dict,
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/workspace/evo/identity/v2/discovery",
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )
