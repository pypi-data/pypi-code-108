import numpy as np
import pandas as pd
import serial

from openqlab.io.base_importer import VisaImporter
from openqlab.io.data_container import DataContainer


class GPIB:
    def __init__(self, ser, addr):
        self._ser = ser
        self.command("++ver")
        print(self._ser.readline().decode())
        self.command("++addr {0}".format(addr))
        self.command("++auto 0")
        self.target_id = self.command("*idn?")
        print("Connected to", self.target_id)

    def command(self, cmd, always_read=False):
        self._ser.write(bytes(cmd + "\n", encoding="utf-8"))
        if cmd.endswith("?") or always_read:
            return self.read_answer()
        else:
            return None

    def read_answer(self):
        self.command("++read eoi")
        return self._ser.readline().decode().strip()


class HP4395A_GPIB(VisaImporter):
    """HP4395A GPIB IMPORTER

    This importer is designed to work together with a Prologix
    GPIB-USB interface, which presents itself as a virtual
    serial port.
    """

    IDN_STARTS_WITH = ""
    NAME = "HP4395A_GPIB"
    AUTOIMPORTER = False
    ADDRESS_STARTS_WITH = ""

    def __init__(  # pylint: disable=super-init-not-called
        self, file, both_channels: bool = False, clear_complex: bool = True
    ):
        self.file = file
        self._both_channels = both_channels
        self._clear_complex = clear_complex

    def read(self):
        serial_port, gpib_address = self.file.split("::")
        with serial.Serial(serial_port, 115200, timeout=1) as ser:
            gpib = GPIB(ser, gpib_address)

            if self._both_channels:
                gpib.command("CHAN1")
                data = self._read_channel(gpib)
                gpib.command("CHAN2")
                data = data.join(self._read_channel(gpib))
            else:
                data = self._read_channel(gpib)

        if self._clear_complex:
            data = data.apply(lambda x: x.to_numpy().real)

        return data

    def _read_channel(self, gpib):  # pylint: disable=no-self-use
        header = {}
        x_data = gpib.command("OUTPSWPRM?")
        y_data = gpib.command("OUTPDTRC?")
        y_unit = gpib.command("FMT?")
        if y_unit == "LOGM":
            header["yUnit"] = "dB"
        elif y_unit == "LINM":
            header["yUnit"] = "lin. Mag."
        elif y_unit == "SPECT":
            header["yUnit"] = "dBm"
        elif y_unit == "LINY":
            header["yUnit"] = "lin. U"
        elif y_unit == "LOGY":
            header["yUnit"] == "log. U"
        elif y_unit == "PHAS":
            phase_unit = gpib.command("PHAU?")
            if phase_unit == "DEG":
                header["yUnit"] = "deg"
            elif phase_unit == "RAD":
                header["yUnit"] = "rad"
        else:
            print("Don't know how to handle Y unit:", y_unit)

        X = np.fromstring(x_data, sep=",")
        Y = np.fromstring(y_data, sep=",")
        if len(X) == len(Y):
            df = pd.DataFrame(Y, X, columns=[header["yUnit"]])
        else:
            df = pd.DataFrame(Y[::2] + 1j * Y[1::2], X, columns=[header["yUnit"]])
        df.index.name = "Frequency"
        header["xUnit"] = "Hz"
        header["logX"] = True if gpib.command("SWPT?") == "LOGF" else False
        header["Channel"] = 1 if gpib.command("CHAN1?") == "1" else 2
        output = DataContainer(df)
        output.update_header(header)
        return output
