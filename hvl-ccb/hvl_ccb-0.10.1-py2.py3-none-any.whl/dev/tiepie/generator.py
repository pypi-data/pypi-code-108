#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""

import logging

import libtiepie as ltp
from libtiepie import generator as ltp_gen

from ...utils.enum import NameEnum
from array import array
import numpy.typing as npt

from typing import (
    cast,
    Optional,
    Union,
)
from .base import (
    TiePieDeviceType,
    wrap_libtiepie_exception,
    _verify_via_libtiepie,
    _require_dev_handle,
)
from .utils import PublicPropertiesReprMixin
from .oscilloscope import TiePieOscilloscope
from ...utils.validation import (
    validate_bool,
    validate_number,
)

logger = logging.getLogger(__name__)


class TiePieGeneratorSignalType(NameEnum, init="value description"):  # type:ignore
    UNKNOWN = ltp.ST_UNKNOWN, "Unknown"
    SINE = ltp.ST_SINE, "Sine"
    TRIANGLE = ltp.ST_TRIANGLE, "Triangle"
    SQUARE = ltp.ST_SQUARE, "Square"
    DC = ltp.ST_DC, "DC"
    NOISE = ltp.ST_NOISE, "Noise"
    ARBITRARY = ltp.ST_ARBITRARY, "Arbitrary"
    PULSE = ltp.ST_PULSE, "Pulse"


class TiePieGeneratorConfigLimits:
    """
    Default limits for generator parameters.
    """

    def __init__(self, dev_gen: ltp_gen.Generator) -> None:
        self.frequency = (0, dev_gen.frequency_max)
        self.amplitude = (0, dev_gen.amplitude_max)
        self.offset = (None, dev_gen.offset_max)


