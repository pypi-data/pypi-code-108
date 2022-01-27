import logging

import fsspec
import pandas as pd
from meutils.db.hive.parsers.base_parser import BaseParser


class TextParser(BaseParser):
    def __init__(
        self,
        delimiter,
        col_names,
        col_dtypes,
        error_bad_lines=True,
        optional_na_values="\\N",
        quoting_type=3,
        default_engine="c",
        **kwargs,
    ):
        super(TextParser, self).__init__(kwargs)
        self.delimiter = delimiter
        self.col_names = col_names
        self.col_dtypes = col_dtypes
        self.error_bad_lines = error_bad_lines

        # add optional NA Values
        # default NA Values in Hive:["\\N", "NULL"]
        # ref: https://blog.csdn.net/a308601801/article/details/90597645
        self.optional_na_values = optional_na_values

        # QUOTE_MINIMAL (0), QUOTE_ALL (1), QUOTE_NONNUMERIC (2)
        # or QUOTE_NONE (3)
        # Since the data may contain `'` or `"`, it uses `QUOTE_NONE` to
        # instructs the csv reader to perform no special processing of
        # quote characters.
        # ref: https://docs.python.org/3/library/csv.html
        self.quoting_type = quoting_type

        # The C engine is faster while the python engine is
        # currently more feature-complete.
        self.default_engine = default_engine

    # override
    def _read(self, file_path):
        try:
            # ignore errors when no encoding is specified
            # https://github.com/pandas-dev/pandas/blob/v1.2.3/pandas/io/common.py#L639
            with fsspec.open(file_path, "r", errors="replace") as handle:
                pd_df = pd.read_csv(
                    handle,
                    delimiter=self.delimiter,
                    names=self.col_names,
                    engine=self.default_engine,
                    na_values=self.optional_na_values,
                    quoting=self.quoting_type,
                    error_bad_lines=self.error_bad_lines,
                )
        except pd.errors.ParserError as pe:
            if self.default_engine == "python":
                raise pe
            logging.warning(pe)
            logging.warning(
                f"File: {file_path} was parsed failed with C engine, "
                "switch to python engine!!!"
            )
            backup_engine = "python"
            with fsspec.open(file_path, "r", errors="replace") as handle:
                pd_df = pd.read_csv(
                    handle,
                    delimiter=self.delimiter,
                    names=self.col_names,
                    engine=backup_engine,
                    na_values=self.optional_na_values,
                    quoting=self.quoting_type,
                    error_bad_lines=self.error_bad_lines,
                )

        return pd_df
