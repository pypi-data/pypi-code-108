import logging
import re

import pandas as pd
from pandas.core.frame import DataFrame

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils

log = logging.getLogger(__name__)


class RohdeSchwarz(StreamImporter):
    NAME = "RohdeSchwarz"
    AUTOIMPORTER = True
    STARTING_LINES = ["^Type", "^Version"]
    HEADER_SPLIT = ";"
    HEADER_MAP = {
        "Type": (str, "Type"),
        "Version": (str, "Version"),
        "RBW": (float, "RBW"),
        "VBW": (float, "VBW"),
        "Center Freq": (float, "CenterFrequency"),
        "Span": (float, "Span"),
        "Start": (float, None),
        "Stop": (float, None),
        "SWT": (float, None),
        "Ref Level": (float, None),
        "Level Offset": (float, None),
        "Rf Att": (float, None),
        "Sweep Count": (float, None),
        "Values": (float, None),
        "x-Axis": (str, None),
        "y-Axis": (str, None),
        "Trace Mode": (str, None),
        "Detector": (str, None),
        "x-Unit": (str, "xUnit"),
        "y-Unit": (str, "yUnit"),
        "Preamplifier": (str, None),
        "Transducer": (str, None),
        "Mode": (str, None),
        "Date": (str, "Date"),
    }

    def read(self) -> DataContainer:
        for line in self._header_lines:
            corrected_line = line.replace(",", ".")
            self._read_line(corrected_line)
        data = self._parse()

        output = DataContainer(data, header_type="spectrum")
        output.update_header(self._header)
        if output.empty:
            raise utils.ImportFailed(
                f'{self.NAME}: Did not find any valid data in file "{self._stream.name}"'
            )
        return output

    def _get_xlabel(self) -> str:
        try:
            x_unit = self._header["xUnit"]
            if x_unit == "s":
                xlabel = "Time"
            elif x_unit == "Hz":
                xlabel = "Frequency"
            else:
                xlabel = "x"
        except KeyError:
            xlabel = "x"

        return xlabel

    def _parse(self) -> DataFrame:
        # self._stream.seek(0)
        data = []
        current_trace = "0"
        dec_sep = None
        line = "True"
        while line:
            line = self._stream.readline()
            logging.debug(f"line = {line}")
            line = line.replace(",", ".")
            match = re.match(r"Trace ([\d])", line)
            if match:
                log.debug(f"match = {match}")
                current_trace = match[1]

            self._read_line(line)

            # this is where the data starts
            if line.startswith("Values"):
                if (
                    not dec_sep
                ):  # only do this for the first trace, otherwise engine="python not possible
                    fpos = self._stream.tell()
                    comma = self._stream.readline().rfind(",")
                    dec_sep = "." if comma == -1 else ","
                    self._stream.seek(fpos)
                ylabel = (
                    utils.get_file_basename(self._stream.name) + "_" + current_trace
                )
                data.append(
                    pd.read_csv(
                        self._stream,
                        sep=";",
                        decimal=dec_sep,
                        index_col=0,
                        usecols=[0, 1],
                        names=[self._get_xlabel(), ylabel],
                        header=None,
                        nrows=self._header["Values"],
                        engine="python",
                    )
                )

        data = pd.concat(data, axis=1)
        return data