class TiePieGeneratorConfig(PublicPropertiesReprMixin):
    """
    Generator's configuration with cleaning of values in properties setters.
    """

    def __init__(self, dev_gen: ltp_gen.Generator):
        self.dev_gen: ltp_gen.Generator = dev_gen
        self._waveform: Optional[npt.NDArray] = None
        self.param_lim: TiePieGeneratorConfigLimits = TiePieGeneratorConfigLimits(
            dev_gen=dev_gen
        )

    def clean_frequency(self, frequency: float) -> float:
        validate_number(
            "Frequency", frequency, limits=self.param_lim.frequency, logger=logger
        )
        frequency = _verify_via_libtiepie(self.dev_gen, "frequency", frequency)
        return float(frequency)

    @property
    def frequency(self) -> float:
        return self.dev_gen.frequency

    @frequency.setter
    def frequency(self, frequency: float) -> None:
        """
        Set signal generator frequency.
        :param frequency: Desired signal frequency in Hertz
        """
        frequency = self.clean_frequency(frequency)
        self.dev_gen.frequency = frequency
        logger.info(f"Generator frequency is set to {frequency} Hz.")

    def clean_amplitude(self, amplitude: float) -> float:
        validate_number(
            "Generator amplitude",
            amplitude,
            limits=self.param_lim.amplitude,
            logger=logger,
        )
        amplitude = _verify_via_libtiepie(self.dev_gen, "amplitude", amplitude)
        return float(amplitude)

    @property
    def amplitude(self) -> float:
        return self.dev_gen.amplitude

    @amplitude.setter
    def amplitude(self, amplitude: float) -> None:
        """
        Set signal generator amplitude (peak value).
        :param amplitude: in Volts
        """
        amplitude = self.clean_amplitude(amplitude)
        self.dev_gen.amplitude = amplitude
        logger.info(f"Generator amplitude is set to {amplitude} V.")

    def clean_offset(self, offset: float) -> float:
        validate_number(
            "Generator offset", offset, limits=self.param_lim.offset, logger=logger
        )
        offset = _verify_via_libtiepie(self.dev_gen, "offset", offset)
        return float(offset)

    @property
    def offset(self) -> float:
        return self.dev_gen.offset

    @offset.setter
    def offset(self, offset: float) -> None:
        """
        Set signal offset voltage.
        :param offset: in Volts.
        """
        offset = self.clean_offset(offset)
        self.dev_gen.offset = offset
        logger.info(f"Generator offset is set to {offset} V.")

    @staticmethod
    def clean_signal_type(
        signal_type: Union[int, TiePieGeneratorSignalType]
    ) -> TiePieGeneratorSignalType:
        return TiePieGeneratorSignalType(signal_type)

    @property
    def signal_type(self) -> TiePieGeneratorSignalType:
        return TiePieGeneratorSignalType(self.dev_gen.signal_type)

    @signal_type.setter
    def signal_type(self, signal_type: Union[int, TiePieGeneratorSignalType]) -> None:
        """
        Set signal type.
        :param signal_type: use TiePieGeneratorSignalType.SIGNAL_KEYWORD
        """
        self.dev_gen.signal_type = self.clean_signal_type(signal_type).value
        logger.info(f"Signal type is set to {signal_type}.")

    @staticmethod
    def clean_enabled(enabled: bool) -> bool:
        validate_bool("channel enabled", enabled, logger=logger)
        return enabled

    @property
    def enabled(self) -> bool:
        return self.dev_gen.output_on

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Enable generator (note: this will not yet start the signal generation)
        :param enabled: if 'True', generator is enabled
        """
        self.dev_gen.output_on = self.clean_enabled(enabled)
        if enabled:
            msg = "enabled"
        else:
            msg = "disabled"
        logger.info(f"Generator is set to {msg}.")

    def clean_waveform(self, waveform: npt.NDArray) -> npt.NDArray:
        validate_number("Waveform", waveform, (-1, 1), logger=logger)
        waveform = waveform.squeeze()
        set_data_length = _verify_via_libtiepie(
            self.dev_gen, "data_length", waveform.size
        )
        if waveform.ndim != 1:
            msg = "Waveform array must be 1-dimensional."
            logger.error(msg)
            raise ValueError(msg)
        if set_data_length != waveform.size:
            msg = (
                f"Waveform with {waveform.size} samples not possible "
                f"(max. is {set_data_length})."
            )
            logger.error(msg)
            raise ValueError(msg)
        return waveform

    @property
    def waveform(self) -> Optional[npt.NDArray]:
        return self._waveform

    @waveform.setter
    def waveform(self, waveform: npt.NDArray):
        """
        Set arbitrary waveform for signal generation
        (choose TiePieGeneratorSignalType.ARBITRARY)
        :param waveform: desired waveform as a numpy array. The array will be scaled
        by a multiplicative factor such that its absolute maximum value is 1. The
        chosen 'amplitude' will thus be the absolute peak value of the generated
        waveform.
        """
        waveform = self.clean_waveform(waveform)
        self._waveform = waveform
        waveform_array = array("f")
        waveform_array.fromlist(waveform.tolist())
        self.dev_gen.set_data(waveform_array)
        logger.info("Arbitrary waveform data loaded")


class TiePieGeneratorMixin:
    """
    TiePie Generator sub-device.

    A wrapper for the `libtiepie.generator.Generator` class. To be mixed in with
    `TiePieOscilloscope` base class.
    """

    def __init__(self, com, dev_config):
        super().__init__(com, dev_config)

        self._gen: Optional[ltp_gen.Generator] = None

        self.config_gen: Optional[TiePieGeneratorConfig] = None
        """
        Generator's dynamical configuration.
        """

    @_require_dev_handle(TiePieDeviceType.GENERATOR)
    def _gen_config_setup(self) -> None:
        """
        Setup dynamical configuration for the connected generator.
        """
        self.config_gen = TiePieGeneratorConfig(
            dev_gen=self._gen,
        )

    def _gen_config_teardown(self) -> None:
        self.config_gen = None

    def _gen_close(self) -> None:
        if self._gen is not None:
            del self._gen
            self._gen = None

    def start(self) -> None:
        """
        Start the Generator.
        """
        super().start()  # type: ignore
        logger.info("Starting generator")

        self._gen = cast(TiePieOscilloscope, self)._get_device_by_serial_number(
            TiePieDeviceType.GENERATOR
        )
        self._gen_config_setup()

    @wrap_libtiepie_exception
    def stop(self) -> None:
        """
        Stop the generator.
        """
        logger.info("Stopping generator")

        self._gen_config_teardown()
        self._gen_close()

        super().stop()  # type: ignore

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.GENERATOR)
    def generator_start(self):
        """
        Start signal generation.
        """
        self._gen.start()
        logger.info("Starting signal generation")

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.GENERATOR)
    def generator_stop(self):
        """
        Stop signal generation.
        """
        self._gen.stop()
        logger.info("Stopping signal generation")
