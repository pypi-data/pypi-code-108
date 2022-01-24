import pathlib
import typing as t

import pandas as pd  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from tktl.core.loggers import LOG
from tktl.core.t import LazifyType
from tktl.future.lazy_loading import lazify_parquet_metadata


def lazify_file(
    *,
    source_path: pathlib.Path,
    target_path: pathlib.Path,
    data: t.Optional[pd.DataFrame],
    lazify_type: LazifyType = LazifyType.SHAP,
):
    LOG.trace(f"Using lazify type '{lazify_type.value}'...")

    LOG.trace(f"Reading file '{source_path}'...")
    table = pq.read_table(source_path)

    table = lazify_parquet_metadata(table, data, lazify_type)

    LOG.trace(f"Writing patched file to '{target_path}'...")
    pq.write_table(table, target_path)
