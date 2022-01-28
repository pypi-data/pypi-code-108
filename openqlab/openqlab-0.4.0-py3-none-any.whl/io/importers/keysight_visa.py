from pathlib import Path
from typing import IO, List, Union

import numpy as np

from openqlab.io.base_importer import VisaImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class KeysightVisa(VisaImporter):
    NAME = "KeysightVisa"
    AUTOIMPORTER = True
    IDN_STARTS_WITH: str = "KEYSIGHT TECHNOLOGIES,DSO-X"
    MAX_COLUMNS = 4

    def __init__(  # pylint: disable=super-init-not-called
        self,
        data: Union[str, IO, Path],
        inst: None = None,
        stop_scope: bool = True,
        number_of_points: int = 1000,
    ):
        super().__init__(data, inst=inst)
        self.STOP_SCOPE = stop_scope
        self.NUMBER_OF_POINTS = number_of_points

    def read(self) -> DataContainer:
        data = self._read_data()
        output = DataContainer.concat(data, axis=1)
        output.index.name = "Time"
        output.header = self._header

        return output

    def _read_data(self) -> List[DataContainer]:
        self.write(":WAVeform:POINTs:MODE NORMal")
        self.write(f":WAVeform:POINts {self.NUMBER_OF_POINTS}")
        self.write(":WAVeform:FORMat ASCII")

        if self.STOP_SCOPE:
            self.write(":STOP")

        self._read_meta_data()

        xorigin = self._header["xorigin"]
        step = self._header["xincrement"]
        points = self._header["points"]
        # Using arange this way gives always the correct number of points
        self._index = np.arange(points) * step + xorigin

        data = []
        for i in range(1, 1 + self.MAX_COLUMNS):
            channel_active = self.query(f":CHANnel{i}:DISPlay?").strip()
            if channel_active == "1":
                data.append(DataContainer({i: self._read_column(i)}, index=self._index))

        if not data:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: No active trace on the scope"
            )

        # TODO start only if stopped
        if self.STOP_SCOPE:
            self.write(":RUN")
        return data

    def _read_meta_data(self) -> None:
        preamble = self.query("WAV:PREamble?").strip()
        entries = preamble.split(",")

        type_dict = {0: "normal", 1: "peak detect", 2: "average", 3: "hresolution"}

        self._header = dict(
            # format=entries[0],
            type=type_dict[int(entries[1])],
            points=int(entries[2]),
            average_count=int(entries[3]),
            xincrement=float(entries[4]),
            xorigin=float(entries[5]),
            xreference=int(entries[6]),
            xUnit="s",
            yUnit="V",
            # yincrement=float(entries[7]),
            # yorigin=float(entries[8]),
            # yreference=int(entries[9]),
        )

    def _read_column(self, channel: int) -> np.ndarray:
        """
        The data looks like this:

        #800000139 6.43216e-003, 9.24623e-003, 4.02010e-003, 1.28643e-002

        The first digit (8) defines the number of digits for the following
        number (00000139) which is the length of the data.
        """
        self.write(f":WAVeform:SOURce CHANnel{channel}")
        raw_data = self.query("WAV:DATA?").strip()

        if not raw_data or not raw_data[0] == "#":
            raise utils.ImportFailed(f"{self.NAME}: The data does not start with #")

        try:
            n = int(raw_data[1])
            n_digits = int(raw_data[2 : n + 2])

            clipped_data = raw_data[n + 2 :]
            assert (
                len(clipped_data) == n_digits
            ), f"len data: {len(clipped_data)}, n_digits: {n_digits}"

            data = np.array(clipped_data.split(","), dtype=float)
        except (ValueError, AssertionError):
            raise utils.ImportFailed(
                f"{self.NAME}: Could not process the data"
            ) from None

        return data
