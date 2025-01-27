from ..exceptions import EvoClientException

__all__ = [
    "ChunkedIOException",
    "ChunkedIOError",
    "RenewalError",
    "RenewalTimeoutError",
]


class ChunkedIOException(EvoClientException):
    """Base exception for unrecoverable errors that are expected within io.

    These exceptions should be caught by client code.
    """


class ChunkedIOError(ChunkedIOException):
    """Base exception for recoverable errors that are handled within chunked_io.

    All ChunkedIOError subtypes are considered recoverable and should implement a recover() method that prepares the
    [`ISource`][evo.common.io.interfaces.ISource] or [`IDestination`][evo.common.io.interfaces.IDestination] that raised
    the error for a retry attempt.

    :ivar raised_by: The source or destination that raised the exception.
    """

    def __init__(self, message: str) -> None:
        """
        :param message: The error message.
        """
        super().__init__(message)

    async def recover(self) -> bool:
        """Run the steps required to recover from the original error and prepare for a retry attempt."""
        return False  # ChunkedIOError is not recoverable by default.


class RenewalError(EvoClientException):
    """RenewalError is raised when renewing the url fails."""


class RenewalTimeoutError(RenewalError):
    """RenewalTimeoutError is raised when an attempt to renew a url is made within a specified threshold."""


class BlobExistsError(EvoClientException):
    """Raised when requesting an upload url for a binary resource that already exists in the target service."""


class BlobNotFoundError(EvoClientException):
    """Raised when requesting a download url for a binary resource that does not exist in the target service."""
