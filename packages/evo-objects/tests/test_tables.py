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

import hashlib
import random
import unittest
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from unittest import mock
from uuid import UUID

import numpy
import pyarrow as pa
import pyarrow.parquet as pq
from parameterized import parameterized, parameterized_class

from evo.common import Environment
from evo.common.test_tools import BASE_URL
from evo.common.utils import Cache
from evo.objects.exceptions import SchemaValidationError, TableFormatError
from evo.objects.utils import (
    ArrowTableFormat,
    BaseTableFormat,
    KnownTableFormat,
    all_known_formats,
    get_known_format,
)
from evo.objects.utils.tables import _ColumnFormat

SAMPLE_DATA_LENGTH = 10
ENVIRONMENT = Environment(hub_url=BASE_URL, org_id=UUID(int=0), workspace_id=UUID(int=0))
CACHE: Cache


def tearDownModule() -> None:
    """Fail-safe cleanup of the cache directory."""
    CACHE.clear_cache()
    CACHE.root.rmdir()


def setUpModule() -> None:
    cache_dir = Path(__file__).parent.resolve() / f".{__name__.lower()}_cache"
    global CACHE
    CACHE = Cache(cache_dir, mkdir=True)
    unittest.addModuleCleanup(tearDownModule)

    # Write gitignore file in case cleanup fails.
    gitignore_file = cache_dir / ".gitignore"
    gitignore_file.write_text("*\n", encoding="utf-8")


def _all_known_formats_for_testing() -> Iterator[dict]:
    for known_format in all_known_formats:
        yield {"data_format": known_format, "expected_field_names": known_format._field_names}


def _generate_float64_data(n_samples: int) -> Iterator[float]:
    max_ = numpy.finfo("float64").max
    for _ in range(n_samples):
        yield max_ * random.uniform(-1.0, 1.0)


def _generate_int_data(int_type: str, n_samples: int) -> Iterator[int]:
    min_, max_ = numpy.iinfo(int_type).min, numpy.iinfo(int_type).max
    for _ in range(n_samples):
        yield random.randint(min_, max_)


def _generate_bool_data(n_samples: int) -> Iterator[bool]:
    for _ in range(n_samples):
        yield random.choice((True, False))


def _generate_string_data(n_samples: int) -> Iterator[str]:
    str_sample = "0123456789ABCDEF "
    for _ in range(n_samples):
        length = random.randint(10, 10000)
        yield "".join(random.choices(str_sample, k=length))


def _generate_timestamp_data(n_samples: int) -> Iterator[datetime]:
    min_ = datetime(1970, 1, 1, tzinfo=timezone.utc).timestamp()
    max_ = datetime(2038, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc).timestamp()
    for _ in range(n_samples):
        yield datetime.utcfromtimestamp(random.uniform(min_, max_))


def _generate_data(format_id: str, n_samples: int) -> Iterator:
    match format_id:
        case "float64":
            yield from _generate_float64_data(n_samples)
        case "uint8" | "uint32" | "uint64" | "int32" | "int64" as int_type:
            yield from _generate_int_data(int_type, n_samples)
        case "bool":
            yield from _generate_bool_data(n_samples)
        case "string":
            yield from _generate_string_data(n_samples)
        case "timestamp":
            yield from _generate_timestamp_data(n_samples)
        case unknown_format:
            raise TypeError(f"Unsupported format '{unknown_format}'")


def _get_sample_column(column_format: _ColumnFormat, n_samples: int) -> pa.Array:
    return pa.array(_generate_data(column_format.id, n_samples), type=column_format.type, size=n_samples)


def _get_table_schema(columns: list[_ColumnFormat]) -> pa.Schema:
    return pa.schema([pa.field(f"{column.id}[{i}]", column.type, nullable=False) for i, column in enumerate(columns)])


