from pure_interface import Interface

__all__ = [
    "IDestination",
    "ISource",
]


class IDestination(Interface):
    """A local or remote destination for managed file IO.

    IDestination implementations should raise a subtype of ChunkedIOError when a recoverable error occurs. The specific
    error will depend on the implementation and must be capable of recovering the IDestination from the failure state.
    """

    async def write_chunk(self, offset: int, data: bytes) -> None:
        """Write raw data to the destination at the provided offset"""


class ISource(Interface):
    """A local or remote source for managed file IO.

    ISource implementations should raise a subtype of ChunkedIOError when a recoverable error occurs. The specific
    error will depend on the implementation and must be capable of recovering the ISource from the failure state.
    """

    async def get_size(self) -> int:
        """Get the size of the source data"""

    async def read_chunk(self, offset: int, length: int) -> bytes:
        """Read <length> bytes of raw data from the source, starting at the given offset"""
