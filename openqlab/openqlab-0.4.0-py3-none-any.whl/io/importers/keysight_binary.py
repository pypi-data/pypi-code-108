import struct
from typing import List, Tuple

import numpy as np
import pandas as pd
from numpy import ndarray

from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class KeysightBinary(StreamImporter):
    NAME = "KeysightBinary"
    AUTOIMPORTER = True
    BINARY = True
    STARTING_LINES = [b"^AG"]

    def read(self) -> DataContainer:
        time, data = self._import_data()

        ylabel = utils.get_file_basename(self._stream.name)

        data = pd.DataFrame(
            np.array(data).T,
            index=time,
            columns=[ylabel + "_{0}".format(ii) for ii in range(1, len(data) + 1)],
        )
        data.index.name = "Time"  # type: ignore
        output = DataContainer(data, header_type="osci")
        return output

    def _import_data(self) -> Tuple[ndarray, List[ndarray]]:
        def debug(s):  # pylint: disable=unused-argument
            # print(s)
            pass

        readuInt8 = lambda f: struct.unpack("<B", f.read(1))[0]
        readInt16 = lambda f: struct.unpack("<h", f.read(2))[0]
        readInt32 = lambda f: struct.unpack("<i", f.read(4))[0]
        readuInt32 = lambda f: struct.unpack("<I", f.read(4))[0]
        readFloat32 = lambda f: struct.unpack("<f", f.read(4))[0]
        readDouble64 = lambda f: struct.unpack("<d", f.read(8))[0]

        self._stream.seek(0)
        # read file header
        fileCookie = self._stream.read(2)
        debug(("fileCookie", fileCookie))

        fileVersion = self._stream.read(2)
        debug(("fileVersion", fileVersion))
        fileSize = readInt32(self._stream)
        debug(("fileSize", fileSize))
        nWaveforms = readInt32(self._stream)
        debug(("nWaveforms", nWaveforms))

        # stores voltage values from all waveforms and all buffers
        voltageVectors = []

        for waveformIndex in range(nWaveforms):
            # read waveform header
            headerSize = readInt32(self._stream)
            debug(("headerSize", headerSize))
            bytesLeft = headerSize - 4
            waveformType = readInt32(self._stream)
            debug(("waveformType", waveformType))
            bytesLeft -= 4
            nWaveformBuffers = readInt32(self._stream)
            debug(("nWaveformBuffers", nWaveformBuffers))
            bytesLeft -= 4
            nPoints = readInt32(self._stream)
            debug(("nPoints", nPoints))
            bytesLeft -= 4
            count = readInt32(self._stream)
            debug(("count", count))
            bytesLeft -= 4
            xDisplayRange = readFloat32(self._stream)
            debug(("xDisplayRange", xDisplayRange))
            bytesLeft -= 4
            xDisplayOrigin = readDouble64(self._stream)
            debug(("xDisplayOrigin", xDisplayOrigin))
            bytesLeft -= 8
            xIncrement = readDouble64(self._stream)
            debug(("xIncrement", xIncrement))
            bytesLeft -= 8
            xOrigin = readDouble64(self._stream)
            debug(("xOrigin", xOrigin))
            bytesLeft -= 8
            xUnits = readInt32(self._stream)
            debug(("xUnits", xUnits))
            bytesLeft -= 4
            yUnits = readInt32(self._stream)
            debug(("yUnits", yUnits))
            bytesLeft -= 4
            dateString = self._stream.read(16)
            debug(("dateString", dateString))
            bytesLeft -= 16
            timeString = self._stream.read(16)
            debug(("timeString", timeString))
            bytesLeft -= 16
            frameString = self._stream.read(24)
            debug(("frameString", frameString))
            bytesLeft -= 24
            waveformString = self._stream.read(16)
            debug(("waveformString", waveformString))
            bytesLeft -= 16
            timeTag = readDouble64(self._stream)
            debug(("timeTag", timeTag))
            bytesLeft -= 8
            segmentIndex = readuInt32(self._stream)
            debug(("segmentIndex", segmentIndex))
            bytesLeft -= 4

            # skip over any remaining data in the header
            self._stream.seek(bytesLeft, 1)  # 1 = relative to current position

            # generate time vector from xIncrement and xOrigin values
            if waveformIndex == 0:
                timeVector = xIncrement * np.arange(nPoints) + xOrigin

            for bufferIndex in range(nWaveformBuffers):
                debug(("bufferIndex:", bufferIndex))
                # read waveform buffer header
                headerSize = readInt32(self._stream)
                debug(("headerSize", headerSize))
                bytesLeft = headerSize - 4
                bufferType = readInt16(self._stream)
                debug(("bufferType", bufferType))
                bytesLeft -= 2
                bytesPerPoint = readInt16(self._stream)
                debug(("bytesPerPoint", bytesPerPoint))
                bytesLeft -= 2
                bufferSize = readInt32(self._stream)
                debug(("bufferSize", bufferSize))
                bytesLeft -= 4
                debug(("bytesLeft", bytesLeft))

                # skip over any remaining data in the header
                self._stream.seek(bytesLeft, 1)  # 1 = relative to current position

                debug(("BufferType:", bufferType))
                if (bufferType == 1) or (bufferType == 2) or (bufferType == 3):
                    # bufferType is PB_DATA_NORMAL, PB_DATA_MIN or PB_DATA_MAX (float)
                    voltageVector = np.zeros(nPoints, dtype=np.float32)
                    for ii in range(nPoints):
                        voltageVector[ii] = readFloat32(self._stream)
                else:
                    if bufferType == 4:
                        # bufferType is PB_DATA_COUNTS (int32)
                        voltageVector = np.zeros(nPoints, dtype=np.int32)
                        for ii in range(nPoints):
                            voltageVector[ii] = readInt32(self._stream)
                    else:
                        if bufferType == 5:
                            # bufferType is PB_DATA_LOGIC (uint8)
                            voltageVector = np.zeros(nPoints, dtype=np.uint8)
                            for ii in range(nPoints):
                                voltageVector[ii] = readuInt8(self._stream)
                        else:
                            # unrecognized bufferType read as unformatted bytes
                            voltageVector = np.zeros(nPoints, dtype=np.uint8)
                            for ii in range(nPoints):
                                voltageVector[ii] = readuInt8(self._stream)
                voltageVectors.append(voltageVector)
        return (timeVector, voltageVectors)
