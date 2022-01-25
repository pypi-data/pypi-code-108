from array import array
from ctypes import c_void_p, c_double
from .api import api
from .const import *
from .library import library
from .device import Device


class Generator(Device):
    """"""

    def __init__(self, handle):
        super(Generator, self).__init__(handle)

    def _get_connector_type(self):
        """ Output connector type. """
        value = api.GenGetConnectorType(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_is_differential(self):
        """ Check whether the output is differential. """
        value = api.GenIsDifferential(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_impedance(self):
        """ Output impedance. """
        value = api.GenGetImpedance(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_resolution(self):
        """ DAC resolution. """
        value = api.GenGetResolution(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_output_value_min(self):
        """ Minimum output value. """
        value = api.GenGetOutputValueMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_output_value_max(self):
        """ Maximum output value. """
        value = api.GenGetOutputValueMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def get_output_value_min_max(self, min, max):
        """ Get the minimum and/or maximum output value.

        :param min: A pointer to a memory location for the minimum value, or ``None.``
        :param max: A pointer to a memory location for the maximum value, or ``None.``
        """
        api.GenGetOutputValueMinMax(self._handle, min, max)
        library.check_last_status_raise_on_error()

    def _get_is_controllable(self):
        """ Check whether a specified generator can be controlled. """
        value = api.GenIsControllable(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_running(self):
        """ Check whether the generator is running. """
        value = api.GenIsRunning(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_status(self):
        """ Current signal generation status """
        value = api.GenGetStatus(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_output_on(self):
        """ Check whether a specified generator is enabled """
        value = api.GenGetOutputOn(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_output_on(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.GenSetOutputOn(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_has_output_invert(self):
        """ Check whether the output can be inverted """
        value = api.GenHasOutputInvert(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_output_invert(self):
        """ Check whether the output is inverted """
        value = api.GenGetOutputInvert(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_output_invert(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.GenSetOutputInvert(self._handle, value)
        library.check_last_status_raise_on_error()

    def start(self):
        """ Start the signal generation.

        """
        api.GenStart(self._handle)
        library.check_last_status_raise_on_error()

    def stop(self):
        """ Stop the signal generation.

        """
        api.GenStop(self._handle)
        library.check_last_status_raise_on_error()

    def _get_signal_types(self):
        """ Supported signal types. """
        value = api.GenGetSignalTypes(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_signal_type(self):
        """ Currently selected signal type. """
        value = api.GenGetSignalType(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_signal_type(self, value):
        api.GenSetSignalType(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_has_amplitude(self):
        """ Check whether the current signal type supports controlling the signal amplitude. """
        value = api.GenHasAmplitude(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_amplitude_min(self):
        """ Minimum signal amplitude for the current signal type. """
        value = api.GenGetAmplitudeMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_amplitude_max(self):
        """ Maximum signal amplitude for the current signal type. """
        value = api.GenGetAmplitudeMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_amplitude(self):
        """ Currently set signal amplitude. """
        value = api.GenGetAmplitude(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_amplitude(self, value):
        api.GenSetAmplitude(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_amplitude(self, amplitude):
        """ Verify if a signal amplitude can be set, without actually setting the hardware itself.

        :param amplitude: The requested signal amplitude.
        :returns: The signal amplitude that would have been set, in Volt.
        """
        result = api.GenVerifyAmplitude(self._handle, amplitude)
        library.check_last_status_raise_on_error()
        return result

    def _get_amplitude_ranges(self):
        """ Supported amplitude ranges. """
        count = api.GenGetAmplitudeRanges(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_double * count)()
        api.GenGetAmplitudeRanges(self._handle, values, count)
        library.check_last_status_raise_on_error()
        return array('d', values)

    def _get_amplitude_range(self):
        """ Currently set amplitude range. """
        value = api.GenGetAmplitudeRange(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_amplitude_range(self, value):
        api.GenSetAmplitudeRange(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_amplitude_auto_ranging(self):
        """ Amplitude auto ranging setting. """
        value = api.GenGetAmplitudeAutoRanging(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_amplitude_auto_ranging(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.GenSetAmplitudeAutoRanging(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_has_offset(self):
        """ Check whether the current signal type supports controlling the signal offset. """
        value = api.GenHasOffset(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_offset_min(self):
        """ Minimum offset for the current signal type. """
        value = api.GenGetOffsetMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_offset_max(self):
        """ Maximum offset for the current signal type. """
        value = api.GenGetOffsetMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_offset(self):
        """ Current signal offset. """
        value = api.GenGetOffset(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_offset(self, value):
        api.GenSetOffset(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_offset(self, offset):
        """ Verify if a signal offset can be set, without actually setting the hardware itself.

        :param offset: The requested signal offset, in Volt.
        :returns: The signal offset that would have been set, in Volt.
        """
        result = api.GenVerifyOffset(self._handle, offset)
        library.check_last_status_raise_on_error()
        return result

    def _get_frequency_modes(self):
        """ Supported generator frequency modes. """
        value = api.GenGetFrequencyModes(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_frequency_mode(self):
        """ Current generator frequency mode """
        value = api.GenGetFrequencyMode(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_frequency_mode(self, value):
        api.GenSetFrequencyMode(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_has_frequency(self):
        """ Check whether the current signal type and frequency mode support controlling the signal/sample frequency. """
        value = api.GenHasFrequency(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_frequency_min(self):
        """ Minimum signal/sample frequency with the current frequency mode. """
        value = api.GenGetFrequencyMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_frequency_max(self):
        """ Maximum signal/sample frequency with the current frequency mode and signal type. """
        value = api.GenGetFrequencyMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def get_frequency_min_max(self, frequency_mode, min, max):
        """ Get the minimum and maximum signal/sample frequency for a specified frequency mode and the current signal type.

        :param frequency_mode: The requested generator frequency mode, a FM_* value.
        :param min: A pointer to a memory location for the minimum frequency, or ``None.``
        :param max: A pointer to a memory location for the maximum frequency, or ``None.``
        """
        api.GenGetFrequencyMinMax(self._handle, frequency_mode, min, max)
        library.check_last_status_raise_on_error()

    def _get_frequency(self):
        """ Current signal/sample frequency. """
        value = api.GenGetFrequency(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_frequency(self, value):
        api.GenSetFrequency(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_frequency(self, frequency):
        """ Verify if a signal/sample frequency can be set, without actually setting the hardware itself.

        :param frequency: The requested signal/sample frequency, in Hz.
        :returns: The signal/sample frequency that would have been set, in Hz.
        """
        result = api.GenVerifyFrequency(self._handle, frequency)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_phase(self):
        """ Check whether the specified generator and the current signal type support controlling the signal phase. """
        value = api.GenHasPhase(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_phase_min(self):
        """ Minimum signal phase. """
        value = api.GenGetPhaseMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_phase_max(self):
        """ Maximum signal phase. """
        value = api.GenGetPhaseMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_phase(self):
        """ Current signal phase. """
        value = api.GenGetPhase(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_phase(self, value):
        api.GenSetPhase(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_phase(self, phase):
        """ Verify if a phase can be set, without actually setting the hardware itself.

        :param phase: The requested signal phase, a number between ``0`` and ``1.``
        :returns: The signal phase that would have been set, a number between ``0`` and ``1.``
        """
        result = api.GenVerifyPhase(self._handle, phase)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_symmetry(self):
        """ Check whether the current signal type supports controlling the signal symmetry. """
        value = api.GenHasSymmetry(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_symmetry_min(self):
        """ Minimum signal symmetry. """
        value = api.GenGetSymmetryMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_symmetry_max(self):
        """ Maximum signal symmetry. """
        value = api.GenGetSymmetryMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_symmetry(self):
        """ Current signal symmetry. """
        value = api.GenGetSymmetry(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_symmetry(self, value):
        api.GenSetSymmetry(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_symmetry(self, symmetry):
        """ Verify if a symmetry can be set, without actually setting the hardware itself.

        :param symmetry: The requested signal symmetry, a number between ``0`` and ``1.``
        :returns: The signal symmetry that would have been set, a number between ``0`` and ``1.``
        """
        result = api.GenVerifySymmetry(self._handle, symmetry)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_width(self):
        """ Check whether the current signal type supports controlling the signal pulse width. """
        value = api.GenHasWidth(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_width_min(self):
        """ Minimum pulse width with the current signal frequency. """
        value = api.GenGetWidthMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_width_max(self):
        """ Maximum pulse width with the current signal frequency. """
        value = api.GenGetWidthMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_width(self):
        """ Current pulse width. """
        value = api.GenGetWidth(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_width(self, value):
        api.GenSetWidth(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_width(self, width):
        """ Verify if a pulse width can be set, without actually setting the hardware itself.

        :param width: The requested pulse width in seconds.
        :returns: The pulse width that would have been set, in seconds.
        """
        result = api.GenVerifyWidth(self._handle, width)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_edge_time(self):
        """ Check whether the current signal type supports controlling the edge times. """
        value = api.GenHasEdgeTime(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_leading_edge_time_min(self):
        """ Minimum leading edge time with the current pulse width and signal frequency. """
        value = api.GenGetLeadingEdgeTimeMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_leading_edge_time_max(self):
        """ Maximum leading edge time with the current pulse width and signal frequency. """
        value = api.GenGetLeadingEdgeTimeMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_leading_edge_time(self):
        """ Current leading edge time with the current pulse width and signal frequency. """
        value = api.GenGetLeadingEdgeTime(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_leading_edge_time(self, value):
        api.GenSetLeadingEdgeTime(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_leading_edge_time(self, leading_edge_time):
        """ Verify if a leading edge time can be set for the current signal type and signal frequency, without actually setting the hardware itself.

        :param leading_edge_time: The requested leading edge time in seconds.
        :returns: The leading edge time that would have been set, in seconds.
        .. versionadded:: 0.6
        """
        result = api.GenVerifyLeadingEdgeTime(self._handle, leading_edge_time)
        library.check_last_status_raise_on_error()
        return result

    def _get_trailing_edge_time_min(self):
        """ Minimum trailing edge time with the current pulse width and signal frequency. """
        value = api.GenGetTrailingEdgeTimeMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_trailing_edge_time_max(self):
        """ Maximum trailing edge time with the current pulse width and signal frequency. """
        value = api.GenGetTrailingEdgeTimeMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_trailing_edge_time(self):
        """ Current trailing edge time with the current pulse width and signal frequency. """
        value = api.GenGetTrailingEdgeTime(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_trailing_edge_time(self, value):
        api.GenSetTrailingEdgeTime(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_trailing_edge_time(self, trailing_edge_time):
        """ Verify if a trailing edge time can be set for the current signal type and signal frequency, without actually setting the hardware itself.

        :param trailing_edge_time: The requested trailing edge time in seconds.
        :returns: The trailing edge time that would have been set, in seconds.
        .. versionadded:: 0.6
        """
        result = api.GenVerifyTrailingEdgeTime(self._handle, trailing_edge_time)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_data(self):
        """ Check whether the current signal type supports controlling the Arbitrary waveform buffer. """
        value = api.GenHasData(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_data_length_min(self):
        """ Minimum length of the waveform buffer. """
        value = api.GenGetDataLengthMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_length_max(self):
        """ Maximum length of the waveform buffer. """
        value = api.GenGetDataLengthMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_length(self):
        """ Length of the currently loaded waveform pattern. """
        value = api.GenGetDataLength(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def verify_data_length(self, data_length):
        """ Verify if a specified length of the waveform buffer for the current signal type can be set, without actually setting the hardware itself.

        :param data_length: The requested waveform buffer length in samples.
        :returns: The waveform buffer length that would have been set, in samples.
        """
        result = api.GenVerifyDataLength(self._handle, data_length)
        library.check_last_status_raise_on_error()
        return result

    def set_data(self, data):
        """ Load a waveform pattern into the waveform buffer.

        :param data: :class:`array.array` of floats, the waveform data.
        """
        if isinstance(data, array) and data.typecode == 'f':
            data_ptr = c_void_p(data.buffer_info()[0])
            data_ptr.__ref = data
            api.GenSetData(self._handle, data_ptr, len(data))
            library.check_last_status_raise_on_error()
        else:
            raise Exception('Invalid data, must be array.array with typecode = `f`')

    def _get_data_raw_type(self):
        """ Raw data type. """
        value = api.GenGetDataRawType(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def get_data_raw_value_range(self, min, zero, max):
        """ Get raw data minimum, equal to zero and maximum values.

        :param min: Pointer to buffer for possible minimum raw data value, or ``None.``
        :param zero: Pointer to buffer for equal to zero raw data value, or ``None.``
        :param max: Pointer to buffer for possible maximum raw data value, or ``None.``
        """
        api.GenGetDataRawValueRange(self._handle, min, zero, max)
        library.check_last_status_raise_on_error()

    def _get_data_raw_value_min(self):
        """ Get maximum raw data value. """
        value = api.GenGetDataRawValueMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_value_zero(self):
        """ Get raw data value that equals zero. """
        value = api.GenGetDataRawValueZero(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_value_max(self):
        """ Get minimum raw data value. """
        value = api.GenGetDataRawValueMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def set_data_raw(self, buffer, sample_count):
        """ Load a waveform pattern into the waveform buffer.

        :param buffer: Pointer to buffer with waveform data.
        :param sample_count: Number of samples in buffer.
        """
        api.GenSetDataRaw(self._handle, buffer, sample_count)
        library.check_last_status_raise_on_error()

    def _get_modes(self):
        """ Supported generator modes for the current signal type and frequency mode. """
        value = api.GenGetModes(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_modes_native(self):
        """ :class:`array.array` of supported generator modes, regardless of the signal type and frequency mode. """
        value = api.GenGetModesNative(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_mode(self):
        """ Current generator mode. """
        value = api.GenGetMode(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_mode(self, value):
        api.GenSetMode(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_is_burst_active(self):
        """ Check whether a burst is active. """
        value = api.GenIsBurstActive(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_burst_count_min(self):
        """ Minimum burst count for the current generator mode. """
        value = api.GenGetBurstCountMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_count_max(self):
        """ Maximum burst count for the current generator mode. """
        value = api.GenGetBurstCountMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_count(self):
        """ Current burst count for the current generator mode. """
        value = api.GenGetBurstCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_burst_count(self, value):
        api.GenSetBurstCount(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_burst_sample_count_min(self):
        """ Minimum burst sample count for the current generator mode. """
        value = api.GenGetBurstSampleCountMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_sample_count_max(self):
        """ Maximum burst sample count for the current generator mode. """
        value = api.GenGetBurstSampleCountMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_sample_count(self):
        """ Current burst sample count for the current generator mode. """
        value = api.GenGetBurstSampleCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_burst_sample_count(self, value):
        api.GenSetBurstSampleCount(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_burst_segment_count_min(self):
        """ Minimum burst segment count for the current settings. """
        value = api.GenGetBurstSegmentCountMin(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_segment_count_max(self):
        """ Maximum burst segment count for the current settings. """
        value = api.GenGetBurstSegmentCountMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_burst_segment_count(self):
        """ Current burst segment count. """
        value = api.GenGetBurstSegmentCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_burst_segment_count(self, value):
        api.GenSetBurstSegmentCount(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_burst_segment_count(self, burst_segment_count):
        """ Verify if a burst segment count can be set, without actually setting the hardware itself.

        :param burst_segment_count: The requested burst segment count.
        :returns: The burst segment count that would have been set.
        """
        result = api.GenVerifyBurstSegmentCount(self._handle, burst_segment_count)
        library.check_last_status_raise_on_error()
        return result

    def set_callback_burst_completed(self, callback, data):
        """ Set a callback function which is called when the generator burst is completed.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.GenSetCallbackBurstCompleted(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_burst_completed(self, event):
            """ Set an event file descriptor which is set when the generator burst is completed.

            :param event: An event file descriptor. Use ``<0`` to disable.
            """
            api.GenSetEventBurstCompleted(self._handle, event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_burst_completed(self, event):
            """ Set an event object handle which is set when the generator burst is completed.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.GenSetEventBurstCompleted(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_message_burst_completed(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_GEN_BURSTCOMPLETED message is sent when the generator burst is completed.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.GenSetMessageBurstCompleted(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

    def set_callback_controllable_changed(self, callback, data):
        """ Set a callback function which is called when the generator controllable property changes.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.GenSetCallbackControllableChanged(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_controllable_changed(self, event):
            """ Set an event file descriptor which is set when the generator controllable property changes.

            :param event: An event file descriptor. Use ``<0`` to disable.
            """
            api.GenSetEventControllableChanged(self._handle, event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_controllable_changed(self, event):
            """ Set event object handle which is set when the generator controllable property changes.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.GenSetEventControllableChanged(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_message_controllable_changed(self, wnd, wparam, lparam):
            """ Set window handle to which a #WM_LIBTIEPIE_GEN_CONTROLLABLECHANGED message is sent when the generator controllable property changes.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.GenSetMessageControllableChanged(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

    connector_type = property(_get_connector_type)
    is_differential = property(_get_is_differential)
    impedance = property(_get_impedance)
    resolution = property(_get_resolution)
    output_value_min = property(_get_output_value_min)
    output_value_max = property(_get_output_value_max)
    is_controllable = property(_get_is_controllable)
    is_running = property(_get_is_running)
    status = property(_get_status)
    output_on = property(_get_output_on, _set_output_on)
    has_output_invert = property(_get_has_output_invert)
    output_invert = property(_get_output_invert, _set_output_invert)
    signal_types = property(_get_signal_types)
    signal_type = property(_get_signal_type, _set_signal_type)
    has_amplitude = property(_get_has_amplitude)
    amplitude_min = property(_get_amplitude_min)
    amplitude_max = property(_get_amplitude_max)
    amplitude = property(_get_amplitude, _set_amplitude)
    amplitude_ranges = property(_get_amplitude_ranges)
    amplitude_range = property(_get_amplitude_range, _set_amplitude_range)
    amplitude_auto_ranging = property(_get_amplitude_auto_ranging, _set_amplitude_auto_ranging)
    has_offset = property(_get_has_offset)
    offset_min = property(_get_offset_min)
    offset_max = property(_get_offset_max)
    offset = property(_get_offset, _set_offset)
    frequency_modes = property(_get_frequency_modes)
    frequency_mode = property(_get_frequency_mode, _set_frequency_mode)
    has_frequency = property(_get_has_frequency)
    frequency_min = property(_get_frequency_min)
    frequency_max = property(_get_frequency_max)
    frequency = property(_get_frequency, _set_frequency)
    has_phase = property(_get_has_phase)
    phase_min = property(_get_phase_min)
    phase_max = property(_get_phase_max)
    phase = property(_get_phase, _set_phase)
    has_symmetry = property(_get_has_symmetry)
    symmetry_min = property(_get_symmetry_min)
    symmetry_max = property(_get_symmetry_max)
    symmetry = property(_get_symmetry, _set_symmetry)
    has_width = property(_get_has_width)
    width_min = property(_get_width_min)
    width_max = property(_get_width_max)
    width = property(_get_width, _set_width)
    has_edge_time = property(_get_has_edge_time)
    leading_edge_time_min = property(_get_leading_edge_time_min)
    leading_edge_time_max = property(_get_leading_edge_time_max)
    leading_edge_time = property(_get_leading_edge_time, _set_leading_edge_time)
    trailing_edge_time_min = property(_get_trailing_edge_time_min)
    trailing_edge_time_max = property(_get_trailing_edge_time_max)
    trailing_edge_time = property(_get_trailing_edge_time, _set_trailing_edge_time)
    has_data = property(_get_has_data)
    data_length_min = property(_get_data_length_min)
    data_length_max = property(_get_data_length_max)
    data_length = property(_get_data_length)
    data_raw_type = property(_get_data_raw_type)
    data_raw_value_min = property(_get_data_raw_value_min)
    data_raw_value_zero = property(_get_data_raw_value_zero)
    data_raw_value_max = property(_get_data_raw_value_max)
    modes = property(_get_modes)
    modes_native = property(_get_modes_native)
    mode = property(_get_mode, _set_mode)
    is_burst_active = property(_get_is_burst_active)
    burst_count_min = property(_get_burst_count_min)
    burst_count_max = property(_get_burst_count_max)
    burst_count = property(_get_burst_count, _set_burst_count)
    burst_sample_count_min = property(_get_burst_sample_count_min)
    burst_sample_count_max = property(_get_burst_sample_count_max)
    burst_sample_count = property(_get_burst_sample_count, _set_burst_sample_count)
    burst_segment_count_min = property(_get_burst_segment_count_min)
    burst_segment_count_max = property(_get_burst_segment_count_max)
    burst_segment_count = property(_get_burst_segment_count, _set_burst_segment_count)
