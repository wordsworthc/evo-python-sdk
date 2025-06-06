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

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Sequence
from pathlib import PurePosixPath
from uuid import UUID

from evo import logging
from evo.common import APIConnector, BaseAPIClient, HealthCheckType, ICache, Page, ServiceHealth
from evo.common.data import Environment
from evo.common.io.exceptions import DataNotFoundError
from evo.common.utils import get_service_health
from evo.workspaces import ServiceUser

from .data import ObjectMetadata, ObjectSchema, ObjectVersion
from .endpoints import ObjectsApi
from .endpoints.models import (
    GeoscienceObject,
    GeoscienceObjectVersion,
    GetObjectResponse,
    ListedObject,
    PostObjectResponse,
    UpdateGeoscienceObject,
)
from .exceptions import ObjectUUIDError
from .io import ObjectDataDownload, ObjectDataUpload
from .utils import ObjectDataClient

logger = logging.getLogger("object.client")

__all__ = [
    "DownloadedObject",
    "ObjectAPIClient",
]


def _version_from_listed_version(model: GeoscienceObjectVersion) -> ObjectVersion:
    """Create an ObjectVersion instance from a generated ListedObject model.

    :param model: The model to create the ObjectVersion instance from.

    :return: An ObjectVersion instance.
    """
    created_by = None if model.created_by is None else ServiceUser.from_model(model.created_by)  # type: ignore
    return ObjectVersion(
        version_id=model.version_id,
        created_at=model.created_at,
        created_by=created_by,
    )


class DownloadedObject:
    """A downloaded geoscience object."""

    def __init__(
        self, object_: GeoscienceObject, metadata: ObjectMetadata, urls_by_name: dict[str, str], connector: APIConnector
    ) -> None:
        self._object = object_
        self._metadata = metadata
        self._urls_by_name = urls_by_name
        self._connector = connector

    @property
    def schema(self) -> ObjectSchema:
        """The schema of the object."""
        return self._metadata.schema_id

    @property
    def metadata(self) -> ObjectMetadata:
        """The metadata of the object."""
        return self._metadata

    def as_dict(self) -> dict:
        """Get this object as a dictionary."""
        return self._object.model_dump(mode="python", by_alias=True)

    def prepare_data_download(self, data_identifiers: Sequence[str | UUID]) -> Iterator[ObjectDataDownload]:
        """Prepare to download multiple data files from the geoscience object service, for this object.

        Any data IDs that are not associated with the requested object will raise a DataNotFoundError.

        :param data_identifiers: A list of sha256 digests or UUIDs for the data to be downloaded.

        :return: An iterator of data download contexts that can be used to download the data.

        :raises DataNotFoundError: If any requested data ID is not associated with this object.
        """
        try:
            filtered_urls_by_name = {str(name): self._urls_by_name[str(name)] for name in data_identifiers}
        except KeyError as exc:
            raise DataNotFoundError(f"Unable to find the requested data: {exc.args[0]}") from exc
        for ctx in ObjectDataDownload._create_multiple(
            connector=self._connector, metadata=self._metadata, urls_by_name=filtered_urls_by_name
        ):
            yield ctx


