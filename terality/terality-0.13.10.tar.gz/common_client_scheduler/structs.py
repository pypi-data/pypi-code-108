from dataclasses import dataclass
from typing import Hashable, List, Optional

from terality_serde import SerdeMixin, IndexType
from terality_serde.json_encoding import ArrayEncoding


@dataclass
class StructRef(SerdeMixin):
    type: str  # strings from IndexType/StructType enums
    id: str  # pylint: disable=invalid-name


@dataclass
class ParquetMetadataIndex(SerdeMixin):
    type_: IndexType
    encodings: List[Optional[ArrayEncoding]]
    names: List[Hashable]
    name: Hashable
    datetime_index_freq: Optional[str]


@dataclass
class ParquetMetadataCols(SerdeMixin):
    encodings: List[Optional[ArrayEncoding]]
    col_names: List[Hashable]
    col_names_name: Hashable


@dataclass
class ParquetMetadata(SerdeMixin):
    """
    When to_pandas/from_pandas methods are performed, these metadata
    are sent between client/scheduler instead of raw data.
    """

    index: ParquetMetadataIndex
    cols: ParquetMetadataCols


@dataclass
class NDArrayMetadata(SerdeMixin):
    transfer_id: str
    parquet_metadata: ParquetMetadata


@dataclass
class PandasIndexMetadata(SerdeMixin):
    transfer_id: str
    parquet_metadata: ParquetMetadata


@dataclass
class PandasSeriesMetadata(SerdeMixin):
    transfer_id: str
    parquet_metadata: ParquetMetadata


@dataclass
class PandasDFMetadata(SerdeMixin):
    transfer_id: str
    parquet_metadata: ParquetMetadata


@dataclass
class Display(SerdeMixin):
    value: str
