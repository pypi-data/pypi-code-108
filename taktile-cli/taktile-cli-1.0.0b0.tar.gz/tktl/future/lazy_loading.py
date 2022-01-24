import pathlib
import typing as t

import pandas as pd  # type: ignore
import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from tktl.core.exceptions import UnlazifiedParquetError
from tktl.core.loggers import LOG
from tktl.core.t import LazifyType

TAKTILE_LAZYLOAD_VERSION_KEY = "taktile_version".encode()
TAKTILE_LAZYLOAD_VERSION_VALUE = "0.2.0".encode()
TAKTILE_LAZYLOAD_BACKGROUND_DATA_KEY = "taktile_background_data".encode()
TAKTILE_LAZYLOAD_TYPE_KEY = "taktile_lazyload_type_key".encode()


def load_background_data_from_lazified_pq(path: pathlib.Path) -> pd.DataFrame:
    schema = pq.read_schema(path)

    if TAKTILE_LAZYLOAD_VERSION_KEY not in schema.metadata:
        raise UnlazifiedParquetError(f"{path} is not a lazified parquet file")

    background_data_bytes = schema.metadata[TAKTILE_LAZYLOAD_BACKGROUND_DATA_KEY]
    background_data = pd.read_json(background_data_bytes, orient="table")

    return background_data


def lazify_parquet_metadata(
    table: pa.Table,
    data: t.Optional[pd.DataFrame] = None,
    lazify_type: LazifyType = LazifyType.SHAP,
) -> pa.Table:
    """lazify_parquet_metadata.
    Add lazy loading information to parquet schema. If
    parameter data is provided, this data is stored. Otherwise
    background data is calculated and stored.

    Parameters
    ----------
    table : pa.Table
        table to lazify
    data : t.Optional[pd.DataFrame]
        data is the lazification data if provided
    lazify_type: LazifyType
        the type of lazification to be performed

    Returns
    -------
    pa.Table the same table with patched metadata

    """

    if data is None:
        try:
            from profiling.shap import ShapExplainer  # type: ignore
        except ImportError:
            LOG.error(
                "Could not load profiling package. Please make sure profiling is installed to lazify metadata"
            )

        df = table.to_pandas()

        LOG.trace("Calculating background data...")
        if lazify_type == LazifyType.SHAP:
            background_data = ShapExplainer._create_background_data_from_full_frame(df)
        else:
            background_data = _create_background_data_as_first_valid_occurence(df)
        background_data_json = background_data.to_json(orient="table")
    else:
        background_data_json = data.to_json(orient="table")

    if TAKTILE_LAZYLOAD_VERSION_KEY in table.schema.metadata:
        LOG.warning("Metadata is already lazified")

    LOG.trace("Patching metadata ...")
    metadata = {
        **table.schema.metadata,
        TAKTILE_LAZYLOAD_VERSION_KEY: TAKTILE_LAZYLOAD_VERSION_VALUE,
        TAKTILE_LAZYLOAD_BACKGROUND_DATA_KEY: background_data_json,
        TAKTILE_LAZYLOAD_TYPE_KEY: lazify_type.value,
    }

    return table.cast(table.schema.with_metadata(metadata))


def _create_background_data_as_first_valid_occurence(df):
    row = {}
    for col in df.columns:
        val = df[col].get(df[col].first_valid_index())
        row[col] = (
            val.dropna().iloc[0] if isinstance(val, pd.Series) else val
        )  # Duplicate Index
    return pd.DataFrame([row], columns=df.columns).astype(df.dtypes)