class ObjectAPIClient(BaseAPIClient):
    def __init__(self, environment: Environment, connector: APIConnector) -> None:
        super().__init__(environment, connector)
        self._objects_api = ObjectsApi(connector=connector)

    async def get_service_health(self, check_type: HealthCheckType = HealthCheckType.FULL) -> ServiceHealth:
        """Get the health of the geoscience object service.

        :param check_type: The type of health check to perform.

        :return: A ServiceHealth object.

        :raises EvoAPIException: If the API returns an unexpected status code.
        :raises ClientValueError: If the response is not a valid service health check response.
        """
        return await get_service_health(self._connector, "geoscience-object", check_type=check_type)

    def _metadata_from_listed_object(self, model: ListedObject) -> ObjectMetadata:
        """Create an ObjectMetadata instance from a generated ListedObject model.

        :param model: The model to create the ObjectMetadata instance from.

        :return: An ObjectMetadata instance.
        """
        created_by = None if model.created_by is None else ServiceUser.from_model(model.created_by)
        modified_by = None if model.modified_by is None else ServiceUser.from_model(model.modified_by)
        return ObjectMetadata(
            environment=self._environment,
            id=model.object_id,
            name=model.name,
            created_at=model.created_at,
            created_by=created_by,
            modified_at=model.modified_at,
            modified_by=modified_by,
            parent=model.path.rstrip("/"),
            schema_id=ObjectSchema.from_id(model.schema_),
            version_id=model.version_id,
        )

    def _metadata_from_endpoint_model(self, model: GetObjectResponse | PostObjectResponse) -> ObjectMetadata:
        """Create an ObjectMetadata instance from a generated GetObjectResponse or PostObjectResponse model.

        :param model: The model to create the ObjectMetadata instance from.

        :return: An ObjectMetadata instance.
        """
        object_path = PurePosixPath(model.object_path)
        created_by = None if model.created_by is None else ServiceUser.from_model(model.created_by)
        modified_by = None if model.modified_by is None else ServiceUser.from_model(model.modified_by)
        return ObjectMetadata(
            environment=self._environment,
            id=model.object_id,
            name=object_path.name,
            created_at=model.created_at,
            created_by=created_by,
            modified_at=model.modified_at,
            modified_by=modified_by,
            parent=str(object_path.parent),
            schema_id=ObjectSchema.from_id(model.object.schema_),
            version_id=model.version_id,
        )

    async def list_objects(self, offset: int = 0, limit: int = 5000) -> Page[ObjectMetadata]:
        """List up to `limit` geoscience objects, starting at `offset`.

        The geoscience objects will be the latest version of the object.
        If there are no objects to list, the page will be empty.

        :param offset: The number of objects to skip before listing.
        :param limit: Max number of objects to list.

        :return: A page of all objects from the query.
        """
        assert limit > 0
        assert offset >= 0
        response = await self._objects_api.list_objects(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            limit=limit,
            offset=offset,
        )
        return Page(
            offset=offset,
            limit=limit,
            total=response.total,
            items=[self._metadata_from_listed_object(model) for model in response.objects],
        )

    async def list_all_objects(self, limit_per_request: int = 5000) -> list[ObjectMetadata]:
        """List all geoscience objects in the workspace.

        This method makes multiple calls to the `list_objects` endpoint until all objects have been listed.

        :param limit_per_request: The maximum number of objects to list in one request.

        :return: A list of all objects in the workspace.
        """
        items = []
        offset = 0
        while True:
            page = await self.list_objects(offset=offset, limit=limit_per_request)
            items += page.items()
            if page.is_last:
                break
            offset = page.next_offset
        return items

    @staticmethod
    def _get_object_versions(response: GetObjectResponse) -> list[ObjectVersion]:
        object_versions = [_version_from_listed_version(model) for model in response.versions]
        return sorted(object_versions, key=lambda v: v.created_at, reverse=True)

    async def list_versions_by_path(self, path: str) -> list[ObjectVersion]:
        """List all version for the given object.

        :param path: The path to the geoscience object.

        :return: A sorted list of object versions. The latest version is the first element of the list.
        """
        response = await self._objects_api.get_object(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            objects_path=path,
            include_versions=True,
        )
        return self._get_object_versions(response)

    async def list_versions_by_id(self, object_id: UUID) -> list[ObjectVersion]:
        """List all version for the given object.

        :param object_id: The UUID of the geoscience object.

        :return: A sorted list of object versions. The latest version is the first element of the list.
        """
        response = await self._objects_api.get_object_by_id(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            object_id=str(object_id),
            include_versions=True,
        )
        return self._get_object_versions(response)

    async def prepare_data_upload(self, data_identifiers: Sequence[str | UUID]) -> AsyncIterator[ObjectDataUpload]:
        """Prepare to upload multiple data files to the geoscience object service.

        Referenced data that already exists in the workspace will be skipped.

        :param data_identifiers: A list of sha256 digests or UUIDs for the data to be uploaded.

        :return: An async iterator of data upload contexts that can be used to upload the data. Data identifiers
            that already exist in the workspace will be skipped.
        """
        async for ctx in ObjectDataUpload._create_multiple(
            connector=self._connector,
            environment=self._environment,
            names=data_identifiers,
        ):
            yield ctx

    async def prepare_data_download(
        self, object_id: UUID, version_id: str, data_identifiers: Sequence[str | UUID]
    ) -> AsyncIterator[ObjectDataDownload]:
        """Prepare to download multiple data files from the geoscience object service.

        Any data IDs that are not associated with the requested object will raise a DataNotFoundError.

        :param object_id: The ID of the object to download data from.
        :param version_id: The version ID of the object to download data from.
        :param data_identifiers: A list of sha256 digests or UUIDs for the data to be downloaded.

        :return: An async iterator of data download contexts that can be used to download the data.

        :raises DataNotFoundError: If any requested data ID is not associated with the referenced object.
        """
        downloaded_object = await self.download_object_by_id(object_id, version=version_id)
        for ctx in downloaded_object.prepare_data_download(data_identifiers):
            yield ctx

    def get_data_client(self, cache: ICache) -> ObjectDataClient:
        """Get a data client for the geoscience object service.

        The data client provides a high-level interface for uploading and downloading data that is referenced in
        geoscience objects, and caching the data locally. It depends on the optional dependency `pyarrow`, which is
        not installed by default. This dependency can be installed with `pip install evo-objects[utils]`.

        :param cache: The cache to use for data downloads.

        :return: An ObjectDataClient instance.

        :raises RuntimeError: If the `pyarrow` package is not installed.
        """
        return ObjectDataClient(environment=self._environment, connector=self._connector, cache=cache)

    async def create_geoscience_object(self, path: str, object_dict: dict) -> ObjectMetadata:
        """Upload a new geoscience object to the geoscience object service.

        New geoscience objects must not have a UUID, so that one can be assigned by the Geoscience Object Service.
        The `object_instance` that is passed in will be updated with the service-assigned UUID after it has been
        uploaded, and the metadata of the created object will be returned.

        :param path: The path to upload the object to.
        :param object_dict: The geoscience object to be uploaded.

        :return: The metadata of the uploaded object.

        :raises ObjectUUIDError: If the provided object has a UUID.
        """
        if object_dict.get("uuid") is not None:
            raise ObjectUUIDError("Object has a UUID but new objects should have None")
        object_for_upload = GeoscienceObject.model_validate(object_dict)

        result = await self._objects_api.post_objects(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            objects_path=path,
            geoscience_object=object_for_upload,
        )
        object_dict["uuid"] = result.object_id
        return self._metadata_from_endpoint_model(result)

    async def move_geoscience_object(self, path: str, object_dict: dict) -> ObjectMetadata:
        """Move an existing geoscience object to a new path in the geoscience object service.

        :param path: The new path to move the object to.
        :param object_dict: The geoscience object to be moved.

        :return: The metadata of the moved object.

        :raises ObjectUUIDError: If the provided object does not have a UUID.
        """
        if object_dict.get("uuid") is None:
            raise ObjectUUIDError("Object does not have a UUID")
        object_for_upload = GeoscienceObject.model_validate(object_dict)

        result = await self._objects_api.post_objects(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            objects_path=path,
            geoscience_object=object_for_upload,
        )
        return self._metadata_from_endpoint_model(result)

    async def update_geoscience_object(self, object_dict: dict) -> ObjectMetadata:
        """Update an existing geoscience object in the geoscience object service.

        :param object_dict: The geoscience object to be updated.

        :return: The metadata of the updated object.

        :raises ObjectUUIDError: If the provided object does not have a UUID.
        """
        if object_dict.get("uuid") is None:
            raise ObjectUUIDError("Object does not have a UUID")
        object_for_upload = UpdateGeoscienceObject.model_validate(object_dict)

        result = await self._objects_api.update_objects_by_id(
            object_id=str(object_for_upload.uuid),
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            update_geoscience_object=object_for_upload,
        )
        return self._metadata_from_endpoint_model(result)

    def _downloaded_object_from_response(self, response: GetObjectResponse) -> DownloadedObject:
        """Parse object metadata and a geoscience object model instance from a get object response

        :param response: The response from one of the get object endpoints.

        :return: A tuple containing the object metadata and a data model of the requested geoscience object.
        """
        metadata = self._metadata_from_endpoint_model(response)
        urls_by_name = {getattr(link, "name", link.id): link.download_url for link in response.links.data}
        return DownloadedObject(response.object, metadata, urls_by_name, self._connector)

    async def download_object_by_path(self, path: str, version: str | None = None) -> DownloadedObject:
        """Download a geoscience object definition (by path).

        :param path: The path to the geoscience object.
        :param version: The version of the geoscience object to download. This will download the latest version by
            default.

        :return: A tuple containing the object metadata and a data model of the requested geoscience object.
        """
        response = await self._objects_api.get_object(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            objects_path=path,
            version=version,
            additional_headers={"Accept-Encoding": "gzip"},
        )
        return self._downloaded_object_from_response(response)

    async def download_object_by_id(self, object_id: UUID, version: str | None = None) -> DownloadedObject:
        """Download a geoscience object definition (by UUID).

        :param object_id: The uuid of the geoscience object.
        :param version: The version of the geoscience object to download. This will download the latest version by
            default.

        :return: A tuple containing the object metadata and a data model of the requested geoscience object.
        """
        response = await self._objects_api.get_object_by_id(
            org_id=str(self._environment.org_id),
            workspace_id=str(self._environment.workspace_id),
            object_id=str(object_id),
            version=version,
            additional_headers={"Accept-Encoding": "gzip"},
        )
        return self._downloaded_object_from_response(response)

    async def get_latest_object_versions(self, object_ids: list[UUID], batch_size: int = 500) -> dict[UUID, str]:
        """Get the latest version of each object by uuid.

        :param object_ids: A list of object uuids.
        :param batch_size: The maximum number of objects to check in one API call (max 500).

        :return: A mapping of uuids to the latest version id.
        """
        offset = 0
        n_objects = len(object_ids)
        latest_ids: dict[UUID, str] = {}
        while batch_object_ids := object_ids[offset : min(offset + batch_size, n_objects)]:
            offset += batch_size
            response = await self._objects_api.list_object_version_ids(
                org_id=str(self._environment.org_id),
                workspace_id=str(self._environment.workspace_id),
                request_body=[str(object_id) for object_id in batch_object_ids],
            )
            latest_ids.update({UUID(latest.object_id): latest.version_id for latest in response})
        return latest_ids
