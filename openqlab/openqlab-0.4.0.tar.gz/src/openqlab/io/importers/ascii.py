from typing import List

import pandas as pd
from pandas.core.frame import DataFrame

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class ASCII(StreamImporter):
    PRIORITY = -10
    NAME = "ASCII"
    AUTOIMPORTER = False
    STARTING_LINES: List[str] = []

    def _check_header(self) -> List:
        for _ in range(11):
            try:
                line = self._stream.readline()
            except UnicodeDecodeError:
                raise utils.UnknownFileType(
                    f"'{self.NAME}' importer: cannot decode binary file"
                ) from None

            col = line.split()
            for item in col:
                try:
                    float(item)
                except ValueError:
                    raise utils.UnknownFileType(
                        f"'{self.NAME}' importer: expected plain numeric ASCII"
                    ) from None
        self._stream.seek(0)
        return []

    def read(self) -> DataContainer:
        data = self._read_data()
        output = DataContainer(data)
        return output

    def _read_data(self) -> DataFrame:
        xlabel = "x"
        ylabel = utils.get_file_basename(self._stream.name)
        data = pd.read_csv(
            self._stream,
            sep=None,
            index_col=0,
            usecols=[0, 1],
            names=[xlabel, ylabel],
            header=None,
            engine="python",
        )
        return data
