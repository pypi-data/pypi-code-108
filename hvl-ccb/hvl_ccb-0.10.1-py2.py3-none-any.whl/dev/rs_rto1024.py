#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Python module for the Rhode & Schwarz RTO 1024 oscilloscope.
The communication to the device is through VISA, type TCPIP / INSTR.
"""

import logging
import re
from pathlib import PureWindowsPath
from time import sleep
from typing import List, Tuple, Union

from hvl_ccb.dev.base import DeviceException
from .visa import (
    VisaDevice,
    VisaDeviceConfig,
    _VisaDeviceConfigBase,
    _VisaDeviceConfigDefaultsBase,
)
from ..comm.visa import VisaCommunication, VisaCommunicationConfig
from ..configuration import configdataclass
from ..utils.enum import AutoNumberNameEnum
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class RTO1024Error(DeviceException):
    pass


@configdataclass
class _RTO1024ConfigBase(_VisaDeviceConfigBase):

    waveforms_path: str
    """
    Windows directory on the oscilloscope filesystem for storing waveforms.
    Mind escaping the backslashes of the path.
    """

    settings_path: str
    """
    Windows directory on the oscilloscope filesystem for storing settings .dfl files.
    Mind escaping the backslashes of the path.
    """

    backup_path: str
    """
    Windows directory on the oscilloscope filesystem for use as backup directory for
    waveforms. Mind escaping the backslashes of the path.
    """


@configdataclass
class _RTO1024ConfigDefaultsBase(_VisaDeviceConfigDefaultsBase):

    command_timeout_seconds: Number = 60
    """
    Timeout to wait for asynchronous commands to complete, in seconds. This timeout
    is respected for long operations such as storing waveforms.
    """
    wait_sec_short_pause: Number = 0.1
    """Time for short wait periods, in seconds (depends on both device and
    network/connection)."""
    wait_sec_enable_history: Number = 1
    """Time to wait after enabling history, in seconds."""
    wait_sec_post_acquisition_start: Number = 2
    """Time to wait after start of continuous acquisition, in seconds."""

    def clean_values(self):
        super().clean_values()

        if self.command_timeout_seconds <= 0:
            raise ValueError(
                "Timeout to wait for asynchronous commands to complete must be a "
                "positive value (in seconds)."
            )
        if self.wait_sec_short_pause <= 0:
            raise ValueError(
                "Wait time for a short pause must be a positive value (in seconds)."
            )
        if self.wait_sec_enable_history <= 0:
            raise ValueError(
                "Wait time for enabling history must be a positive value (in seconds)."
            )
        if self.wait_sec_post_acquisition_start <= 0:
            raise ValueError(
                "Wait time after acquisition start must be a positive value (in "
                "seconds)."
            )


@configdataclass
class RTO1024Config(VisaDeviceConfig, _RTO1024ConfigDefaultsBase, _RTO1024ConfigBase):
    """
    Configdataclass for the RTO1024 device.
    """

    pass


@configdataclass
class RTO1024VisaCommunicationConfig(VisaCommunicationConfig):
    """
    Configuration dataclass for VisaCommunication with specifications for the RTO1024
    device class.
    """

    interface_type: Union[
        str, VisaCommunicationConfig.InterfaceType
    ] = VisaCommunicationConfig.InterfaceType.TCPIP_INSTR  # type: ignore


class RTO1024VisaCommunication(VisaCommunication):
    """
    Specialization of VisaCommunication for the RTO1024 oscilloscope
    """

    @staticmethod
    def config_cls():
        return RTO1024VisaCommunicationConfig


class RTO1024(VisaDevice):
    """
    Device class for the Rhode & Schwarz RTO 1024 oscilloscope.
    """

    class TriggerModes(AutoNumberNameEnum):
        """
        Enumeration for the three available trigger modes.
        """

        AUTO = ()
        NORMAL = ()
        FREERUN = ()

        @classmethod
        def names(cls):
            """
            Returns a list of the available trigger modes.
            :return: list of strings
            """

            return list(map(lambda x: x.name, cls))

    @staticmethod
    def config_cls():
        return RTO1024Config

    @staticmethod
    def default_com_cls():
        return RTO1024VisaCommunication

    def __init__(
        self,
        com: Union[RTO1024VisaCommunication, RTO1024VisaCommunicationConfig, dict],
        dev_config: Union[RTO1024Config, dict],
    ):
        super().__init__(com, dev_config)

    def start(self) -> None:
        """
        Start the RTO1024 oscilloscope and bring it into a defined state and remote
        mode.
        """

        super().start()

        # go to remote mode
        self.com.write("&GTR")

        # reset device (RST) and clear status registers (CLS)
        self.com.write("*RST", "*CLS")

        # enable local display
        self.local_display(True)

        # enable status register
        self.com.write("*ESE 127")

    def stop(self) -> None:
        """
        Stop the RTO1024 oscilloscope, reset events and close communication. Brings
        back the device to a state where local operation is possible.
        """

        if self._spoll_thread is not None and self._spoll_thread.is_polling():
            # disable any events, EventStatusEnable ESE = 0
            self.com.write("*ESE 0")

            # disable any service requests SRE = 0
            self.com.write("*SRE 0")

            # device clear: abort processing of any commands
            self.com.write("&DCL")

            # go to local mode
            self.com.write("&GTL")
        else:
            logger.warning("RTO1024 was already stopped")

        super().stop()

    def local_display(self, state: bool) -> None:
        """
        Enable or disable local display of the scope.

        :param state: is the desired local display state
        """
        state_str = "ON" if state else "OFF"
        self.com.write(f"SYST:DISP:UPD {state_str}")

    def set_acquire_length(self, timerange: float) -> None:
        r"""
        Defines the time of one acquisition, that is the time across the 10 divisions
        of the diagram.

        *  Range: 250E-12 ... 500 [s]
        *  Increment: 1E-12 [s]
        *  \*RST = 0.5 [s]

        :param timerange: is the time for one acquisition. Range: 250e-12 ... 500 [s]
        """

        self.com.write(f"TIMebase:RANGe {timerange:G}")

    def get_acquire_length(self) -> float:
        r"""
        Gets the time of one acquisition, that is the time across the 10 divisions
        of the diagram.

        *  Range: 250E-12 ... 500 [s]
        *  Increment: 1E-12 [s]

        :return: the time for one acquisition. Range: 250e-12 ... 500 [s]
        """

        return float(self.com.query("TIMebase:RANGe?"))

    def set_reference_point(self, percentage: int) -> None:
        r"""
        Sets the reference point of the time scale in % of the display.
        If the "Trigger offset" is zero, the trigger point matches the reference point.
        ReferencePoint = zero pint of the time scale

        *  Range: 0 ... 100 [%]
        *  Increment: 1 [%]
        *  \*RST = 50 [%]

        :param percentage: is the reference in %
        """

        self.com.write(f"TIMebase:REFerence {percentage:d}")

    def get_reference_point(self) -> int:
        r"""
        Gets the reference point of the time scale in % of the display.
        If the "Trigger offset" is zero, the trigger point matches the reference point.
        ReferencePoint = zero pint of the time scale

        *  Range: 0 ... 100 [%]
        *  Increment: 1 [%]

        :return: the reference in %
        """

        return int(self.com.query("TIMebase:REFerence?"))

    def set_repetitions(self, number: int) -> None:
        r"""
        Set the number of acquired waveforms with RUN Nx SINGLE. Also defines the
        number of waveforms used to calculate the average waveform.

        *  Range: 1 ... 16777215
        *  Increment: 10
        *  \*RST = 1

        :param number: is the number of waveforms to acquire
        """

        self.com.write(f"ACQuire:COUNt {number:d}")

    def get_repetitions(self) -> int:
        r"""
        Get the number of acquired waveforms with RUN Nx SINGLE. Also defines the
        number of waveforms used to calculate the average waveform.

        *  Range: 1 ... 16777215
        *  Increment: 10
        *  \*RST = 1

        :return: the number of waveforms to acquire
        """

        return int(self.com.query("ACQuire:COUNt?"))

    def set_channel_state(self, channel: int, state: bool) -> None:
        """
        Switches the channel signal on or off.

        :param channel: is the input channel (1..4)
        :param state: is True for on, False for off
        """

        self.com.write(f"CHANnel{channel}:STATe {'ON' if state else 'OFF'}")

    def get_channel_state(self, channel: int) -> bool:
        """
        Queries if the channel is active or not.

        :param channel: is the input channel (1..4)
        :return: True if active, else False
        """

        return self.com.query(f"CHANnel{channel}:STATe?") == "1"

    def set_channel_scale(self, channel: int, scale: float) -> None:
        r"""
        Sets the vertical scale for the indicated channel.
        The scale value is given in volts per division.

        *   Range for scale: depends on attenuation factor and coupling. With
            1:1 probe and external attenuations and 50 Ω input
            coupling, the vertical scale (input sensitivity) is 1
            mV/div to 1 V/div. For 1 MΩ input coupling, it is 1
            mV/div to 10 V/div. If the probe and/or external
            attenuation is changed, multiply the values by the
            attenuation factors to get the actual scale range.

        *  Increment: 1e-3
        *  \*RST = 0.05

        See also:
        set_channel_range

        :param channel: is the channel number (1..4)
        :param scale: is the vertical scaling [V/div]
        """

        self.com.write(f"CHANnel{channel}:SCALe {scale:4.3f}")

    def get_channel_scale(self, channel: int) -> float:
        """
        Queries the channel scale in V/div.

        :param channel: is the input channel (1..4)
        :return: channel scale in V/div
        """

        return float(self.com.query(f"CHANnel{channel}:SCALe?"))

    def set_channel_range(self, channel: int, v_range: float) -> None:
        r"""
        Sets the voltage range across the 10 vertical divisions of the diagram. Use
        the command alternatively instead of set_channel_scale.

        *   Range for range: Depends on attenuation factors and coupling. With
            1:1 probe and external attenuations and 50 Ω input
            coupling, the range is 10 mV to 10 V. For 1 MΩ
            input coupling, it is 10 mV to 100 V. If the probe
            and/or external attenuation is changed, multiply the
            range values by the attenuation factors.

        *  Increment: 0.01
        *  \*RST = 0.5

        :param channel: is the channel number (1..4)
        :param v_range: is the vertical range [V]
        """

        self.com.write(f"CHANnel{channel}:RANGe {v_range:4.3f}")

    def get_channel_range(self, channel: int) -> float:
        """
        Queries the channel range in V.

        :param channel: is the input channel (1..4)
        :return: channel range in V
        """

        return float(self.com.query(f"CHANnel{channel}:RANGe?"))

    def set_channel_position(self, channel: int, position: float) -> None:
        r"""
        Sets the vertical position of the indicated channel as a graphical value.

        *  Range: -5.0 ... 5.0 [div]
        *  Increment: 0.02
        *  \*RST = 0

        :param channel: is the channel number (1..4)
        :param position: is the position. Positive values move the waveform up,
            negative values move it down.
        """

        self.com.write(f"CHANnel{channel}:POSition {position:3.2f}")

    def get_channel_position(self, channel: int) -> float:
        r"""
        Gets the vertical position of the indicated channel.

        :param channel: is the channel number (1..4)
        :return: channel position in div (value between -5 and 5)
        """

        return float(self.com.query(f"CHANnel{channel}:POSition?"))

    def set_channel_offset(self, channel: int, offset: float) -> None:
        r"""
        Sets the voltage offset of the indicated channel.

        *  Range: Dependent on the channel scale and coupling [V]
        *  Increment: Minimum 0.001 [V], may be higher depending on the channel scale
           and coupling
        *  \*RST = 0

        :param channel: is the channel number (1..4)
        :param offset: Offset voltage. Positive values move the waveform down,
            negative values move it up.
        """

        self.com.write(f"CHANnel{channel}:OFFSet {offset:3.3f}")

    def get_channel_offset(self, channel: int) -> float:
        r"""
        Gets the voltage offset of the indicated channel.

        :param channel: is the channel number (1..4)
        :return: channel offset voltage in V (value between -1 and 1)
        """

        return float(self.com.query(f"CHANnel{channel}:OFFSet?"))

    def set_trigger_source(self, channel: int, event_type: int = 1) -> None:
        """
        Set the trigger (Event A) source channel.

        :param channel: is the channel number (1..4)
        :param event_type: is the event type. 1: A-Event, 2: B-Event, 3: R-Event
        """

        self.com.write(f"TRIGger{event_type}:SOURce CHAN{channel}")

    def set_trigger_level(
        self, channel: int, level: float, event_type: int = 1
    ) -> None:
        r"""
        Sets the trigger level for the specified event and source.

        *  Range: -10 to 10 V
        *  Increment: 1e-3 V
        *  \*RST = 0 V

        :param channel: indicates the trigger source.

            *  1..4    = channel 1 to 4, available for all event types 1..3
            *  5       = external trigger input on the rear panel for analog signals,
               available for A-event type = 1
            *  6..9    = not available

        :param level: is the voltage for the trigger level in [V].
        :param event_type: is the event type. 1: A-Event, 2: B-Event, 3: R-Event
        """

        self.com.write(f"TRIGger{event_type}:LEVel{channel} {level}")

    def set_trigger_mode(self, mode: Union[str, TriggerModes]) -> None:
        """
        Sets the trigger mode which determines the behavior of the instrument if no
        trigger occurs.

        :param mode: is either auto, normal, or freerun.
        :raises RTO1024Error: if an invalid triggermode is selected
        """

        if isinstance(mode, str):
            try:
                mode = self.TriggerModes[mode.upper()]  # type: ignore
            except KeyError as e:
                err_msg = (
                    f'"{mode}" is not an allowed trigger mode out of '
                    f"{self.TriggerModes.names()}."
                )
                logger.error(err_msg, exc_info=e)
                raise RTO1024Error(err_msg)
        assert isinstance(mode, self.TriggerModes)

        self.com.write(f"TRIGger1:MODE {mode.name}")

    def file_copy(self, source: str, destination: str) -> None:
        """
        Copy a file from one destination to another on the oscilloscope drive. If the
        destination file already exists, it is overwritten without notice.

        :param source: absolute path to the source file on the DSO filesystem
        :param destination: absolute path to the destination file on the DSO filesystem
        :raises RTO1024Error: if the operation did not complete
        """

        # clear status
        self.com.write("*CLS")

        # initiate file copy
        self.com.write(f"MMEMory:COPY '{source}', '{destination}'", "*OPC")

        # wait for OPC
        done = self.wait_operation_complete(self.config.command_timeout_seconds)

        if not done:
            err_msg = "File copy not complete, timeout exceeded."
            logger.error(err_msg)
            raise RTO1024Error(err_msg)

        logger.info(f'File copied: "{source}" to "{destination}"')

    def backup_waveform(self, filename: str) -> None:
        """
        Backup a waveform file from the standard directory specified in the device
        configuration to the standard backup destination specified in the device
        configuration. The filename has to be specified without .bin or path.

        :param filename: The waveform filename without extension and path
        """
        waveforms_file_path = str(PureWindowsPath(self.config.waveforms_path, filename))
        backup_file_path = str(PureWindowsPath(self.config.backup_path, filename))

        logger.info(f"Backing up {filename}.Wfm.bin")
        self.file_copy(waveforms_file_path + ".Wfm.bin", backup_file_path + ".Wfm.bin")

        logger.info(f"Backing up {filename}.bin")
        self.file_copy(waveforms_file_path + ".bin", backup_file_path + ".bin")

    def list_directory(self, path: str) -> List[Tuple[str, str, int]]:
        """
        List the contents of a given directory on the oscilloscope filesystem.

        :param path: is the path to a folder
        :return: a list of filenames in the given folder
        """

        file_string = self.com.query(f"MMEMory:CATalog? '{path}'")

        # generate list of strings
        file_list = re.findall('[^,^"]+,[A-Z]+,[0-9]+', file_string)

        # delete . and .. entries
        assert len(file_list) > 0 and file_list[0][:1] == ".", 'Expected "." folder'
        assert len(file_list) > 1 and file_list[1][:2] == "..", 'Expected ".." folder'
        file_list[0:2] = []

        # split lines into lists [name, extension, size]
        file_list = [line.split(",") for line in file_list]

        return file_list

    def save_waveform_history(
        self, filename: str, channel: int, waveform: int = 1
    ) -> None:
        """
        Save the history of one channel and one waveform to a .bin file. This
        function is used after an acquisition using sequence trigger mode (with or
        without ultra segmentation) was performed.

        :param filename: is the name (without extension) of the file
        :param channel: is the channel number
        :param waveform: is the waveform number (typically 1)
        :raises RTO1024Error: if storing waveform times out
        """

        # turn on fast export
        self.com.write("EXPort:WAVeform:FASTexport ON")

        # enable history
        self.com.write("CHAN:HIST ON")
        sleep(self.config.wait_sec_enable_history)

        # turn off display
        self.local_display(False)

        # disable multichannel export
        self.com.write("EXPort:WAVeform:MULTichannel OFF")

        # select source channel and waveform
        self.com.write(f"EXPort:WAVeform:SOURce C{channel}W{waveform}")

        # set filename
        abs_win_path = PureWindowsPath(self.config.waveforms_path, filename)
        self.com.write(f"EXPort:WAVeform:NAME '{abs_win_path}.bin'")

        # enable waveform logging
        self.com.write("EXPort:WAVeform:DLOGging ON")

        # clear status, to get *OPC working
        self.com.write("*CLS")
        sleep(self.config.wait_sec_short_pause)

        # play waveform to start exporting
        self.com.write("CHANnel:HISTory:PLAY", "*OPC")
        is_done = self.wait_operation_complete(self.config.command_timeout_seconds)

        # disable fast export
        self.com.write("EXPort:WAVeform:FASTexport OFF")

        # enable local display
        self.local_display(True)

        if not is_done:
            logger.error("Storing waveform timed out.")
            raise RTO1024Error("Storing waveform timed out.")

        # check filelist
        filenames: List[str] = [
            file_info[0]
            for file_info in self.list_directory(self.config.waveforms_path)
        ]
        if (filename + ".Wfm.bin") not in filenames or (
            filename + ".bin"
        ) not in filenames:
            err_msg = f"Waveform {filename} could not be stored."
            logger.error(err_msg)
            raise RTO1024Error(err_msg)

        logger.info(f"Waveform {filename} stored successfully.")

    def run_continuous_acquisition(self) -> None:
        """
        Start acquiring continuously.
        """

        self.com.write("RUN")

    def run_single_acquisition(self) -> None:
        """
        Start a single or Nx acquisition.
        """

        self.com.write("SINGle")

    def stop_acquisition(self) -> None:
        """
        Stop any acquisition.
        """

        self.com.write("STOP")

    def prepare_ultra_segmentation(self) -> None:
        """
        Make ready for a new acquisition in ultra segmentation mode. This function
        does one acquisition without ultra segmentation to clear the history and
        prepare for a new measurement.
        """

        # disable ultra segmentation
        self.com.write("ACQuire:SEGMented:STATe OFF")

        # go to AUTO trigger mode to let the scope running freely
        self.set_trigger_mode("AUTO")

        # pause a little bit
        sleep(self.config.wait_sec_short_pause)

        # start acquisition and wait for two seconds
        self.run_continuous_acquisition()
        sleep(self.config.wait_sec_post_acquisition_start)

        # stop acquisition
        self.stop_acquisition()

        # set normal trigger mode
        self.set_trigger_mode("NORMAL")

        # enable ultra segmentation
        self.com.write("ACQuire:SEGMented:STATe ON")

        # set to maximum amount of acquisitions
        self.com.write("ACQuire:SEGMented:MAX ON")

        # final pause to secure the state
        sleep(self.config.wait_sec_short_pause)

    def save_configuration(self, filename: str) -> None:
        r"""
        Save the current oscilloscope settings to a file.
        The filename has to be specified without path and '.dfl' extension, the file
        will be saved to the configured settings directory.

        **Information from the manual**
        `SAVe` stores the current instrument settings under the
        specified number in an intermediate memory. The settings can
        be recalled using the command `\*RCL` with the associated
        number. To transfer the stored instrument settings to a file,
        use `MMEMory:STORe:STATe` .

        :param filename: is the name of the settings file without path and extension
        """

        abs_win_path = PureWindowsPath(self.config.settings_path, filename)
        self.com.write(f"MMEMory:SAV '{abs_win_path}.dfl'")

    def load_configuration(self, filename: str) -> None:
        r"""
        Load current settings from a configuration file. The filename has to be
        specified without base directory and '.dfl' extension.

        **Information from the manual**
        `ReCaLl` calls up the instrument settings from an intermediate
        memory identified by the specified number. The instrument
        settings can be stored to this memory using the command
        `\*SAV` with the associated number. It also activates the
        instrument settings which are stored in a file and loaded
        using `MMEMory:LOAD:STATe` .

        :param filename: is the name of the settings file without path and extension
        """

        abs_win_path = PureWindowsPath(self.config.settings_path, filename)
        self.com.write(f"MMEMory:RCL '{abs_win_path}.dfl'")

    def get_timestamps(self) -> List[float]:
        """
        Gets the timestamps of all recorded frames in the history and returns them as
        a list of floats.

        :return: list of timestamps in [s]
        :raises RTO1024Error: if the timestamps are invalid
        """

        # disable local display (it is faster)
        self.local_display(False)

        # enable the history
        self.com.write("CHANnel:WAVeform:HISTory:STATe 1")

        # get the number of acquisitions
        number_acquisitions = int(self.com.query("ACQuire:AVAilable?"))

        # get the relative timestamp for each acquisition
        timestamps_relative = []

        # loop over all acquisitions. Note: Negative index up to 0!
        for index in range(-number_acquisitions + 1, 1):
            # switch to acquisition frame in history
            self.com.write(f"CHANnel:WAVeform:HISTory:CURRent {index}")

            # wait until frame is loaded
            sleep(self.config.wait_sec_short_pause)

            # store relative timestamp
            timestamps_relative.append(
                float(self.com.query("CHANnel:WAVeform:HISTory:TSRelative?"))
            )

            # wait until timestamp is stored
            sleep(self.config.wait_sec_short_pause)

        # re-enable local display
        self.local_display(True)

        # check validity of acquired timestamps. If they are read out too fast,
        # there may be the same value two times in the list.
        if len(set(timestamps_relative)) != len(timestamps_relative):
            logger.error("Timestamps are not valid, there are doubled values.")
            raise RTO1024Error("Timestamps are not valid, there are doubled values.")

        logger.info("Timestamps successfully transferred.")
        return timestamps_relative

    def activate_measurements(
        self,
        meas_n: int,
        source: str,
        measurements: List[str],
        category: str = "AMPTime",
    ):
        """
        Activate the list of 'measurements' of the waveform 'source' in the
        measurement box number 'meas_n'. The list 'measurements' starts with the main
        measurement and continues with additional measurements of the same 'category'.

        :param meas_n: measurement number 1..8
        :param source: measurement source, for example C1W1
        :param measurements: list of measurements, the first one will be the main
            measurement.
        :param category: the category of measurements, by default AMPTime
        """

        self.com.write(f"MEAS{meas_n}:ENAB ON")
        self.com.write(f"MEAS{meas_n}:SOUR {source}")
        self.com.write(f"MEAS{meas_n}:CAT {category}")
        if measurements:
            self.com.write(f"MEAS{meas_n}:MAIN {measurements.pop(0)}")
        while measurements:
            self.com.write(f"MEAS{meas_n}:ADD {measurements.pop(0)}, ON")

    def read_measurement(self, meas_n: int, name: str) -> float:
        """

        :param meas_n: measurement number 1..8
        :param name: measurement name, for example "MAX"
        :return: measured value
        """

        return float(self.com.query(f"MEAS{meas_n}:RES? {name}"))
