"""
File API
=============

The File API provides the ability to manage files of any type or size, associated with
your Evo workspace. Enable your product with Evo connected workflows by integrating with the Seequent Evo
File API. Most file formats and sizes are accepted.

Files can be referenced by their UUID, or by a user-defined file path. Files are versioned, so updating or
replacing them will create a new version of the file. The latest version of the file is always returned
unless a specific version is requested.

For more information on using the File API, see [Overview](/docs/guides/file), or the API references here.


This code is generated from the OpenAPI specification for File API.
API version: 2.7.0
"""

from evo.common.connector import ApiConnector
from evo.common.data import EmptyResponse, RequestMethod

from ..models import *  # noqa: F403

__all__ = ["FileV2Api"]


class FileV2Api:
    """Api client for the file_v2 endpoint.

    NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    :param connector: Client for communicating with the API.
    """

    def __init__(self, connector: ApiConnector):
        self.connector = connector

    async def delete_file_by_id(
        self,
        file_id: str,
        organisation_id: str,
        workspace_id: str,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> EmptyResponse:
        """Delete a file by ID

        Request to delete a file. This will delete the file and all historic versions.

        :param file_id:
            Format: `uuid`
            Example: `'file_id_example'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_id": file_id,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the header parameters.
        _header_params = {}
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "204": EmptyResponse,
        }

        return await self.connector.call_api(
            method=RequestMethod.DELETE,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/{file_id}",
            path_params=_path_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def delete_file_by_path(
        self,
        file_path: str,
        organisation_id: str,
        workspace_id: str,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> EmptyResponse:
        """Delete a file by path

        Request to delete a file. This will delete the file and all historic versions.

        :param file_path: Path to the file.
            Example: `'a/b/file.txt'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_path": file_path,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the header parameters.
        _header_params = {}
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "204": EmptyResponse,
        }

        return await self.connector.call_api(
            method=RequestMethod.DELETE,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/path/{file_path}",
            path_params=_path_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def get_file_by_id(
        self,
        file_id: str,
        organisation_id: str,
        workspace_id: str,
        version_id: str | None = None,
        include_versions: bool | None = None,
        deleted: bool | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> DownloadFileResponse:  # noqa: F405
        """Download a file by ID

        Request file metadata and a delegated download link for a specified file by ID. The `download` link should be followed to download the file contents from blob storage. This link is pre-signed and will expire after 30 minutes. Set the `include_versions` query parameter to `true` to get the complete list of available versions. Set the `version` query parameter to request a download link for that specific version of the specified file. If `version` is not set, the latest version of the file will be returned.

        :param file_id: UUID of a file.
            Format: `uuid`
            Example: `'255fa5a6-f37d-11ed-93c1-00155d19a71b'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param version_id: (optional) Optional version ID for the desired file version. By default, the response will return the _latest_ version.
            Format: `int64`
            Example: `'1223372036854775807'`
        :param include_versions: (optional) Optional inclusion of the `DownloadFile.versions`. By default, the response will return `versions` as `null`.
            Example: `False`
        :param deleted: (optional) Optional flag to include deleted files. By default, the response will not include deleted files.
            Example: `True`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_id": file_id,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the query parameters.
        _query_params = {}
        if version_id is not None:
            _query_params["version_id"] = version_id
        if include_versions is not None:
            _query_params["include_versions"] = include_versions
        if deleted is not None:
            _query_params["deleted"] = deleted

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": DownloadFileResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/{file_id}",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def get_file_by_path(
        self,
        file_path: str,
        organisation_id: str,
        workspace_id: str,
        version_id: str | None = None,
        include_versions: bool | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> DownloadFileResponse:  # noqa: F405
        """Download a file by path

        Request file metadata and a delegated download link for a specified file by path. The `download` link should be followed to download the file contents from blob storage. This link is pre-signed and will expire after 30 minutes. Set the `include_versions` query parameter to `true` to get the complete list of available versions. Set the `version` query parameter to request a download link for that specific version of the specified file. If `version` is not set, the latest version of the file will be returned.

        :param file_path: Path to the file.
            Example: `'a/b/file.txt'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param version_id: (optional) Optional version ID for the desired file version. By default, the response will return the _latest_ version.
            Format: `int64`
            Example: `'1223372036854775807'`
        :param include_versions: (optional) Optional inclusion of the `DownloadFile.versions`. By default, the response will return `versions` as `null`.
            Example: `False`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_path": file_path,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the query parameters.
        _query_params = {}
        if version_id is not None:
            _query_params["version_id"] = version_id
        if include_versions is not None:
            _query_params["include_versions"] = include_versions

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": DownloadFileResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/path/{file_path}",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def list_files(
        self,
        organisation_id: str,
        workspace_id: str,
        limit: int | None = None,
        offset: int | None = None,
        deleted: bool | None = None,
        author: str | None = None,
        file_name: str | None = None,
        created_at: list[str] | None = None,
        modified_by: str | None = None,
        modified_at: list[str] | None = None,
        deleted_by: str | None = None,
        deleted_at: list[str] | None = None,
        order_by: str | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> ListFilesResponse:  # noqa: F405
        """List folder contents

        Request to list files. The maximum number of results returned is limited to 5000.

        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param limit: (optional) The number of results to return.
            Example: `5000`
        :param offset: (optional) The number of results to skip.
            Example: `0`
        :param deleted: (optional) When true, only files that have been deleted will be returned
            Example: `False`
        :param author: (optional) The ID of the author to filter on.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param file_name: (optional) The name of the file to filter on. Will perform a case insensitive partial match, so the query `file_name=gold` will match a file with the name `allgoldcolumns.csv`.
            Example: `'drilling_data'`
        :param created_at: (optional) A date or dates (max 2) to filter files by. Dates may contain operator prefixes, in the form `<operator>:<datetime>`. The following operators are available (`lt`=less than, `lte`=less than or equal to, `gt`=greater than, `gte`=greater than or equal to).If you omit the operator, then it is assumed the operator is 'equal to'. In this case you may only supply one date. The dates must also be in a valid ISO 8601 format.Dates may include a UTC offset. If the offset is omitted, the timezone is assumed to be UTC.
            Example: `['gte:2023-03-10T22:56:53Z']`
        :param modified_by: (optional) The ID of the last person to modify the file to filter on.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param modified_at: (optional) A date or dates (max 2) to filter files by. Dates may contain operator prefixes, in the form `<operator>:<datetime>`. The following operators are available (`lt`=less than, `lte`=less than or equal to, `gt`=greater than, `gte`=greater than or equal to).If you omit the operator, then it is assumed the operator is 'equal to'. In this case you may only supply one date. The dates must also be in a valid ISO 8601 format.Dates may include a UTC offset. If the offset is omitted, the timezone is assumed to be UTC.
            Example: `['gte:2023-03-10T22:56:53Z']`
        :param deleted_by: (optional) The UUID of the user that deleted a file
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param deleted_at: (optional) A date or dates (max 2) to filter files by. Dates may contain operator prefixes, in the form `<operator>:<datetime>`. The following operators are available (`lt`=less than, `lte`=less than or equal to, `gt`=greater than, `gte`=greater than or equal to).If you omit the operator, then it is assumed the operator is 'equal to'. In this case you may only supply one date. The dates must also be in a valid ISO 8601 format.Dates may include a UTC offset. If the offset is omitted, the timezone is assumed to be UTC.
            Example: `['gte:2023-03-10T22:56:53Z']`
        :param order_by: (optional) A comma separated list of fields to order by, where the default sort order is ascending. To specify the sort order, prefix the field name with either `asc:` or `desc:` for ascending or descending respectively. Field names can be one of the following known sort fields: `created_at`, `modified_at`, `deleted_at`
            Example: `'order_by=modified_at,desc:created_at'`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the query parameters.
        _query_params = {}
        if limit is not None:
            _query_params["limit"] = limit
        if offset is not None:
            _query_params["offset"] = offset
        if deleted is not None:
            _query_params["deleted"] = deleted
        if author is not None:
            _query_params["author"] = author
        if file_name is not None:
            _query_params["file_name"] = file_name
        if created_at is not None:
            _query_params["created_at"] = created_at
        if modified_by is not None:
            _query_params["modified_by"] = modified_by
        if modified_at is not None:
            _query_params["modified_at"] = modified_at
        if deleted_by is not None:
            _query_params["deleted_by"] = deleted_by
        if deleted_at is not None:
            _query_params["deleted_at"] = deleted_at
        if order_by is not None:
            _query_params["order_by"] = order_by

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {
            "created_at": "multi",
            "modified_at": "multi",
            "deleted_at": "multi",
        }

        _response_types_map = {
            "200": ListFilesResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.GET,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def update_file_by_id(
        self,
        file_id: str,
        organisation_id: str,
        workspace_id: str,
        version_id: str | None = None,
        deleted: bool | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> UploadFileResponse | DownloadFileResponse:  # noqa: F405
        """Update a file

        Request an upload link for a new version of the specified file in blob storage. If the file does not exist an error will be returned. Follow up a successful request with a call to the returned pre-signed upload link. Specify a binary body containing the file to upload, with the addition of header key-value pair `x-ms-blob-type: BlockBlob` as required by the MS Azure documentation. The upload link is pre-signed and will expire after 30 minutes.  Including a `version_id` parameter allows creating a link to a blob with uncommitted blocks, i.e. the upload has not been completed properly, or the original pre-signed link has expired. Uncommitted blocks are valid for up to one week, after which they are automatically deleted.  Including a `deleted` parameter with a value of `false` will restore a deleted file.

        :param file_id:
            Format: `uuid`
            Example: `'file_id_example'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param version_id: (optional) (Optional) version ID to fetch a link for.
            Format: `int64`
            Example: `'1223372036854775807'`
        :param deleted: (optional) When set to false, the operation will attempt to restore a deleted file.
            Example: `True`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_id": file_id,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the query parameters.
        _query_params = {}
        if version_id is not None:
            _query_params["version_id"] = version_id
        if deleted is not None:
            _query_params["deleted"] = deleted

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": UploadFileResponse,  # noqa: F405
            "204": EmptyResponse,
            "303": DownloadFileResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.PUT,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/{file_id}",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )

    async def upsert_file_by_path(
        self,
        file_path: str,
        organisation_id: str,
        workspace_id: str,
        version_id: str | None = None,
        additional_headers: dict[str, str] | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> UploadFileResponse:  # noqa: F405
        """Upload a file

        Request an upload link to store the specified file in blob storage. If the folders in the file path do not exist, they will be created. If the file already exists, a new version will be created with the updated file content. Follow up a successful request with a call to the returned pre-signed upload link. Specify a binary body containing the file to upload, with the addition of header key-value pair `x-ms-blob-type: BlockBlob` as required by the MS Azure documentation. The upload link is pre-signed and will expire after 30 minutes.  Including a `version_id` parameter allows creating a link to a blob with uncommitted blocks, i.e. the upload has not been completed properly, or the original pre-signed link has expired. Uncommitted blocks are valid for up to one week, after which they are automatically deleted.

        :param file_path: Path to the file.
            Example: `'a/b/file.txt'`
        :param organisation_id: The customer's organisation organisation ID.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param workspace_id: The ID of the workspace in the organization.
            Format: `uuid`
            Example: `'00000000-0000-0000-0000-000000000000'`
        :param version_id: (optional) (Optional) version ID to fetch a link for.
            Format: `int64`
            Example: `'1223372036854775807'`
        :param additional_headers: (optional) Additional headers to send with the request.
        :param request_timeout: (optional) Timeout setting for this request. If one number is provided, it will be the
            total request timeout. It can also be a pair (tuple) of (connection, read) timeouts.

        :return: Returns the result object.

        :raise evo.common.exceptions.BadRequestException: If the server responds with HTTP status 400.
        :raise evo.common.exceptions.UnauthorizedException: If the server responds with HTTP status 401.
        :raise evo.common.exceptions.ForbiddenException: If the server responds with HTTP status 403.
        :raise evo.common.exceptions.NotFoundException: If the server responds with HTTP status 404.
        :raise evo.common.exceptions.BaseRFC87Error: If the server responds with any other HTTP status between
            400 and 599, and the body of the response conforms to RFC 87.
        :raise evo.common.exceptions.EvoApiException: If the server responds with any other HTTP status between 400
            and 599, and the body of the response does not conform to RFC 87.
        :raise evo.common.exceptions.UnknownResponseError: For other HTTP status codes with no corresponding response
            type in `response_types_map`.
        """
        # Prepare the path parameters.
        _path_params = {
            "file_path": file_path,
            "organisation_id": organisation_id,
            "workspace_id": workspace_id,
        }

        # Prepare the query parameters.
        _query_params = {}
        if version_id is not None:
            _query_params["version_id"] = version_id

        # Prepare the header parameters.
        _header_params = {
            "Accept": "application/json",
        }
        if additional_headers is not None:
            _header_params.update(additional_headers)

        # Define the collection formats.
        _collection_formats = {}

        _response_types_map = {
            "200": UploadFileResponse,  # noqa: F405
        }

        return await self.connector.call_api(
            method=RequestMethod.PUT,
            resource_path="/file/v2/orgs/{organisation_id}/workspaces/{workspace_id}/files/path/{file_path}",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            collection_formats=_collection_formats,
            response_types_map=_response_types_map,
            request_timeout=request_timeout,
        )
