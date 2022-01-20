import os
import logging
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

from . import files


def write(
    dataframe,
    root_path,
    overwrite=True,
    partition_cols=None,
    partition_filename_cb=None,
    filesystem=None,
    use_legacy_dataset=None,
    **kwargs
):

    table = pa.Table.from_pandas(dataframe)

    if overwrite:
        if os.path.exists(root_path):
            # files.make_directory(file_path)
            files.remove_directory(root_path, recursive=True)

    try:
        pq.write_to_dataset(
            table,
            root_path=root_path,
            partition_cols=partition_cols,
            partition_filename_cb=partition_filename_cb,
            filesystem=filesystem,
            use_legacy_dataset=use_legacy_dataset,
            **kwargs
        )
    except Exception as err:
        logging.error(err)
