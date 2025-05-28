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

import os
from abc import ABC, abstractmethod
from typing import BinaryIO

from evo import logging

from .._types import PathLike, resolve_path
from ..interfaces import IFeedback, ITransport
from ..utils import NoFeedback, Retry
from .bytes import BytesSource
from .chunked_io_manager import DEFAULT_CHUNK_SIZE, ChunkedIOManager
from .exceptions import ChunkedIOError
from .interfaces import ISource
from .storage import StorageDestination

logger = logging.getLogger("io.upload")


class Upload(ABC):
    """A base class for referencing binary data that needs to be uploaded.

    Each SDK that accepts binary data from an API is expected to extend this class, providing the specific implementation
    for generating upload URLs.
    """

    @property
    @abstractmethod
    def label(self) -> str:
        """The label of the resource to be uploaded."""
        ...

    @abstractmethod
    async def get_upload_url(self) -> str:
        """Generate a URL that will be used to upload the resource.

        This method may be called multiple times to generate a new URL if the last URL expires.

        :returns: The upload URL.

        :raises DataExistsError: if the resource already exists.
        """
        ...

    def destination(self, transport: ITransport) -> StorageDestination:
        """Create a StorageDestination for manually uploading binary data.

        :param transport: The transport to use for the API calls.

        :returns: A StorageDestination instance that can be used to upload data.
        """
        return StorageDestination(url_callback=self.get_upload_url, transport=transport)

    async def upload_from_source(
        self,
        source: ISource,
        transport: ITransport,
        max_workers: int | None = None,
        retry: Retry | None = None,
        fb: IFeedback = NoFeedback,
    ) -> None:
        """Upload data from the provided ISource implementation.

        :param source: An ISource instance to upload data from.
        :param transport: The transport to use for the API calls.
        :param max_workers: The maximum number of concurrent connections to use for data transfer. If None, the default
            is `min(32, os.cpu_count() + 4)`
        :param retry: A Retry object with a wait strategy. If None, a default Retry is created. If a chunk is successfully
            transferred the attempt counter will be reset.
        :param fb: feedback to track the upload, by tracking reads from the file only

        :raises ChunkedIOException: if a non-recoverable exception occurred.
        :raises RetryError: if the maximum number of consecutive attempts have failed. RetryError is a subclass
            of ChunkedIOException.
        """
        logger.debug(f"Attempting to upload data (label: {self.label})")

        if retry is None:
            retry = Retry(logger=logger)

        manager = ChunkedIOManager(message="Uploading", retry=retry, max_workers=max_workers)
        async with self.destination(transport=transport) as destination:
            await manager.run(source, destination, fb)
            await destination.commit(retry=retry)

        logger.debug(f"Data uploaded successfully (label: {self.label})")

    async def upload_from_bytes(
        self,
        data: BinaryIO,
        transport: ITransport,
        max_workers: int | None = None,
        retry: Retry | None = None,
        fb: IFeedback = NoFeedback,
    ) -> None:
        """Upload data from a readable and seekable binary stream.

        :param stream: A readable and seekable binary stream to upload data from.
        :param transport: The transport to use for the API calls.
        :param max_workers: The maximum number of concurrent connections to use for data transfer. If None, the default
            is `min(32, os.cpu_count() + 4)`
        :param retry: A Retry object with a wait strategy. If None, a default Retry is created. If a chunk is successfully
            transferred the attempt counter will be reset.
        :param fb: feedback to track the upload, by tracking reads from the file only

        :raises ChunkedIOException: if a non-recoverable exception occurred.
        :raises RetryError: if the maximum number of consecutive attempts have failed. RetryError is a subclass
            of ChunkedIOException.
        """
        return await self.upload_from_source(
            source=BytesSource(data),  # BytesSource will determine the size of the stream by seeking to the end.
            transport=transport,
            max_workers=max_workers,
            retry=retry,
            fb=fb,
        )

    async def upload_from_path(
        self,
        filename: PathLike,
        transport: ITransport,
        max_workers: int | None = None,
        retry: Retry | None = None,
        fb: IFeedback = NoFeedback,
    ) -> None:
        """Upload a file with the given filename.

        :param filename: file to upload
        :param transport: The transport to use for the API calls.
        :param max_workers: The maximum number of concurrent connections to use for data transfer. If None, the default
            is `min(32, os.cpu_count() + 4)`
        :param retry: A Retry object with a wait strategy. If None, a default Retry is created. If a chunk is successfully
            transferred the attempt counter will be reset.
        :param fb: feedback to track the upload, by tracking reads from the file only

        :raises ValueError: if the file to upload does not exist
        :raises ChunkedIOException: if a non-recoverable exception occurred.
        :raises RetryError: if the maximum number of consecutive attempts have failed. RetryError is a subclass
            of ChunkedIOException.
        """
        src_path = resolve_path(filename)

        if not src_path.is_file():
            raise ValueError(f"file {src_path} does not exist")

        size = os.path.getsize(src_path)
        with src_path.open("rb") as input_:
            source = BytesSource(input_, size)
            return await self.upload_from_source(
                source=source,
                transport=transport,
                max_workers=max_workers,
                retry=retry,
                fb=fb,
            )

    async def stream_upload(
        self,
        stream: BinaryIO,
        transport: ITransport,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        retry: Retry | None = None,
    ) -> None:
        """Upload data from a readable binary stream.

        This is generally less performant than using `upload_from_source`, because it reads the stream synchronously
        and sequentially. Where possible, prefer using other upload methods that make use of the parallelism provided by
        `ChunkedIOManager`.

        :param stream: A readable binary stream to upload data from.
        :param transport: The transport to use for the API calls.
        :param chunk_size: The maximum size of each chunk to be transferred. The final chunk will usually be smaller
            than the chunk_size.
        :param retry: A Retry object with a wait strategy. If None, a default Retry is created. If a chunk is successfully
            transferred the attempt counter will be reset.

        :raises ChunkedIOException: if a non-recoverable exception occurred.
        :raises RetryError: if the maximum number of consecutive attempts have failed. RetryError is a subclass
            of ChunkedIOException.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")

        if chunk_size > 1024 * 1024 * 4000:
            raise ValueError("chunk_size must not exceed 4000 MiB (4000 * 1024 * 1024 bytes)")

        if retry is None:
            retry = Retry(logger=logger)

        # This is basically a minimal re-implementation of `ChunkedIOManager.run` for uploading from a stream, where
        # we must read chunks synchronously and sequentially.
        async with self.destination(transport=transport) as destination:
            offset = 0
            while chunk := stream.read(chunk_size):
                async for handler in retry:
                    with handler.suppress_errors(ChunkedIOError):
                        await destination.write_chunk(offset, chunk)
                        offset += len(chunk)

                    # Attempt to recover from a ChunkedIOError if it occurs.
                    if isinstance(handler.exception, ChunkedIOError) and not await handler.exception.recover():
                        # If the error cannot be recovered, raise it.
                        raise handler.exception
