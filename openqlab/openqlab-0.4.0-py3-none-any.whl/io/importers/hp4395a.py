from pathlib import Path
from typing import List

import pandas as pd
from pandas.errors import EmptyDataError

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer

# TODO implement header


class HP4395A(StreamImporter):
    NAME = "HP4395A"
    AUTOIMPORTER = True
    STARTING_LINES = [r'^"4395A|^"8751A']

    def read(self) -> DataContainer:
        self._header["xUnit"] = "Hz"
        self._header["yUnit"] = "dB"

        points = 0
        channel = 0
        channels: List = []
        filename = Path(self._stream.name).stem

        line = "True"
        while line:
            line = self._stream.readline()
            if line.startswith('"NUMBER of POINTS'):
                points = int(line.rstrip("\r\n")[19:-1])
            elif line.startswith('"CHANNEL'):
                channel = int(line.rstrip("\r\n")[10:-1])
                prefix = f"{filename}_Ch{channel}"
            elif line.startswith('"Frequency"'):
                pos = (
                    self._stream.tell()
                )  # UGLY: pd.read_table seems to always seek to the
                #       end of the file, so store our approx.
                #       position here.
                channels.append(
                    pd.read_csv(
                        self._stream,
                        index_col=0,
                        nrows=points,
                        sep="\t",
                        names=[
                            "Frequency (Hz)",
                            f"{prefix}_DataReal",
                            f"{prefix}_DataImag",
                            f"{prefix}_MemReal",
                            f"{prefix}_MemImag",
                        ],
                    )
                )
                self._stream.seek(pos)

        data: pd.DataFrame = pd.concat(channels, axis=1)
        output: DataContainer = DataContainer(data, header_type="spectrum")
        if data.empty:
            raise EmptyDataError(
                f"{self.NAME} importer: no data found in file {self._stream.name}"
            )
        output.header = self._header
        return output
