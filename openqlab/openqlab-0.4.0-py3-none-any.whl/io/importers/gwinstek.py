from pathlib import Path
from typing import Callable, cast

import numpy as np
import pandas as pd

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class Gwinstek(StreamImporter):
    NAME = "Gwinstek"
    AUTOIMPORTER = True
    STARTING_LINES = [r"^Format,1.0B,"]
    SAVEMODES = ("Detail", "Fast")
    HEADER_SPLIT = ","
    HEADER_MAP = {
        "Memory Length": (int, "NumPoints"),
        "Source": (str, None),
        "Vertical Units": (str, "yUnit"),
        "Vertical Units Div": (float, None),
        "Vertical Units Extend Div": (float, None),
        "Label": (str, None),
        "Probe Type": (float, None),
        "Probe Ratio": (float, None),
        "Vertical Scale": (float, "yScale"),
        "Vertical Position": (float, "yOffset"),
        "Horizontal Units": (str.lower, "xUnit"),
        "Horizontal Scale": (float, "xScale"),
        "Horizontal Position": (float, "xOffset"),
        "SincET Mode": (str, None),
        "Sampling Period": (float, None),
        "Horizontal Old Scale": (float, None),
        "Horizontal Old Position": (float, None),
        "Firmware": (str, None),
        "Mode": (str, None),
    }

    def read(self) -> DataContainer:
        self._read_header()
        data = self._read_data()
        output = DataContainer(data, header_type="osci")

        return output

    def _read_line(self, line: str) -> None:
        split = line.strip().split(self.HEADER_SPLIT)
        keyword, *values = split

        if keyword not in self.HEADER_MAP:
            return

        type_ = cast(Callable, self.HEADER_MAP[keyword][0])
        keyword = self._get_key(keyword)

        values = values[0::2]
        self._header[keyword] = [type_(value) for value in values]

    def _read_header(self) -> None:
        line = "string"
        while line:
            line = self._stream.readline()
            if line.startswith("Waveform Data"):
                break
            self._read_line(line)
        self.num_traces = len(self._header["NumPoints"])

    def _read_trace(self, ii: int) -> DataContainer:
        xlabel = "Time"

        header = {key: value[ii] for key, value in self._header.items()}
        mode = header.get("Mode")

        if mode not in self.SAVEMODES:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: Could not determine savemode in file '{self._stream.name}'"
            )

        if mode == "Detail":
            index, data = self._data.iloc[:, 2 * ii : 2 * ii + 2].values.T

        if mode == "Fast":
            x_offset = header["xOffset"]
            start = -header["xScale"] * 10 / 2 + x_offset
            stop = header["xScale"] * 10 / 2 + x_offset
            num_points = header["NumPoints"]

            index = np.linspace(start, stop, endpoint=False, num=num_points)
            data = self._data.iloc[:, 2 * ii].values
            data = data * header["yScale"] / 25

        output = DataContainer(
            data=data,
            index=index,
            header=header,
            columns=[f"{Path(self._stream.name).stem}_{ii+1}"],
        )
        output.index.name = xlabel

        return output

    def _read_data(self) -> DataContainer:

        self._data = pd.read_csv(self._stream, sep=self.HEADER_SPLIT, header=None)

        traces = [self._read_trace(n) for n in range(self.num_traces)]
        return DataContainer.concat(traces, axis=1)
