import pandas as pd
import pyarrow.orc

from meutils.db.hive.parsers.base_parser import BaseParser


class ORCParser(BaseParser):
    def __init__(self, **kwargs):
        super(ORCParser, self).__init__(kwargs)

    # override
    def _read(self, file_path):
        return pd.read_orc(file_path)
