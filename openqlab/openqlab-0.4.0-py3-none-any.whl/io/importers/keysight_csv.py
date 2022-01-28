import pandas as pd
from pandas.core.frame import DataFrame

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class KeysightCSV(StreamImporter):
    NAME = "KeysightCSV"
    AUTOIMPORTER = True
    STARTING_LINES = ["^x-axis", "^second"]

    def read(self) -> DataContainer:
        data = self._read_data()
        output = DataContainer(data, header_type="osci")
        output.header["xUnit"] = "s"
        output.header["yUnit"] = "V"
        return output

    def _read_data(self) -> DataFrame:
        xlabel = "Time"
        ylabel = utils.get_file_basename(self._stream.name)
        output = pd.read_csv(
            self._stream, sep=",", index_col=0, prefix=ylabel + "_", header=None
        )
        output.index.name = xlabel

        return output
