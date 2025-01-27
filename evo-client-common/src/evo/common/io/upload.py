from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager

from evo import logging

from .._types import PathLike
from ..interfaces import IFeedback, ITransport
from ..utils import NoFeedback, Retry
from .azure import BlobStorageDestination

logger = logging.getLogger("io.upload")


class Upload(ABC):
    """A base class for referencing binary data that needs to be uploaded.

    Each service that accepts binary data is expected to extend this class, providing the specific implementation
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

        :raises BlobExistsError: if the resource already exists in the target service.
        """
        ...

    @contextmanager
    def _uploading(self) -> Iterator[None]:
        """A context manager that logs the start and end of the upload process."""
        logger.debug(f"Attempting to upload data (label: {self.label})")
        yield
        logger.debug(f"Data uploaded successfully (label: {self.label})")

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
        with self._uploading():
            await BlobStorageDestination.upload_file(
                filename=filename,
                url_generator=self.get_upload_url,
                transport=transport,
                max_workers=max_workers,
                retry=retry,
                fb=fb,
            )
