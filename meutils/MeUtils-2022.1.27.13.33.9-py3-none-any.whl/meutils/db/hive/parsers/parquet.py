import pandas as pd
from meutils.db.hive.parsers.base_parser import BaseParser


class ParquetParser(BaseParser):
    def __init__(self, **kwargs):
        super(ParquetParser, self).__init__(kwargs)

    # override
    def _read(self, file_path):
        return pd.read_parquet(file_path)
