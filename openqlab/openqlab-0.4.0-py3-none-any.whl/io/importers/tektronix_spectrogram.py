import xml.etree.ElementTree as ET
from io import StringIO
from typing import Dict, Optional, Union
from xml.etree.ElementTree import Element

import numpy as np
import pandas as pd
from numpy import ndarray
from scipy.io import loadmat

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class TektronixSpectrogram(StreamImporter):
    NAME = "TektronixSpectrogram"
    AUTOIMPORTER = True
    STARTING_LINES = [b"MATLAB"]
    BINARY = True

    def read(self) -> DataContainer:
        self._stream.seek(0)
        data = loadmat(self._stream)
        required_keys = ["rsaMetadata", "SpectraCenter", "SpectraSpan", "TDelta", "S0"]
        for key in required_keys:
            if key not in data.keys():
                raise utils.UnknownFileType(
                    f"{self.NAME} Matlab file, but don't yet know how to handle it."
                )

        header = self._create_header(data)
        frequencies = np.linspace(
            header["StartFrequency"], header["StopFrequency"], len(data["S0"])
        )
        series = {}
        ii = 0
        timestamp = 0.0
        while f"S{ii}" in data.keys():
            series[timestamp] = data[f"S{ii}"].flatten()
            ii += 1
            timestamp += header["DeltaT"]
        df = pd.DataFrame(data=series, index=frequencies)
        df.rename_axis("Frequency (Hz)", inplace=True)
        df.rename_axis("Time (s)", axis="columns", inplace=True)
        df = df.transpose()
        output = DataContainer(df, header=header, header_type="spectrum")
        return output

    @staticmethod
    def _get_xml_text(
        xml: Element, path: str, default: Optional[Union[str, int]] = None
    ) -> Optional[Union[str, int]]:
        el = xml.find(path)
        if el is None:
            return default
        else:
            return el.text

    def _create_header(
        self, data: Dict[str, Union[bytes, str, ndarray]]
    ) -> Dict[str, Union[str, float]]:
        it = ET.iterparse(StringIO(data["rsaMetadata"][0]))
        for _, el in it:
            if "}" in el.tag:
                el.tag = el.tag.split("}", 1)[1]  # strip all namespaces
        root = it.root

        header = {
            "Date": self._get_xml_text(
                root,
                "./DataSetsCollection/SpectrumDataSets/SpectrumDataDescription/DateTime",
                "",
            ),
            "RBW": float(self._get_xml_text(root, ".//*[@pid='rbw']/Value", 0)),
            "VBW": float(self._get_xml_text(root, ".//*[@pid='vidBW']/Value", 0)),
            "Span": float(data["SpectraSpan"]),
            "CenterFrequency": float(data["SpectraCenter"]),
            "StartFrequency": float(data["SpectraCenter"] - data["SpectraSpan"] / 2),
            "StopFrequency": float(data["SpectraCenter"] + data["SpectraSpan"] / 2),
            "DeltaT": float(data["TDelta"][0][0]),
        }
        return header
