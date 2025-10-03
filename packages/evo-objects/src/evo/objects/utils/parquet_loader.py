from __future__ import annotations

from io import BytesIO
from logging import getLogger
from typing import cast

from pydantic import TypeAdapter

from evo.common import ICache, IFeedback, ITransport
from evo.common.io import BytesDestination, ChunkedIOManager, Download, HTTPSource
from evo.common.utils import NoFeedback

from ..exceptions import SchemaValidationError
from . import ArrowTableFormat, KnownTableFormat
from .types import TableInfo

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    raise ImportError("The 'pyarrow' package is required to use ParquetLoader") from None

try:
    import pandas as pd
except ImportError:
    _PD_AVAILABLE = False
else:
    _PD_AVAILABLE = True

try:
    import numpy as np
except ImportError:
    _NP_AVAILABLE = False
else:
    _NP_AVAILABLE = True

__all__ = ["ParquetLoader"]

logger = getLogger(__name__)

_TABLE_INFO_ADAPTER: TypeAdapter[TableInfo] = TypeAdapter(TableInfo)


class ParquetLoader:
    """A loader for Parquet data from a geoscience object."""

    def __init__(
        self, download: Download, table_info: TableInfo, transport: ITransport, cache: ICache | None = None
    ) -> None:
        """
        :param download: The download information for the Parquet data.
        :param table_info: The expected table information for validation.
        :param transport: The transport to use for data downloads.
        :param cache: An optional cache to use for data downloads.
        """
        self._download = download
        validated_table_info = _TABLE_INFO_ADAPTER.validate_python(table_info)
        self._expected_format = KnownTableFormat.from_table_info(validated_table_info)
        self._expected_length = table_info["length"]
        self._transport = transport
        self._cache = cache

    async def _reader_from_cache(self, fb: IFeedback) -> pa.NativeFile:
        cached = await self._download.download_to_cache(self._cache, self._transport, fb=fb)
        return pa.OSFile(str(cached), "r")

    async def _reader_from_memory(self, fb: IFeedback) -> pa.NativeFile:
        # Initialize a buffer to store the downloaded data in memory
        memory = BytesIO()

        # Use ChunkedIOManager to download the data into the memory buffer
        manager = ChunkedIOManager()
        async with HTTPSource(self._download.get_download_url, self._transport) as source:
            destination = BytesDestination(memory)
            await manager.run(source, destination, fb=fb)

        # Reset the buffer's position to the beginning
        memory.seek(0)
        return pa.BufferReader(memory.getbuffer())

    async def _reader(self, fb: IFeedback) -> pa.NativeFile:
        if self._cache is not None:
            return await self._reader_from_cache(fb)
        else:
            return await self._reader_from_memory(fb)

    def _validate_data(self, data: pq.ParquetFile) -> None:
        logger.debug("Checking parquet data format")
        actual_format = ArrowTableFormat.from_schema(data.schema_arrow)
        KnownTableFormat._check_format(self._expected_format, actual_format)

        logger.debug("Checking parquet data length")
        actual_length = data.metadata.num_rows
        if self._expected_length != actual_length:
            raise SchemaValidationError(
                f"Row count ({actual_length}) does not match expectation ({self._expected_length})"
            )

        logger.debug("Parquet metadata checks succeeded")

    async def load_as_table(self, fb: IFeedback = NoFeedback) -> pa.Table:
        """Load the Parquet data as a PyArrow Table.

        :param fb: An optional feedback interface to report progress.

        :raises SchemaValidationError: If the data does not match the expected schema.
        """
        with await self._reader(fb) as reader:
            data = pq.ParquetFile(reader)
            self._validate_data(data)
            return data.read()

    if _PD_AVAILABLE:
        # Optional support for pandas dataframes

        async def load_as_dataframe(self, fb: IFeedback = NoFeedback) -> pd.DataFrame:
            """Load the Parquet data as a Pandas DataFrame.

            :param fb: An optional feedback interface to report progress.

            :raises SchemaValidationError: If the data does not match the expected schema.
            """
            table = await self.load_as_table(fb)
            return table.to_pandas()

    if _NP_AVAILABLE:
        # Optional support for numpy arrays

        async def load_as_array(self, fb: IFeedback = NoFeedback) -> np.ndarray:
            """Load the Parquet data as a NumPy array.

            The array will have a shape of (N,) for single-column data or (N, M) for multi-column data,
            where N is the number of rows and M is the number of columns. The target data _must_ have a uniform dtype.

            :param fb: An optional feedback interface to report progress.

            :raises SchemaValidationError: If the data does not match the expected schema.
            """
            try:
                dtype = np.dtype(self._expected_format.data_type)
            except TypeError:
                raise SchemaValidationError(
                    f"Unsupported data type '{self._expected_format.data_type}' cannot be loaded as a numpy array"
                )

            table = await self.load_as_table(fb)
            columns = cast(list[np.ndarray], [col.combine_chunks().to_numpy() for col in table.itercolumns()])
            if len(columns) == 1:
                return columns[0].astype(dtype)
            else:
                return np.column_stack(columns).astype(dtype)
