import struct

import numpy as np
import pandas as pd
from numpy import ndarray
from pandas.core.frame import DataFrame

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class Gwinstek_LSF(StreamImporter):
    NAME = "Gwinstek_LSF"
    AUTOIMPORTER = True
    BINARY = True
    STARTING_LINES = [b"^Format,1.0B;"]
    SAVEMODES = ("Detail", "Fast")
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
        "Horizontal Units": (str, "xUnit"),
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

        output.update_header(self._header)
        return output

    def _read_header(self) -> None:
        split = self._header_lines[0].decode().split(";")
        for line in split:
            if line.startswith("Waveform Data"):
                break
            self._read_line(line)

    def construct_x_axis(self) -> ndarray:
        x_offset = self._header["xOffset"]
        start = -self._header["xScale"] * 10 / 2 + x_offset
        stop = self._header["xScale"] * 10 / 2 + x_offset
        num_points = self._header["NumPoints"]
        return np.linspace(start, stop, endpoint=False, num=num_points)

    def _read_data(self) -> DataFrame:
        xlabel = "Time"
        ylabel = utils.get_file_basename(self._stream.name)
        try:
            if self._header["xUnit"] == "S":
                self._header["xUnit"] = "s"
        except KeyError:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: could not gather necessary information in file '{self._stream.name}'"
            ) from None

        if not self._stream.read(1) == b"#":
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: expected line to start with '#' '{self._stream.name}'"
            )

        digits = int(struct.unpack("c", self._stream.read(1))[0])
        self._stream.read(digits)

        y_scale = self._header["yScale"] / 25
        y_offset = self._header["yOffset"] / y_scale + 128

        data = np.fromfile(self._stream, dtype="int16")
        index = self.construct_x_axis()
        data = pd.DataFrame(data, index=index, columns=[ylabel])
        data.index.name = xlabel
        data = (data - y_offset) * y_scale

        return data
