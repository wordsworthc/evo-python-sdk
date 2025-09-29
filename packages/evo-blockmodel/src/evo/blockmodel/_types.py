from __future__ import annotations

from typing import Protocol

# `evo-blockmodel-client` uses protocols for annotating some pyarrow types, because:
# - pyarrow is optional, but type annotations are not.
# - pyarrow has poor type checker support.
#
# These protocols should be treated as aliases for the corresponding pyarrow types.
# Any required interfaces from the corresponding pyarrow types should be added to these protocols as needed.


class DataType(Protocol):
    """Pyarrow data type.

    https://arrow.apache.org/docs/python/generated/pyarrow.DataType.html
    """

    ...


class Schema(Protocol):
    """Pyarrow schema.

    https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html
    """

    @property
    def names(self) -> list[str]:
        """The schema's field names."""
        ...

    @property
    def types(self) -> list[DataType]:
        """The schema's field types."""
        ...


class Table(Protocol):
    """Pyarrow table.

    https://arrow.apache.org/docs/python/generated/pyarrow.Table.html
    """

    @property
    def schema(self) -> Schema:
        """Schema of the table and its columns."""
        ...

    @property
    def num_columns(self) -> int:
        """Number of columns in this table."""
        ...

    @property
    def num_rows(self) -> int:
        """Number of rows in this table.

        Due to the definition of a table, all columns have the same number of rows.
        """
        ...

    def to_pandas(self) -> DataFrame:
        """Convert to a pandas-compatible NumPy array or DataFrame, as appropriate"""


class DataFrame(Protocol):
    """Pandas DataFrame.

    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    """
