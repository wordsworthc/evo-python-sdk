from __future__ import annotations

from typing import TypeVar
from uuid import UUID

from ._types import DataType
from .endpoints import models
from .endpoints.models import JobResponse
from .exceptions import UnknownJobPayload

T = TypeVar("T")


def extract_payload(job_id: UUID, job_response: JobResponse, payload_type: type[T]) -> T:
    payload = job_response.payload
    if isinstance(payload, payload_type):
        return payload
    else:
        raise UnknownJobPayload(
            job_id, f"Expected {payload_type.__name__} for job payload, got {type(payload).__name__} instead"
        )


try:
    import pyarrow
except ImportError:
    data_type_mapping = {}
else:
    data_type_mapping = {
        pyarrow.bool_(): models.DataType.Boolean,
        pyarrow.int8(): models.DataType.Int8,
        pyarrow.int16(): models.DataType.Int16,
        pyarrow.int32(): models.DataType.Int32,
        pyarrow.int64(): models.DataType.Int64,
        pyarrow.uint8(): models.DataType.UInt8,
        pyarrow.uint16(): models.DataType.UInt16,
        pyarrow.uint32(): models.DataType.UInt32,
        pyarrow.uint64(): models.DataType.UInt64,
        pyarrow.float16(): models.DataType.Float16,
        pyarrow.float32(): models.DataType.Float32,
        pyarrow.float64(): models.DataType.Float64,
        pyarrow.utf8(): models.DataType.Utf8,
        pyarrow.date32(): models.DataType.Date32,
        pyarrow.timestamp("us", tz="UTC"): models.DataType.Timestamp,
    }


def convert_dtype(data_type: DataType) -> models.DataType:
    try:
        return data_type_mapping[data_type]
    except KeyError:
        raise ValueError(f"Unsupported data type: {data_type}")