def _change_format(current_format: _ColumnFormat) -> _ColumnFormat:
    match current_format.id:
        case "float64":
            return _ColumnFormat("int64")
        case "uint8" | "uint32" | "uint64" | "int32" | "int64":
            return _ColumnFormat("float64")
        case "bool" | "timestamp":
            return _ColumnFormat("string")
        case "string":
            return _ColumnFormat("bool")
        case unknown_format:
            raise TypeError(f"Unsupported format '{unknown_format}'")


def _get_sample_table(
    table_format: BaseTableFormat, n_rows: int, add_column: bool = False, change_types: bool = False
) -> pa.Table:
    column_formats = [column for column in table_format._columns]

    if add_column:
        column_formats.append(_ColumnFormat(column_formats[-1].type))

    if change_types:
        column_formats = [_change_format(column) for column in column_formats]

    if table_format._multi_dimensional:
        # Test multidimensional tables with an arbitrary number of columns. If the number of columns matches a more
        # specific GO type (one with a fixed number of columns), the more specific type would be instantiated.
        column_formats *= 20

    sample_schema = pa.schema(
        [pa.field(f"{column.id}[{i}]", column.type, nullable=False) for i, column in enumerate(column_formats)]
    )
    sample_data = [
        pa.array(_generate_data(column_format.id, n_rows), type=column_format.type, size=n_rows)
        for column_format in column_formats
    ]
    return pa.table(sample_data, names=sample_schema.names).cast(sample_schema)


def _get_buffer_digest(buffer: BinaryIO) -> str:
    """Return a sha256 digest of a binary buffer"""
    buffer.seek(0)
    file_hash = hashlib.sha256()
    while next_block := buffer.read(4 * 1024 * 1024):
        file_hash.update(next_block)
    return file_hash.hexdigest()


def _get_table_digest(table: pa.Table) -> str:
    """return a sha256 digest of a pyarrow.Table saved in parquet format"""
    buffer = BytesIO()
    pq.write_table(table=table, where=buffer, version="2.4", compression="gzip")
    return _get_buffer_digest(buffer=buffer)


def _test_name_from_known_format(cls: type, num: int, params_dict: dict) -> str:
    """Create parameterized test name from DataFormat"""
    data_format = params_dict["data_format"]
    return parameterized.to_safe_name(f"{cls.__name__}_{num}_{data_format.name}")


