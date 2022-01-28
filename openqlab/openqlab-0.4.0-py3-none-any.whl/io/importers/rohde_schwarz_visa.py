from pathlib import Path
from typing import IO, List, Union

import numpy as np

from openqlab.io.base_importer import VisaImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class RohdeSchwarzVisa(VisaImporter):
    NAME = "RohdeSchwarzVisa"
    AUTOIMPORTER = True
    IDN_STARTS_WITH: str = "Rohde&Schwarz,FS"
    MAX_COLUMNS = 3
    MAX_DATA_POINTS = 30001

    def __init__(
        self, data: Union[str, IO, Path], inst: None = None, data_points: int = 10000
    ):
        super().__init__(data, inst=inst)

        if not 0 < data_points < self.MAX_DATA_POINTS:
            raise ValueError(
                f"The number of data points has to be from 1 to {self.MAX_DATA_POINTS}"
            )
        self._data_points = data_points
        self._header: dict

    def read(self) -> DataContainer:
        self.write(f"sweep:points {self._data_points}")

        data = self._read_data()
        output = DataContainer.concat(data, axis=1)
        output.header = self._header
        output.index.name = "Time" if output.header["Span"] == 0 else "Frequency"

        return output

    def _read_data(self) -> List[DataContainer]:
        self._read_meta_data()

        start = self._header["Start"]
        stop = self._header["Stop"]

        points = int(self.query("sweep:points?").strip())

        # frequency domain
        if self._header["Span"] > 0:
            self._index = np.linspace(start, stop, points)
        else:  # time domain
            self._index = np.linspace(0, self._header["SweepTime"], points)

        data = []
        for i in range(1, 1 + self.MAX_COLUMNS):
            channel_active = self.query(f"DISP:WIND:TRACE{i}:STAT?").strip()

            if channel_active == "1":
                data.append(DataContainer({i: self._read_column(i)}, index=self._index))

        if not data:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: No active trace on the scope"
            )

        return data

    def _read_meta_data(self) -> None:
        # TODO more metadata (see rohdeSchwarz importer)
        center_freq, span, start, stop = (
            self.query("SENSe:FREQuency:CENTer?; SPAN?; STARt?; STOP?")
            .strip()
            .split(";")
        )
        rbw, vbw = self.query("BAND:RES?; VID?").strip().split(";")

        yUnit = self.query("UNIT:POWer?").strip()
        if yUnit == "DBM":
            yUnit = "dBm"

        xUnit = "s" if span == "0" else "Hz"

        sweep_time = self.query("sweep:time?").strip()

        self._header = {
            "Start": float(start),
            "Stop": float(stop),
            "CenterFrequency": float(center_freq),
            "Span": float(span),
            "RBW": float(rbw),
            "VBW": float(vbw),
            "xUnit": xUnit,
            "yUnit": yUnit,
            "SweepTime": float(sweep_time),
        }

    # TODO test with positive dBm values
    def _read_column(self, channel: int) -> np.ndarray:
        """
        TODO
        """
        raw_data = self.query(f"TRACE? TRACE{channel}").strip()

        if not raw_data or not raw_data[0] in ["-", "+"]:
            raise utils.ImportFailed(
                f"{self.NAME}: The data does not start with a number: {raw_data[:20]}"
            )

        try:
            data = np.array(raw_data.split(","), dtype=float)
        except (ValueError, AssertionError) as e:
            raise utils.ImportFailed(f"{self.NAME}: Could not process the data") from e

        return data
