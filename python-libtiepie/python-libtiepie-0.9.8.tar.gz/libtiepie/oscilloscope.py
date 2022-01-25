from array import array
from ctypes import c_uint8, c_float
from .api import api
from .const import *
from .utils import *
from .library import library
from .device import Device
from .oscilloscopechannels import OscilloscopeChannels
from .exceptions import *


class Oscilloscope(Device):
    """"""

    def __init__(self, handle):
        super(Oscilloscope, self).__init__(handle)
        self._channels = OscilloscopeChannels(handle)

    def _get_channels(self):
        return self._channels

    def get_data(self, count=None, raw=False):
        """ Get the measurement data for enabled channels.

        :param count: Number of samples to read, defaults to all.
        :param raw: Get raw data.

        :returns: `list` of `array.array`'s with sample data.
        """
        if not self.is_data_ready:
            raise UnsuccessfulError()

        channel_count = len(self.channels)

        # Calculate valid data start/length:
        if self._measure_mode == MM_BLOCK:
            length = int(self._record_length - round(self._pre_sample_ratio * self._record_length) + self.valid_pre_sample_count)
            start = self._record_length - length
        else:
            length = self._record_length
            start = 0

        if (count is not None) and (count >= 0) and (count < length):
            length = count

        # Create pointer array:
        pointers = api.HlpPointerArrayNew(channel_count)

        try:
            # Allocate memory and fill pointer array:
            result = [None] * channel_count
            for i in range(channel_count):
                if self._active_channels[i]:
                    if raw:
                        raw_type = self.channels[i].data_raw_type
                        if raw_type == DATARAWTYPE_INT8:
                            result[i] = array('b', [0]) * length
                        elif raw_type == DATARAWTYPE_INT16:
                            result[i] = array('h', [0]) * length
                        elif raw_type == DATARAWTYPE_INT32:
                            result[i] = array('l', [0]) * length
                        elif raw_type == DATARAWTYPE_INT64:
                            result[i] = array('q', [0]) * length
                        elif raw_type == DATARAWTYPE_UINT8:
                            result[i] = array('B', [0]) * length
                        elif raw_type == DATARAWTYPE_UINT16:
                            result[i] = array('H', [0]) * length
                        elif raw_type == DATARAWTYPE_UINT32:
                            result[i] = array('L', [0]) * length
                        elif raw_type == DATARAWTYPE_UINT64:
                            result[i] = array('Q', [0]) * length
                        elif raw_type == DATARAWTYPE_FLOAT32:
                            result[i] = array('f', [0]) * length
                        elif raw_type == DATARAWTYPE_FLOAT64:
                            result[i] = array('d', [0]) * length
                        else:
                            raise UnsuccessfulError()
                    else:
                        result[i] = array('f', [0]) * length
                    api.HlpPointerArraySet(pointers, i, cast(result[i].buffer_info()[0], c_void_p))

            # Get the data:
            if raw:
                api.ScpGetDataRaw(self._handle, pointers, channel_count, start, length)
            else:
                api.ScpGetData(self._handle, pointers, channel_count, start, length)
            library.check_last_status_raise_on_error()
        finally:
            # Delete pointer array:
            api.HlpPointerArrayDelete(pointers)

        return result

    def _get_valid_pre_sample_count(self):
        """ Number of valid pre samples in the measurement. """
        value = api.ScpGetValidPreSampleCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def get_data_raw(self, buffers, channel_count, start_index, sample_count):
        """ Get raw measurement data.

        :param buffers: Pointer to buffer with pointers to buffer for channel data, pointer buffer may contain ``None`` pointers.
        :param channel_count: Number of pointers in pointer buffer.
        :param start_index: Position in record to start reading.
        :param sample_count: Number of samples to read.
        :returns: Number of samples read.
        """
        result = api.ScpGetDataRaw(self._handle, buffers, channel_count, start_index, sample_count)
        library.check_last_status_raise_on_error()
        return result

    def get_data_async_completed(self):
        """ Check whether the data download is completed.

        :returns: ``True`` if completed, ``False`` otherwise.
        """
        result = api.ScpIsGetDataAsyncCompleted(self._handle)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def start_get_data_async(self, buffers, channel_count, start_index, sample_count):
        """ Start the download of measurement data for specified channels.

        :param buffers: A pointer to a buffer with pointers to buffers for channel data, the pointer buffer may contain ``None`` pointers.
        :param channel_count: The number of pointers in the pointer buffer.
        :param start_index: The position in the record to start reading.
        :param sample_count: The number of samples to read.
        .. versionadded:: 0.6
        """
        api.ScpStartGetDataAsync(self._handle, buffers, channel_count, start_index, sample_count)
        library.check_last_status_raise_on_error()

    def start_get_data_async_raw(self, buffers, channel_count, start_index, sample_count):
        """ Start the download of raw measurement data for specified channels.

        :param buffers: Pointer to buffer with pointers to buffer for channel data, pointer buffer may contain ``None`` pointers.
        :param channel_count: Number of pointers in pointer buffer.
        :param start_index: Position in record to start reading.
        :param sample_count: Number of samples to read.
        .. versionadded:: 0.6
        """
        api.ScpStartGetDataAsyncRaw(self._handle, buffers, channel_count, start_index, sample_count)
        library.check_last_status_raise_on_error()

    def cancel_get_data_async(self):
        """ Cancel the download of measurement data.

        :returns: ``True`` if successful, ``False`` otherwise.
        .. versionadded:: 0.6
        """
        result = api.ScpCancelGetDataAsync(self._handle)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def set_callback_data_ready(self, callback, data):
        """ Set a callback function which is called when the oscilloscope has new measurement data ready.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.ScpSetCallbackDataReady(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    def set_callback_data_overflow(self, callback, data):
        """ Set a callback function which is called when the oscilloscope streaming measurement caused an data overflow.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.ScpSetCallbackDataOverflow(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    def set_callback_connection_test_completed(self, callback, data):
        """ Set a callback function which is called when the oscilloscope connection test is completed.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.ScpSetCallbackConnectionTestCompleted(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    def set_callback_triggered(self, callback, data):
        """ Set a callback function which is called when the oscilloscope is triggered.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.ScpSetCallbackTriggered(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_data_ready(self, event):
            """ Set an event file descriptor which is set when the oscilloscope has new measurement data ready.

            :param event: An event file descriptor. Use ``&lt;0`` to disable.
            """
            api.ScpSetEventDataReady(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_data_overflow(self, event):
            """ Set an event file descriptor which is set when the oscilloscope streaming measurement caused an data overflow.

            :param event: An event file descriptor. Use ``&lt;0`` to disable.
            """
            api.ScpSetEventDataOverflow(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_connection_test_completed(self, event):
            """ Set an event file descriptor which is set when the oscilloscope connection test is completed.

            :param event: An event file descriptor. Use ``&lt;0`` to disable.
            """
            api.ScpSetEventConnectionTestCompleted(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_triggered(self, event):
            """ Set an event file descriptor which is set when the oscilloscope is triggered.

            :param event: An event file descriptor. Use ``&lt;0`` to disable.
            """
            api.ScpSetEventTriggered(self._handle, event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_data_ready(self, event):
            """ Set an event object handle which is set when the oscilloscope has new measurement data ready.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.ScpSetEventDataReady(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_data_overflow(self, event):
            """ Set an event object handle which is set when the oscilloscope streaming measurement caused an data overflow.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.ScpSetEventDataOverflow(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_connection_test_completed(self, event):
            """ Set an event object handle which is set when the oscilloscope connection test is completed.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.ScpSetEventConnectionTestCompleted(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_triggered(self, event):
            """ Set an event object handle which is set when the oscilloscope is triggered.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.ScpSetEventTriggered(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_message_data_ready(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_SCP_DATAREADY message is sent when the oscilloscope has new measurement data ready.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.ScpSetMessageDataReady(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

        def set_message_data_overflow(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_SCP_DATAOVERFLOW message is sent when the oscilloscope streaming measurement caused an data overflow.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.ScpSetMessageDataOverflow(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

        def set_message_connection_test_completed(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_SCP_CONNECTIONTESTCOMPLETED message is sent when the oscilloscope connection test is completed.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.ScpSetMessageConnectionTestCompleted(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

        def set_message_triggered(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_SCP_TRIGGERED message is sent when the oscilloscope is triggered.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.ScpSetMessageTriggered(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

    def start(self):
        """ Start a single measurement. """
        if self.is_running:
            raise MeasurementRunningError()

        # Cache some values, needed for getting data:
        self._measure_mode = self.measure_mode
        self._record_length = self.record_length
        if self._measure_mode == MM_BLOCK:
            self._pre_sample_ratio = self.pre_sample_ratio
        self._active_channels = []
        for ch in self.channels:
            self._active_channels.append(ch.enabled)

        result = api.ScpStart(self._handle)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def stop(self):
        """ Stop a running measurement.

        """
        api.ScpStop(self._handle)
        library.check_last_status_raise_on_error()

    def force_trigger(self):
        """ Force a trigger.

        """
        api.ScpForceTrigger(self._handle)
        library.check_last_status_raise_on_error()

    def _get_measure_modes(self):
        """ Supported measure modes. """
        value = api.ScpGetMeasureModes(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_measure_mode(self):
        """ Current measure mode. """
        value = api.ScpGetMeasureMode(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_measure_mode(self, value):
        api.ScpSetMeasureMode(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_is_running(self):
        """ Check whether the oscilloscope is currently measuring. """
        value = api.ScpIsRunning(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_triggered(self):
        """ Check whether the oscilloscope has triggered. """
        value = api.ScpIsTriggered(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_time_out_triggered(self):
        """ Check whether the trigger was caused by the trigger time out. """
        value = api.ScpIsTimeOutTriggered(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_force_triggered(self):
        """ Check whether the trigger was caused by ScpForceTrigger. """
        value = api.ScpIsForceTriggered(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_data_ready(self):
        """ Check whether new, unread measured data is available. """
        value = api.ScpIsDataReady(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_data_overflow(self):
        """ Check whether a data overflow has occurred. """
        value = api.ScpIsDataOverflow(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_auto_resolution_modes(self):
        """ Supported auto resolution modes. """
        value = api.ScpGetAutoResolutionModes(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_auto_resolution_mode(self):
        """ Current auto resolution mode. """
        value = api.ScpGetAutoResolutionMode(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_auto_resolution_mode(self, value):
        api.ScpSetAutoResolutionMode(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_resolutions(self):
        """ :class:`array.array` of supported resolutions. """
        count = api.ScpGetResolutions(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_uint8 * count)()
        api.ScpGetResolutions(self._handle, values, count)
        library.check_last_status_raise_on_error()
        return array('B', values)

    def _get_resolution(self):
        """ Current resolution. """
        value = api.ScpGetResolution(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_resolution(self, value):
        api.ScpSetResolution(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_is_resolution_enhanced(self):
        """ Check whether the currently selected resolution is enhanced or a native resolution of the hardware. """
        value = api.ScpIsResolutionEnhanced(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_clock_sources(self):
        """ Supported clock sources. """
        value = api.ScpGetClockSources(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_clock_source(self):
        """ Currently selected clock source. """
        value = api.ScpGetClockSource(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_clock_source(self, value):
        api.ScpSetClockSource(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_clock_source_frequencies(self):
        """ :class:`array.array` of supported clock source frequencies. """
        count = api.ScpGetClockSourceFrequencies(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_double * count)()
        api.ScpGetClockSourceFrequencies(self._handle, values, count)
        library.check_last_status_raise_on_error()
        return array('d', values)

    def _get_clock_source_frequency(self):
        """ Current clock source frequency. """
        value = api.ScpGetClockSourceFrequency(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_clock_source_frequency(self, value):
        api.ScpSetClockSourceFrequency(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_clock_outputs(self):
        """ Supported clock outputs. """
        value = api.ScpGetClockOutputs(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_clock_output(self):
        """ Currently selected clock output. """
        value = api.ScpGetClockOutput(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_clock_output(self, value):
        api.ScpSetClockOutput(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_clock_output_frequencies(self):
        """ :class:`array.array` of supported clock output frequencies. """
        count = api.ScpGetClockOutputFrequencies(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_double * count)()
        api.ScpGetClockOutputFrequencies(self._handle, values, count)
        library.check_last_status_raise_on_error()
        return array('d', values)

    def _get_clock_output_frequency(self):
        """ Current clock output frequency. """
        value = api.ScpGetClockOutputFrequency(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_clock_output_frequency(self, value):
        api.ScpSetClockOutputFrequency(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_sample_frequency_max(self):
        """ Maximum supported sample frequency. """
        value = api.ScpGetSampleFrequencyMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_sample_frequency(self):
        """ Currently selected sample frequency. """
        value = api.ScpGetSampleFrequency(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_sample_frequency(self, value):
        api.ScpSetSampleFrequency(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_sample_frequency(self, sample_frequency):
        """ Verify if a required sample frequency can be set, without actually setting the hardware itself.

        :param sample_frequency: The required sample frequency, in Hz.
        :returns: The sample frequency that would have been set, if ScpSetSampleFrequency() was used.
        """
        result = api.ScpVerifySampleFrequency(self._handle, sample_frequency)
        library.check_last_status_raise_on_error()
        return result

    def _get_record_length_max(self):
        """ Maximum supported record length. """
        value = api.ScpGetRecordLengthMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_record_length(self):
        """ Currently selected record length. """
        value = api.ScpGetRecordLength(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_record_length(self, value):
        api.ScpSetRecordLength(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_record_length(self, record_length):
        """ Verify if a required record length can be set, without actually setting the hardware itself.

        :param record_length: The required record length, in samples.
        :returns: The record length that would have been set, if ScpSetRecordLength() was used.
        """
        result = api.ScpVerifyRecordLength(self._handle, record_length)
        library.check_last_status_raise_on_error()
        return result

    def _get_pre_sample_ratio(self):
        """ Current pre sample ratio. """
        value = api.ScpGetPreSampleRatio(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_pre_sample_ratio(self, value):
        api.ScpSetPreSampleRatio(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_segment_count_max(self):
        """ Maximum supported number of segments. """
        value = api.ScpGetSegmentCountMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_segment_count(self):
        """ Currently selected number of segments. """
        value = api.ScpGetSegmentCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_segment_count(self, value):
        api.ScpSetSegmentCount(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_segment_count(self, segment_count):
        """ Verify if a required number of segments can be set, without actually setting the hardware itself.

        :param segment_count: The required number of segments.
        :returns: The actually number of segments that would have been set, if ScpSetSegmentCount() was used.
        """
        result = api.ScpVerifySegmentCount(self._handle, segment_count)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_trigger(self):
        """ Check whether the oscilloscope has trigger support with the currently selected measure mode. """
        value = api.ScpHasTrigger(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_trigger_time_out(self):
        """ Currently selected trigger time out in seconds. """
        value = api.ScpGetTriggerTimeOut(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_trigger_time_out(self, value):
        api.ScpSetTriggerTimeOut(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_trigger_time_out(self, time_out):
        """ Verify if a required trigger time out can be set, without actually setting the hardware itself.

        :param time_out: The required trigger time out in seconds, or #TO_INFINITY.
        :returns: The trigger time out that would have been set, if ScpSetTriggerTimeOut() was used.
        """
        result = api.ScpVerifyTriggerTimeOut(self._handle, time_out)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_trigger_delay(self):
        """ Check whether the oscilloscope has trigger delay support with the currently selected measure mode. """
        value = api.ScpHasTriggerDelay(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_trigger_delay_max(self):
        """ Maximum trigger delay in seconds, for the currently selected measure mode and sample frequency. """
        value = api.ScpGetTriggerDelayMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_trigger_delay(self):
        """ Currently selected trigger delay in seconds. """
        value = api.ScpGetTriggerDelay(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_trigger_delay(self, value):
        api.ScpSetTriggerDelay(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_trigger_delay(self, delay):
        """ Verify if a required trigger delay can be set, without actually setting the hardware itself.

        :param delay: The required trigger delay in seconds.
        :returns: The trigger delay that would have been set, if ScpSetTriggerDelay() was used.
        """
        result = api.ScpVerifyTriggerDelay(self._handle, delay)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_trigger_hold_off(self):
        """ Check whether the oscilloscope has trigger hold off support with the currently selected measure mode. """
        value = api.ScpHasTriggerHoldOff(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_trigger_hold_off_count_max(self):
        """ Maximum trigger hold off count in samples. """
        value = api.ScpGetTriggerHoldOffCountMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_trigger_hold_off_count(self):
        """ Trigger hold off count in samples. """
        value = api.ScpGetTriggerHoldOffCount(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_trigger_hold_off_count(self, value):
        api.ScpSetTriggerHoldOffCount(self._handle, value)
        library.check_last_status_raise_on_error()

    def _get_has_connection_test(self):
        """ Check whether the specified oscilloscope supports connection testing. """
        value = api.ScpHasConnectionTest(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def start_connection_test(self):
        """ Perform a connection test on all enabled channels.

        """
        api.ScpStartConnectionTest(self._handle)
        library.check_last_status_raise_on_error()

    def _get_is_connection_test_completed(self):
        """ Check whether the connection test on a specified oscilloscope is completed. """
        value = api.ScpIsConnectionTestCompleted(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def get_connection_test_data(self):
        """ Get the connection test result data.

        :returns: :class:`list` of :class:`.TriState` values.
        """
        if not self.is_connection_test_completed:
            raise UnsuccessfulError()

        channel_count = len(self.channels)

        # Allocate memory:
        buffer = (c_uint8 * channel_count)()

        # Get the data:
        channel_count = api.ScpGetConnectionTestData(self._handle, buffer, channel_count)
        library.check_last_status_raise_on_error()

        # Create result array:
        result = []
        for i in range(channel_count):
            result.append(convert_tristate(buffer[i]))

        return result

    valid_pre_sample_count = property(_get_valid_pre_sample_count)
    measure_modes = property(_get_measure_modes)
    measure_mode = property(_get_measure_mode, _set_measure_mode)
    is_running = property(_get_is_running)
    is_triggered = property(_get_is_triggered)
    is_time_out_triggered = property(_get_is_time_out_triggered)
    is_force_triggered = property(_get_is_force_triggered)
    is_data_ready = property(_get_is_data_ready)
    is_data_overflow = property(_get_is_data_overflow)
    auto_resolution_modes = property(_get_auto_resolution_modes)
    auto_resolution_mode = property(_get_auto_resolution_mode, _set_auto_resolution_mode)
    resolutions = property(_get_resolutions)
    resolution = property(_get_resolution, _set_resolution)
    is_resolution_enhanced = property(_get_is_resolution_enhanced)
    clock_sources = property(_get_clock_sources)
    clock_source = property(_get_clock_source, _set_clock_source)
    clock_source_frequencies = property(_get_clock_source_frequencies)
    clock_source_frequency = property(_get_clock_source_frequency, _set_clock_source_frequency)
    clock_outputs = property(_get_clock_outputs)
    clock_output = property(_get_clock_output, _set_clock_output)
    clock_output_frequencies = property(_get_clock_output_frequencies)
    clock_output_frequency = property(_get_clock_output_frequency, _set_clock_output_frequency)
    sample_frequency_max = property(_get_sample_frequency_max)
    sample_frequency = property(_get_sample_frequency, _set_sample_frequency)
    record_length_max = property(_get_record_length_max)
    record_length = property(_get_record_length, _set_record_length)
    pre_sample_ratio = property(_get_pre_sample_ratio, _set_pre_sample_ratio)
    segment_count_max = property(_get_segment_count_max)
    segment_count = property(_get_segment_count, _set_segment_count)
    has_trigger = property(_get_has_trigger)
    trigger_time_out = property(_get_trigger_time_out, _set_trigger_time_out)
    has_trigger_delay = property(_get_has_trigger_delay)
    trigger_delay_max = property(_get_trigger_delay_max)
    trigger_delay = property(_get_trigger_delay, _set_trigger_delay)
    has_trigger_hold_off = property(_get_has_trigger_hold_off)
    trigger_hold_off_count_max = property(_get_trigger_hold_off_count_max)
    trigger_hold_off_count = property(_get_trigger_hold_off_count, _set_trigger_hold_off_count)
    has_connection_test = property(_get_has_connection_test)
    is_connection_test_completed = property(_get_is_connection_test_completed)
    channels = property(_get_channels)
