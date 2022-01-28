from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer


class DataContainerCSV(StreamImporter):
    NAME = "DataContainerCSV"
    AUTOIMPORTER = True
    STARTING_LINES = [DataContainer.JSON_PREFIX.strip()]

    def read(self) -> DataContainer:
        self._stream.seek(0)
        output = DataContainer.from_csv(self._stream, parse_dates=True)
        return output
