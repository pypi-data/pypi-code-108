import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class Tektronix(StreamImporter):
    NAME = "Tektronix"
    AUTOIMPORTER = True
    STARTING_LINES = [r"^Spectrum", r"^\[Global Parameters\]"]
    HEADER_MAP = {
        "Span": (float, "Span"),
        "Resolution Bandwidth": (float, "RBW"),
        "Video Bandwidth": (float, "VBW"),
        "Actual RBW": (float, None),
        "Frequency": (float, "CenterFrequency"),
        "Reference Level": (float, None),
        "RBW-unit": (str, "xUnit"),
        "Reference Level-unit": (str, "yUnit"),
    }
    xUNIT = "Hz"

    def read(self) -> DataContainer:
        self._read_header()
        data = self._read_data()
        output = DataContainer(data, header_type="spectrum")
        output.update_header(self._header)
        if output.empty:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: Did not find any valid \
                data in file '{self._stream.name}'"
            )
        return output

    def _read_header(self) -> None:
        self._header["Date"] = self._header_lines[0].split(",")[1].strip("\n")
        self._header["xUnit"] = self.xUNIT
        line = "True"
        while line:
            line = self._stream.readline()
            self._read_line(line)

            if line.startswith("[Traces]"):
                break

    def _read_data(self) -> DataFrame:
        traces = self._stream.read().split("[Trace]")
        del traces[0]

        data_out = pd.DataFrame()
        ylabel = utils.get_file_basename(self._stream.name)
        for i in range(len(traces)):
            trace = traces[i]
            try:
                lines = trace.strip().splitlines()
                lines.pop(0)
                name = ylabel + "_{0}".format(i + 1)
                points = int(lines.pop(0).split(",")[1])
                start = float(lines.pop(0).split(",")[1])
                stop = float(lines.pop(0).split(",")[1])
                y = [float(i.split(",")[0]) for i in lines]
                x = np.linspace(start, stop, num=points)
                data = pd.DataFrame(data=y, index=x, columns=[name])
            except ValueError:
                raise utils.ImportFailed(
                    f"'{self.NAME}' importer: Number of points does not fit number of values in file '{self._stream.name}'."
                ) from None
            data.index.rename("Frequency", inplace=True)
            if data_out.empty:
                data_out = data
            # elif len(data_out) == len(data):
            elif (data_out.index == data.index).all():
                data_out = data_out.join(data)
            else:
                raise utils.ImportFailed(
                    f"'{self.NAME}' importer: Traces in file '{self._stream.name}' do not have equal frequency axis."
                )
        return data_out