@parameterized_class(_all_known_formats_for_testing(), class_name_func=_test_name_from_known_format)
class TestKnownFormat(unittest.TestCase):
    data_format: KnownTableFormat
    expected_field_names: str

    def setUp(self) -> None:
        self.sample_table = _get_sample_table(table_format=self.data_format, n_rows=SAMPLE_DATA_LENGTH)
        self.expected_parquet_digest = _get_table_digest(self.sample_table)
        self.data_dir = CACHE.get_location(ENVIRONMENT, self.__class__.__name__)
        self.parquet_file = self.data_dir / self.expected_parquet_digest

    def tearDown(self) -> None:
        self.parquet_file.unlink(missing_ok=True)

    def test_unknown_format(self) -> None:
        all_other_formats = [other for other in all_known_formats if not other.is_provided_by(self.data_format)]
        with (
            mock.patch("evo.objects.utils.table_formats.all_known_formats", new=all_other_formats),
            self.assertRaises(TableFormatError),
        ):
            known_format = get_known_format(self.sample_table)
            raise AssertionError(f"Got unexpected format: {known_format.name}")

    def test_get_known_format(self) -> None:
        actual_format = get_known_format(self.sample_table)
        actual_field_names = actual_format._field_names

        # Check that the actual format is compatible with the expected format.
        self.data_format._check_format(actual_format)

        self.assertEqual(self.data_format.name, actual_format.name)
        self.assertEqual(self.data_format.width, actual_format.width)
        self.assertEqual(self.data_format.data_type, actual_format.data_type)
        self.assertEqual(self.expected_field_names, actual_field_names)

    def test_save_table(self) -> None:
        self.assertFalse(self.parquet_file.is_file())

        known_format = get_known_format(self.sample_table)
        table_info = known_format.save_table(self.sample_table, self.data_dir)

        self.assertEqual(frozenset(table_info), self.expected_field_names)
        self.assertEqual(self.expected_parquet_digest, table_info["data"])
        self.assertEqual(SAMPLE_DATA_LENGTH, table_info["length"])

        self.assertTrue(self.parquet_file.is_file())

    def test_save_table_when_file_exists_and_is_open(self) -> None:
        self.assertFalse(self.parquet_file.is_file())

        known_format = get_known_format(self.sample_table)
        known_format.save_table(self.sample_table, self.data_dir)
        self.assertTrue(self.parquet_file.is_file())

        with self.parquet_file.open():
            table_info = known_format.save_table(self.sample_table, self.data_dir)

        self.assertEqual(frozenset(table_info), self.expected_field_names)
        self.assertEqual(self.expected_parquet_digest, table_info["data"])
        self.assertEqual(SAMPLE_DATA_LENGTH, table_info["length"])

        self.assertTrue(self.parquet_file.is_file())

    def _save_parquet_file(self, add_column: bool = False, add_row: bool = False, change_type: bool = False) -> dict:
        if add_column or add_row or change_type:
            sample_length = SAMPLE_DATA_LENGTH
            if add_row:
                sample_length += 1
            self.sample_table = _get_sample_table(
                table_format=self.data_format, n_rows=sample_length, add_column=add_column, change_types=change_type
            )

        pq.write_table(self.sample_table, where=self.parquet_file, version="2.4", compression="gzip")
        info_dict = {
            "data": self.expected_parquet_digest,
            "length": SAMPLE_DATA_LENGTH,
            "width": self.sample_table.num_columns,
            "data_type": self.data_format.data_type,
            "keys_data_type": self.data_format._columns[0]._format_id,
            "field_names": self.expected_field_names,
        }
        if add_column:
            info_dict["width"] -= 1
        return info_dict

    def test_known_format_from_table_info(self) -> None:
        table_info = self._save_parquet_file()
        self.assertTrue(self.parquet_file.is_file())

        inferred_format = KnownTableFormat.from_table_info(table_info)
        self.assertTrue(self.data_format.is_provided_by(inferred_format))

    def test_load_table(self) -> None:
        table_info = self._save_parquet_file()
        self.assertTrue(self.parquet_file.is_file())
        inferred_format = KnownTableFormat.from_table_info(table_info)

        actual_table = KnownTableFormat.load_table(table_info, self.data_dir)
        self.assertEqual(inferred_format.width, actual_table.num_columns)
        self.assertEqual(table_info["length"], actual_table.num_rows)

        actual_format = ArrowTableFormat.from_schema(actual_table.schema)
        self.assertEqual(inferred_format.data_type, actual_format.data_type)

    def test_load_table_with_too_many_columns(self) -> None:
        table_info = self._save_parquet_file(add_column=True)
        self.assertTrue(self.parquet_file.is_file())

        with self.assertRaises(TableFormatError):
            KnownTableFormat.load_table(table_info, self.data_dir)

    def test_load_table_with_too_many_rows(self) -> None:
        table_info = self._save_parquet_file(add_row=True)
        self.assertTrue(self.parquet_file.is_file())

        with self.assertRaises(SchemaValidationError):
            KnownTableFormat.load_table(table_info, self.data_dir)

    def test_load_table_with_wrong_data_types(self) -> None:
        table_info = self._save_parquet_file(change_type=True)
        self.assertTrue(self.parquet_file.is_file())

        with self.assertRaises(TableFormatError):
            KnownTableFormat.load_table(table_info, self.data_dir)

    def test_load_table_from_uuid(self) -> None:
        table_info = self._save_parquet_file()
        self.assertTrue(self.parquet_file.is_file())

        table_info["data"] = uuid.uuid4()
        self.parquet_file = self.parquet_file.rename(self.parquet_file.parent / str(table_info["data"]))
        self.assertTrue(self.parquet_file.is_file())

        inferred_format = KnownTableFormat.from_table_info(table_info)

        actual_table = KnownTableFormat.load_table(table_info, self.data_dir)
        self.assertEqual(inferred_format.width, actual_table.num_columns)
        self.assertEqual(table_info["length"], actual_table.num_rows)

        actual_format = ArrowTableFormat.from_schema(actual_table.schema)
        self.assertEqual(inferred_format.data_type, actual_format.data_type)


