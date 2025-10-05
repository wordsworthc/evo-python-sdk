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

from collections.abc import Iterator, Sequence
from uuid import UUID

from evo import logging
from evo.common import APIConnector, ICache
from evo.common.io.exceptions import DataNotFoundError

from ..data import ObjectMetadata, ObjectReference, ObjectSchema
from ..endpoints import ObjectsApi, models
from ..io import ObjectDataDownload
from . import parse

__all__ = ["DownloadedObject"]

logger = logging.getLogger("object.client")


class DownloadedObject:
    """A downloaded geoscience object."""

    def __init__(
        self,
        object_: models.GeoscienceObject,
        metadata: ObjectMetadata,
        urls_by_name: dict[str, str],
        connector: APIConnector,
        cache: ICache | None = None,
    ) -> None:
        """
        :param object_: The raw geoscience object model.
        :param metadata: The parsed metadata for the object.
        :param urls_by_name: A mapping of data names to their initial download URLs.
        :param connector: The API connector to use for downloading data.
        :param cache: An optional cache to use for data downloads.
        """
        self._object = object_
        self._metadata = metadata
        self._urls_by_name = urls_by_name
        self._connector = connector
        self._cache = cache

    @staticmethod
    async def from_reference(
        connector: APIConnector,
        reference: ObjectReference | str,
        cache: ICache | None = None,
        request_timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> DownloadedObject:
        """Download a geoscience object from the service, given an object reference.

        :param connector: The API connector to use for downloading data.
        :param reference: The reference to the object to download, or a URL as a string that can be parsed into
            a reference.
        :param cache: An optional cache to use for data downloads.
        :param request_timeout: An optional timeout to use for API requests. See evo.common.APIConnector for details.

        :raises ValueError: If the reference is invalid, or if the connector base URL does not match the reference hub URL.
        """
        ref = ObjectReference(reference)  # Parse the reference if it's a string

        if connector.base_url != ref.hub_url:
            raise ValueError(
                f"The connector base URL '{connector.base_url}' does not match the reference hub URL '{ref.hub_url}'"
            )

        api = ObjectsApi(connector)

        request_kwargs = dict(
            org_id=str(ref.org_id),
            workspace_id=str(ref.workspace_id),
            version=ref.version_id,
            additional_headers={"Accept-Encoding": "gzip"},
            request_timeout=request_timeout,
        )

        if ref.object_id is not None and ref.object_path is not None:
            raise ValueError("Only one of object_id or object_path should be provided")

        if ref.object_id is not None:
            response = await api.get_object_by_id(object_id=ref.object_id, **request_kwargs)
        elif ref.object_path is not None:
            response = await api.get_object(objects_path=ref.object_path, **request_kwargs)
        else:
            raise ValueError("Either object_id or object_path must be provided")

        metadata = parse.object_metadata(response, ref.environment)
        urls_by_name = {getattr(link, "name", link.id): link.download_url for link in response.links.data}
        return DownloadedObject(
            object_=response.object,
            metadata=metadata,
            urls_by_name=urls_by_name,
            connector=connector,
            cache=cache,
        )

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
