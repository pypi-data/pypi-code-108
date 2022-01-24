import pathlib as _pathlib
import typing as _typing
from importlib import metadata as _metadata

import toml as _toml

from dynamo_io.definitions import BinarySetColumn  # noqa: F401
from dynamo_io.definitions import BooleanColumn  # noqa: F401
from dynamo_io.definitions import BytesColumn  # noqa: F401
from dynamo_io.definitions import Column  # noqa: F401
from dynamo_io.definitions import ColumnType  # noqa: F401
from dynamo_io.definitions import DELETE  # noqa: F401
from dynamo_io.definitions import DateColumn  # noqa: F401
from dynamo_io.definitions import DatetimeColumn  # noqa: F401
from dynamo_io.definitions import DynamoType  # noqa: F401
from dynamo_io.definitions import DynamoTypes  # noqa: F401
from dynamo_io.definitions import FloatColumn  # noqa: F401
from dynamo_io.definitions import FloatSetColumn  # noqa: F401
from dynamo_io.definitions import GlobalFirstColumn  # noqa: F401
from dynamo_io.definitions import GlobalSecondColumn  # noqa: F401
from dynamo_io.definitions import GlobalThirdColumn  # noqa: F401
from dynamo_io.definitions import Index  # noqa: F401
from dynamo_io.definitions import IndexedColumn  # noqa: F401
from dynamo_io.definitions import Indexes  # noqa: F401
from dynamo_io.definitions import IntegerColumn  # noqa: F401
from dynamo_io.definitions import IntegerSetColumn  # noqa: F401
from dynamo_io.definitions import ListColumn  # noqa: F401
from dynamo_io.definitions import MapColumn  # noqa: F401
from dynamo_io.definitions import PagedRowResponse  # noqa: F401
from dynamo_io.definitions import PartitionColumn  # noqa: F401
from dynamo_io.definitions import Response  # noqa: F401
from dynamo_io.definitions import ResponseType  # noqa: F401
from dynamo_io.definitions import Schema  # noqa: F401
from dynamo_io.definitions import SingleRowResponse  # noqa: F401
from dynamo_io.definitions import SortColumn  # noqa: F401
from dynamo_io.definitions import StringColumn  # noqa: F401
from dynamo_io.definitions import StringSetColumn  # noqa: F401
from dynamo_io.definitions import TimestampColumn  # noqa: F401
from dynamo_io.definitions import TypeHints  # noqa: F401
from dynamo_io.reader import get_indexed_record  # noqa: F401
from dynamo_io.reader import get_indexed_records  # noqa: F401
from dynamo_io.reader import get_indexed_row  # noqa: F401
from dynamo_io.reader import get_indexed_rows  # noqa: F401
from dynamo_io.reader import get_record  # noqa: F401
from dynamo_io.reader import get_records_for_partition  # noqa: F401
from dynamo_io.reader import get_row  # noqa: F401
from dynamo_io.reader import get_rows_for_partition  # noqa: F401
from dynamo_io.reader import read_entire_table  # noqa: F401
from dynamo_io.recorder import PagedRecordResponse  # noqa: F401
from dynamo_io.recorder import Record  # noqa: F401
from dynamo_io.recorder import SingleRecordResponse  # noqa: F401
from dynamo_io.writer import insert_records  # noqa: F401
from dynamo_io.writer import remove  # noqa: F401
from dynamo_io.writer import transacts  # noqa: F401
from dynamo_io.writer import upsert  # noqa: F401

SchemaType = _typing.ClassVar[Schema]

try:
    __version__ = _metadata.version(__package__)
except _metadata.PackageNotFoundError:  # pragma: no cover
    # If the package is not installed such that it has distribution metadata
    # fallback to loading the version from the pyproject.toml file.
    __version__ = _toml.loads(
        _pathlib.Path(__file__).parent.parent.joinpath("pyproject.toml").read_text()
    )["tool"]["poetry"]["version"]