def _complex_formats_for_testing() -> Iterator[dict]:
    """Generator of table formats with their generated GO models and keyword arguments for testing.

    :yields: (<table-format>, <expected-field-names>)
    """
    yield {
        "data_format": BaseTableFormat("downhole-collection-location-path", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("hexahedrons-indices", [pa.uint64()] * 8),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": True,
    }
    yield {
        "data_format": BaseTableFormat("hexahedrons-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("quadrilaterals-indices", [pa.uint64()] * 4),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": True,
    }
    yield {
        "data_format": BaseTableFormat("quadrilaterals-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("segments-indices", [pa.uint64()] * 2),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("segments-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("tetrahedra-indices", [pa.uint64()] * 4),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": True,
    }
    yield {
        "data_format": BaseTableFormat("tetrahedra-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("triangles-indices", [pa.uint64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("triangles-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }
    yield {
        "data_format": BaseTableFormat("unstructured-grid-geometry-vertices", [pa.float64()] * 3),
        "expected_field_names": ["data", "length", "width", "data_type"],
        "expect_extra_column_fails": False,
    }


@parameterized_class(_complex_formats_for_testing(), class_name_func=_test_name_from_known_format)
class TestComplexFormats(unittest.TestCase):
    data_format: BaseTableFormat
    expected_field_names: str
    expect_extra_column_fails: bool

    def setUp(self) -> None:
        self.sample_table = _get_sample_table(table_format=self.data_format, n_rows=SAMPLE_DATA_LENGTH)
        self.expected_parquet_digest = _get_table_digest(self.sample_table)
        self.data_dir = CACHE.get_location(ENVIRONMENT, self.__class__.__name__)
        self.parquet_file = self.data_dir / self.expected_parquet_digest

    def tearDown(self) -> None:
        self.parquet_file.unlink(missing_ok=True)

    def test_save_table(self) -> None:
        self.assertFalse(self.parquet_file.is_file())

        known_format = get_known_format(self.sample_table)
        table_info = known_format.save_table(self.sample_table, self.data_dir)

        self.assertEqual(list(table_info), self.expected_field_names)
        self.assertEqual(self.expected_parquet_digest, table_info["data"])
        self.assertEqual(SAMPLE_DATA_LENGTH, table_info["length"])

        self.assertTrue(self.parquet_file.is_file())

    def test_save_table_extra_column_fails(self) -> None:
        self.assertFalse(self.parquet_file.is_file())
        sample_table = _get_sample_table(self.data_format, n_rows=SAMPLE_DATA_LENGTH, add_column=True)

        if self.expect_extra_column_fails:
            with self.assertRaises(TableFormatError):
                _known_format = get_known_format(sample_table)
        else:
            known_format = get_known_format(sample_table)
            known_format.save_table(sample_table, self.data_dir)

        self.assertFalse(self.parquet_file.is_file())

    def test_save_table_different_column_types_fails(self) -> None:
        self.assertFalse(self.parquet_file.is_file())
        sample_table = _get_sample_table(self.data_format, n_rows=SAMPLE_DATA_LENGTH, change_types=True)

        known_format = get_known_format(sample_table)
        with self.assertRaises(TableFormatError):
            known_format.save_table(self.sample_table, self.data_dir)

        self.assertFalse(self.parquet_file.is_file())
