from array import array
from ctypes import *
from .api import api
from .const import *
from .library import library
from .oscilloscopechanneltrigger import OscilloscopeChannelTrigger


class OscilloscopeChannel(object):
    """"""

    def __init__(self, handle, ch):
        self._handle = handle
        self._ch = ch
        self._trigger = OscilloscopeChannelTrigger(handle, ch) if self.has_trigger else None

    def _get_trigger(self):
        return self._trigger

    def _get_is_available(self):
        """ Check whether the channel is available. """
        value = api.ScpChIsAvailable(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_connector_type(self):
        """ Channel connector type. """
        value = api.ScpChGetConnectorType(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_is_differential(self):
        """ Check whether the channel has a differential input. """
        value = api.ScpChIsDifferential(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_impedance(self):
        """ Channel input impedance. """
        value = api.ScpChGetImpedance(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_bandwidths(self):
        """ Supported input bandwidths. """
        count = api.ScpChGetBandwidths(self._handle, self._ch, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_double * count)()
        api.ScpChGetBandwidths(self._handle, self._ch, values, count)
        library.check_last_status_raise_on_error()
        return array('d', values)

    def _get_bandwidth(self):
        """ Current channel input bandwidth. """
        value = api.ScpChGetBandwidth(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_bandwidth(self, value):
        api.ScpChSetBandwidth(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_couplings(self):
        """ Supported coupling kinds. """
        value = api.ScpChGetCouplings(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_coupling(self):
        """ Currently set coupling. """
        value = api.ScpChGetCoupling(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_coupling(self, value):
        api.ScpChSetCoupling(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_enabled(self):
        """ Check whether a specified channel is currently enabled. """
        value = api.ScpChGetEnabled(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.ScpChSetEnabled(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_probe_gain(self):
        """ Currently set channel probe gain. """
        value = api.ScpChGetProbeGain(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_probe_gain(self, value):
        api.ScpChSetProbeGain(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_probe_offset(self):
        """ Currently set channel probe offset. """
        value = api.ScpChGetProbeOffset(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_probe_offset(self, value):
        api.ScpChSetProbeOffset(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_auto_ranging(self):
        """ Check whether auto ranging is enabled. """
        value = api.ScpChGetAutoRanging(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_auto_ranging(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.ScpChSetAutoRanging(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_ranges(self):
        """ Supported input ranges, with the currently selected coupling. """
        count = api.ScpChGetRanges(self._handle, self._ch, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_double * count)()
        api.ScpChGetRanges(self._handle, self._ch, values, count)
        library.check_last_status_raise_on_error()
        return array('d', values)

    def _get_range(self):
        """ Currently selected input range. """
        value = api.ScpChGetRange(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_range(self, value):
        api.ScpChSetRange(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_has_safe_ground(self):
        """ Check whether the specified channel has SafeGround. """
        value = api.ScpChHasSafeGround(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_safe_ground_enabled(self):
        """ Check whether SafeGround is enabled. """
        value = api.ScpChGetSafeGroundEnabled(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_safe_ground_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.ScpChSetSafeGroundEnabled(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_safe_ground_threshold_min(self):
        """ Minimum SafeGround threshold current. """
        value = api.ScpChGetSafeGroundThresholdMin(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_safe_ground_threshold_max(self):
        """ Maximum SafeGround threshold current. """
        value = api.ScpChGetSafeGroundThresholdMax(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_safe_ground_threshold(self):
        """ Actual SafeGround threshold current. """
        value = api.ScpChGetSafeGroundThreshold(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_safe_ground_threshold(self, value):
        api.ScpChSetSafeGroundThreshold(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def verify_safe_ground_threshold(self, threshold):
        """ Verify if the required threshold current can be set.

        :param threshold: The required threshold current, in Ampere.
        :returns: The SafeGround threshold current that would be set.
        .. versionadded:: 0.6
        """
        result = api.ScpChVerifySafeGroundThreshold(self._handle, self._ch, threshold)
        library.check_last_status_raise_on_error()
        return result

    def _get_has_trigger(self):
        """ Check whether the specified channel has trigger support with the currently selected measure mode. """
        value = api.ScpChHasTrigger(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_data_value_min(self):
        """ Minimum value of the input range the current data was measured with. """
        value = api.ScpChGetDataValueMin(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_value_max(self):
        """ Maximum value of the input range the current data was measured with. """
        value = api.ScpChGetDataValueMax(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_type(self):
        """ Get raw data type. """
        value = api.ScpChGetDataRawType(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_value_min(self):
        """ Get possible raw data minimum value. """
        value = api.ScpChGetDataRawValueMin(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_value_zero(self):
        """ Get raw data value which equals zero. """
        value = api.ScpChGetDataRawValueZero(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_data_raw_value_max(self):
        """ Get possible raw data maximum value. """
        value = api.ScpChGetDataRawValueMax(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_is_range_max_reachable(self):
        """ Check whether the ranges maximum is reachable. """
        value = api.ScpChIsRangeMaxReachable(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_has_connection_test(self):
        """ Check whether a specified channel supports connection testing. """
        value = api.ScpChHasConnectionTest(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    is_available = property(_get_is_available)
    connector_type = property(_get_connector_type)
    is_differential = property(_get_is_differential)
    impedance = property(_get_impedance)
    bandwidths = property(_get_bandwidths)
    bandwidth = property(_get_bandwidth, _set_bandwidth)
    couplings = property(_get_couplings)
    coupling = property(_get_coupling, _set_coupling)
    enabled = property(_get_enabled, _set_enabled)
    probe_gain = property(_get_probe_gain, _set_probe_gain)
    probe_offset = property(_get_probe_offset, _set_probe_offset)
    auto_ranging = property(_get_auto_ranging, _set_auto_ranging)
    ranges = property(_get_ranges)
    range = property(_get_range, _set_range)
    has_safe_ground = property(_get_has_safe_ground)
    safe_ground_enabled = property(_get_safe_ground_enabled, _set_safe_ground_enabled)
    safe_ground_threshold_min = property(_get_safe_ground_threshold_min)
    safe_ground_threshold_max = property(_get_safe_ground_threshold_max)
    safe_ground_threshold = property(_get_safe_ground_threshold, _set_safe_ground_threshold)
    has_trigger = property(_get_has_trigger)
    data_value_min = property(_get_data_value_min)
    data_value_max = property(_get_data_value_max)
    data_raw_type = property(_get_data_raw_type)
    data_raw_value_min = property(_get_data_raw_value_min)
    data_raw_value_zero = property(_get_data_raw_value_zero)
    data_raw_value_max = property(_get_data_raw_value_max)
    is_range_max_reachable = property(_get_is_range_max_reachable)
    has_connection_test = property(_get_has_connection_test)
    trigger = property(_get_trigger)
