# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ramsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field prefix: ax25_frame.payload.payload.prefix
    :field beacon_timestamp: ax25_frame.payload.payload.beacon_timestamp
    :field battery_voltage: ax25_frame.payload.payload.battery_voltage
    :field battery_current_magnitude: ax25_frame.payload.payload.battery_current_magnitude
    :field battery_is_charging: ax25_frame.payload.payload.battery_is_charging
    :field voltage_feeding_bcr1_x: ax25_frame.payload.payload.voltage_feeding_bcr1_x
    :field current_bcr1_neg_x: ax25_frame.payload.payload.current_bcr1_neg_x
    :field current_bcr1_pos_x: ax25_frame.payload.payload.current_bcr1_pos_x
    :field voltage_feeding_bcr2_y: ax25_frame.payload.payload.voltage_feeding_bcr2_y
    :field current_bcr1_neg_y: ax25_frame.payload.payload.current_bcr1_neg_y
    :field current_bcr1_pos_y: ax25_frame.payload.payload.current_bcr1_pos_y
    :field voltage_feeding_bcr3_z: ax25_frame.payload.payload.voltage_feeding_bcr3_z
    :field current_bcr1_neg_z: ax25_frame.payload.payload.current_bcr1_neg_z
    :field bcr_output_voltage: ax25_frame.payload.payload.bcr_output_voltage
    :field bcr_output_current: ax25_frame.payload.payload.bcr_output_current
    :field battery_bus_voltage: ax25_frame.payload.payload.battery_bus_voltage
    :field battery_bus_current: ax25_frame.payload.payload.battery_bus_current
    :field low_v_bus_voltage: ax25_frame.payload.payload.low_v_bus_voltage
    :field low_v_bus_current: ax25_frame.payload.payload.low_v_bus_current
    :field high_v_bus_voltage: ax25_frame.payload.payload.high_v_bus_voltage
    :field high_v_bus_current: ax25_frame.payload.payload.high_v_bus_current
    :field temperature_eps: ax25_frame.payload.payload.temperature_eps
    :field temperature_battery_motherboard: ax25_frame.payload.payload.temperature_battery_motherboard
    :field temperature_battery_daughterboard: ax25_frame.payload.payload.temperature_battery_daughterboard
    :field temperature_pos_x_array: ax25_frame.payload.payload.temperature_pos_x_array
    :field temperature_neg_x_array: ax25_frame.payload.payload.temperature_neg_x_array
    :field temperature_pos_y_array: ax25_frame.payload.payload.temperature_pos_y_array
    :field temperature_neg_y_array: ax25_frame.payload.payload.temperature_neg_y_array
    :field sunsensor_pos_xa: ax25_frame.payload.payload.sunsensor_pos_xa
    :field sunsensor_pos_xb: ax25_frame.payload.payload.sunsensor_pos_xb
    :field sunsensor_neg_xa: ax25_frame.payload.payload.sunsensor_neg_xa
    :field sunsensor_neg_xb: ax25_frame.payload.payload.sunsensor_neg_xb
    :field sunsensor_pos_ya: ax25_frame.payload.payload.sunsensor_pos_ya
    :field sunsensor_pos_yb: ax25_frame.payload.payload.sunsensor_pos_yb
    :field sunsensor_neg_ya: ax25_frame.payload.payload.sunsensor_neg_ya
    :field sunsensor_net_yb: ax25_frame.payload.payload.sunsensor_net_yb
    :field imtq_cal_mag_x: ax25_frame.payload.payload.imtq_cal_mag_x
    :field imtq_cal_mag_y: ax25_frame.payload.payload.imtq_cal_mag_y
    :field imtq_cal_mag_z: ax25_frame.payload.payload.imtq_cal_mag_z
    :field antenna_deployment_status: ax25_frame.payload.payload.antenna_deployment_status
    :field longitude: ax25_frame.payload.payload.longitude
    :field latitude: ax25_frame.payload.payload.latitude
    :field elevation: ax25_frame.payload.payload.elevation
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Ramsat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Ramsat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Ramsat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Ramsat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Ramsat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Ramsat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Ramsat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Ramsat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Ramsat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Ramsat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Ramsat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Ramsat.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.payload = Ramsat.RsPacket(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CQ    ") or (self.callsign == u"W4SKH ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class RsPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.prefix = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            if not self.prefix == u"RSBeac:":
                raise kaitaistruct.ValidationNotEqualError(u"RSBeac:", self.prefix, self._io, u"/types/rs_packet/seq/0")
            self.beacon_timestamp = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.battery_voltage_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.battery_current_magnitude_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.battery_is_charging_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.voltage_feeding_bcr1_x_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.current_bcr1_neg_x_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.current_bcr1_pos_x_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.voltage_feeding_bcr2_y_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.current_bcr1_neg_y_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.current_bcr1_pos_y_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.voltage_feeding_bcr3_z_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.current_bcr1_neg_z_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.bcr_output_voltage_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.bcr_output_current_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.battery_bus_voltage_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.battery_bus_current_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.low_v_bus_voltage_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.low_v_bus_current_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.high_v_bus_voltage_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.high_v_bus_current_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_eps_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_battery_motherboard_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_battery_daughterboard_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_pos_x_array_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_neg_x_array_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_pos_y_array_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.temperature_neg_y_array_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_pos_xa_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_pos_xb_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_neg_xa_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_neg_xb_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_pos_ya_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_pos_yb_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_neg_ya_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.sunsensor_net_yb_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.imtq_cal_mag_x_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.imtq_cal_mag_y_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.imtq_cal_mag_z_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.antenna_deployment_status_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.longitude_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.latitude_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.elevation_str = (self._io.read_bytes(4)).decode(u"ASCII")

        @property
        def bcr_output_current(self):
            if hasattr(self, '_m_bcr_output_current'):
                return self._m_bcr_output_current if hasattr(self, '_m_bcr_output_current') else None

            self._m_bcr_output_current = int(self.bcr_output_current_str)
            return self._m_bcr_output_current if hasattr(self, '_m_bcr_output_current') else None

        @property
        def bcr_output_voltage(self):
            if hasattr(self, '_m_bcr_output_voltage'):
                return self._m_bcr_output_voltage if hasattr(self, '_m_bcr_output_voltage') else None

            self._m_bcr_output_voltage = int(self.bcr_output_voltage_str)
            return self._m_bcr_output_voltage if hasattr(self, '_m_bcr_output_voltage') else None

        @property
        def sunsensor_neg_ya(self):
            if hasattr(self, '_m_sunsensor_neg_ya'):
                return self._m_sunsensor_neg_ya if hasattr(self, '_m_sunsensor_neg_ya') else None

            self._m_sunsensor_neg_ya = int(self.sunsensor_neg_ya_str)
            return self._m_sunsensor_neg_ya if hasattr(self, '_m_sunsensor_neg_ya') else None

        @property
        def temperature_neg_y_array(self):
            if hasattr(self, '_m_temperature_neg_y_array'):
                return self._m_temperature_neg_y_array if hasattr(self, '_m_temperature_neg_y_array') else None

            self._m_temperature_neg_y_array = int(self.temperature_neg_y_array_str)
            return self._m_temperature_neg_y_array if hasattr(self, '_m_temperature_neg_y_array') else None

        @property
        def current_bcr1_neg_x(self):
            if hasattr(self, '_m_current_bcr1_neg_x'):
                return self._m_current_bcr1_neg_x if hasattr(self, '_m_current_bcr1_neg_x') else None

            self._m_current_bcr1_neg_x = int(self.current_bcr1_neg_x_str)
            return self._m_current_bcr1_neg_x if hasattr(self, '_m_current_bcr1_neg_x') else None

        @property
        def imtq_cal_mag_x(self):
            if hasattr(self, '_m_imtq_cal_mag_x'):
                return self._m_imtq_cal_mag_x if hasattr(self, '_m_imtq_cal_mag_x') else None

            self._m_imtq_cal_mag_x = int(self.imtq_cal_mag_x_str)
            return self._m_imtq_cal_mag_x if hasattr(self, '_m_imtq_cal_mag_x') else None

        @property
        def current_bcr1_pos_x(self):
            if hasattr(self, '_m_current_bcr1_pos_x'):
                return self._m_current_bcr1_pos_x if hasattr(self, '_m_current_bcr1_pos_x') else None

            self._m_current_bcr1_pos_x = int(self.current_bcr1_pos_x_str)
            return self._m_current_bcr1_pos_x if hasattr(self, '_m_current_bcr1_pos_x') else None

        @property
        def sunsensor_net_yb(self):
            if hasattr(self, '_m_sunsensor_net_yb'):
                return self._m_sunsensor_net_yb if hasattr(self, '_m_sunsensor_net_yb') else None

            self._m_sunsensor_net_yb = int(self.sunsensor_net_yb_str)
            return self._m_sunsensor_net_yb if hasattr(self, '_m_sunsensor_net_yb') else None

        @property
        def temperature_pos_x_array(self):
            if hasattr(self, '_m_temperature_pos_x_array'):
                return self._m_temperature_pos_x_array if hasattr(self, '_m_temperature_pos_x_array') else None

            self._m_temperature_pos_x_array = int(self.temperature_pos_x_array_str)
            return self._m_temperature_pos_x_array if hasattr(self, '_m_temperature_pos_x_array') else None

        @property
        def battery_bus_voltage(self):
            if hasattr(self, '_m_battery_bus_voltage'):
                return self._m_battery_bus_voltage if hasattr(self, '_m_battery_bus_voltage') else None

            self._m_battery_bus_voltage = int(self.battery_bus_voltage_str)
            return self._m_battery_bus_voltage if hasattr(self, '_m_battery_bus_voltage') else None

        @property
        def battery_current_magnitude(self):
            if hasattr(self, '_m_battery_current_magnitude'):
                return self._m_battery_current_magnitude if hasattr(self, '_m_battery_current_magnitude') else None

            self._m_battery_current_magnitude = int(self.battery_current_magnitude_str)
            return self._m_battery_current_magnitude if hasattr(self, '_m_battery_current_magnitude') else None

        @property
        def sunsensor_pos_xa(self):
            if hasattr(self, '_m_sunsensor_pos_xa'):
                return self._m_sunsensor_pos_xa if hasattr(self, '_m_sunsensor_pos_xa') else None

            self._m_sunsensor_pos_xa = int(self.sunsensor_pos_xa_str)
            return self._m_sunsensor_pos_xa if hasattr(self, '_m_sunsensor_pos_xa') else None

        @property
        def battery_voltage(self):
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

            self._m_battery_voltage = int(self.battery_voltage_str)
            return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

        @property
        def low_v_bus_voltage(self):
            if hasattr(self, '_m_low_v_bus_voltage'):
                return self._m_low_v_bus_voltage if hasattr(self, '_m_low_v_bus_voltage') else None

            self._m_low_v_bus_voltage = int(self.low_v_bus_voltage_str)
            return self._m_low_v_bus_voltage if hasattr(self, '_m_low_v_bus_voltage') else None

        @property
        def sunsensor_neg_xa(self):
            if hasattr(self, '_m_sunsensor_neg_xa'):
                return self._m_sunsensor_neg_xa if hasattr(self, '_m_sunsensor_neg_xa') else None

            self._m_sunsensor_neg_xa = int(self.sunsensor_neg_xa_str)
            return self._m_sunsensor_neg_xa if hasattr(self, '_m_sunsensor_neg_xa') else None

        @property
        def temperature_eps(self):
            if hasattr(self, '_m_temperature_eps'):
                return self._m_temperature_eps if hasattr(self, '_m_temperature_eps') else None

            self._m_temperature_eps = int(self.temperature_eps_str)
            return self._m_temperature_eps if hasattr(self, '_m_temperature_eps') else None

        @property
        def latitude(self):
            if hasattr(self, '_m_latitude'):
                return self._m_latitude if hasattr(self, '_m_latitude') else None

            self._m_latitude = int(self.latitude_str)
            return self._m_latitude if hasattr(self, '_m_latitude') else None

        @property
        def sunsensor_pos_xb(self):
            if hasattr(self, '_m_sunsensor_pos_xb'):
                return self._m_sunsensor_pos_xb if hasattr(self, '_m_sunsensor_pos_xb') else None

            self._m_sunsensor_pos_xb = int(self.sunsensor_pos_xb_str)
            return self._m_sunsensor_pos_xb if hasattr(self, '_m_sunsensor_pos_xb') else None

        @property
        def longitude(self):
            if hasattr(self, '_m_longitude'):
                return self._m_longitude if hasattr(self, '_m_longitude') else None

            self._m_longitude = int(self.longitude_str)
            return self._m_longitude if hasattr(self, '_m_longitude') else None

        @property
        def elevation(self):
            if hasattr(self, '_m_elevation'):
                return self._m_elevation if hasattr(self, '_m_elevation') else None

            self._m_elevation = int(self.elevation_str)
            return self._m_elevation if hasattr(self, '_m_elevation') else None

        @property
        def voltage_feeding_bcr1_x(self):
            if hasattr(self, '_m_voltage_feeding_bcr1_x'):
                return self._m_voltage_feeding_bcr1_x if hasattr(self, '_m_voltage_feeding_bcr1_x') else None

            self._m_voltage_feeding_bcr1_x = int(self.voltage_feeding_bcr1_x_str)
            return self._m_voltage_feeding_bcr1_x if hasattr(self, '_m_voltage_feeding_bcr1_x') else None

        @property
        def voltage_feeding_bcr2_y(self):
            if hasattr(self, '_m_voltage_feeding_bcr2_y'):
                return self._m_voltage_feeding_bcr2_y if hasattr(self, '_m_voltage_feeding_bcr2_y') else None

            self._m_voltage_feeding_bcr2_y = int(self.voltage_feeding_bcr2_y_str)
            return self._m_voltage_feeding_bcr2_y if hasattr(self, '_m_voltage_feeding_bcr2_y') else None

        @property
        def temperature_battery_daughterboard(self):
            if hasattr(self, '_m_temperature_battery_daughterboard'):
                return self._m_temperature_battery_daughterboard if hasattr(self, '_m_temperature_battery_daughterboard') else None

            self._m_temperature_battery_daughterboard = int(self.temperature_battery_daughterboard_str)
            return self._m_temperature_battery_daughterboard if hasattr(self, '_m_temperature_battery_daughterboard') else None

        @property
        def current_bcr1_pos_y(self):
            if hasattr(self, '_m_current_bcr1_pos_y'):
                return self._m_current_bcr1_pos_y if hasattr(self, '_m_current_bcr1_pos_y') else None

            self._m_current_bcr1_pos_y = int(self.current_bcr1_pos_y_str)
            return self._m_current_bcr1_pos_y if hasattr(self, '_m_current_bcr1_pos_y') else None

        @property
        def antenna_deployment_status(self):
            if hasattr(self, '_m_antenna_deployment_status'):
                return self._m_antenna_deployment_status if hasattr(self, '_m_antenna_deployment_status') else None

            self._m_antenna_deployment_status = int(self.antenna_deployment_status_str)
            return self._m_antenna_deployment_status if hasattr(self, '_m_antenna_deployment_status') else None

        @property
        def battery_is_charging(self):
            if hasattr(self, '_m_battery_is_charging'):
                return self._m_battery_is_charging if hasattr(self, '_m_battery_is_charging') else None

            self._m_battery_is_charging = int(self.battery_is_charging_str)
            return self._m_battery_is_charging if hasattr(self, '_m_battery_is_charging') else None

        @property
        def battery_bus_current(self):
            if hasattr(self, '_m_battery_bus_current'):
                return self._m_battery_bus_current if hasattr(self, '_m_battery_bus_current') else None

            self._m_battery_bus_current = int(self.battery_bus_current_str)
            return self._m_battery_bus_current if hasattr(self, '_m_battery_bus_current') else None

        @property
        def sunsensor_pos_ya(self):
            if hasattr(self, '_m_sunsensor_pos_ya'):
                return self._m_sunsensor_pos_ya if hasattr(self, '_m_sunsensor_pos_ya') else None

            self._m_sunsensor_pos_ya = int(self.sunsensor_pos_ya_str)
            return self._m_sunsensor_pos_ya if hasattr(self, '_m_sunsensor_pos_ya') else None

        @property
        def low_v_bus_current(self):
            if hasattr(self, '_m_low_v_bus_current'):
                return self._m_low_v_bus_current if hasattr(self, '_m_low_v_bus_current') else None

            self._m_low_v_bus_current = int(self.low_v_bus_current_str)
            return self._m_low_v_bus_current if hasattr(self, '_m_low_v_bus_current') else None

        @property
        def voltage_feeding_bcr3_z(self):
            if hasattr(self, '_m_voltage_feeding_bcr3_z'):
                return self._m_voltage_feeding_bcr3_z if hasattr(self, '_m_voltage_feeding_bcr3_z') else None

            self._m_voltage_feeding_bcr3_z = int(self.voltage_feeding_bcr3_z_str)
            return self._m_voltage_feeding_bcr3_z if hasattr(self, '_m_voltage_feeding_bcr3_z') else None

        @property
        def current_bcr1_neg_y(self):
            if hasattr(self, '_m_current_bcr1_neg_y'):
                return self._m_current_bcr1_neg_y if hasattr(self, '_m_current_bcr1_neg_y') else None

            self._m_current_bcr1_neg_y = int(self.current_bcr1_neg_y_str)
            return self._m_current_bcr1_neg_y if hasattr(self, '_m_current_bcr1_neg_y') else None

        @property
        def current_bcr1_neg_z(self):
            if hasattr(self, '_m_current_bcr1_neg_z'):
                return self._m_current_bcr1_neg_z if hasattr(self, '_m_current_bcr1_neg_z') else None

            self._m_current_bcr1_neg_z = int(self.current_bcr1_neg_z_str)
            return self._m_current_bcr1_neg_z if hasattr(self, '_m_current_bcr1_neg_z') else None

        @property
        def high_v_bus_current(self):
            if hasattr(self, '_m_high_v_bus_current'):
                return self._m_high_v_bus_current if hasattr(self, '_m_high_v_bus_current') else None

            self._m_high_v_bus_current = int(self.high_v_bus_current_str)
            return self._m_high_v_bus_current if hasattr(self, '_m_high_v_bus_current') else None

        @property
        def imtq_cal_mag_z(self):
            if hasattr(self, '_m_imtq_cal_mag_z'):
                return self._m_imtq_cal_mag_z if hasattr(self, '_m_imtq_cal_mag_z') else None

            self._m_imtq_cal_mag_z = int(self.imtq_cal_mag_z_str)
            return self._m_imtq_cal_mag_z if hasattr(self, '_m_imtq_cal_mag_z') else None

        @property
        def high_v_bus_voltage(self):
            if hasattr(self, '_m_high_v_bus_voltage'):
                return self._m_high_v_bus_voltage if hasattr(self, '_m_high_v_bus_voltage') else None

            self._m_high_v_bus_voltage = int(self.high_v_bus_voltage_str)
            return self._m_high_v_bus_voltage if hasattr(self, '_m_high_v_bus_voltage') else None

        @property
        def sunsensor_pos_yb(self):
            if hasattr(self, '_m_sunsensor_pos_yb'):
                return self._m_sunsensor_pos_yb if hasattr(self, '_m_sunsensor_pos_yb') else None

            self._m_sunsensor_pos_yb = int(self.sunsensor_pos_yb_str)
            return self._m_sunsensor_pos_yb if hasattr(self, '_m_sunsensor_pos_yb') else None

        @property
        def imtq_cal_mag_y(self):
            if hasattr(self, '_m_imtq_cal_mag_y'):
                return self._m_imtq_cal_mag_y if hasattr(self, '_m_imtq_cal_mag_y') else None

            self._m_imtq_cal_mag_y = int(self.imtq_cal_mag_y_str)
            return self._m_imtq_cal_mag_y if hasattr(self, '_m_imtq_cal_mag_y') else None

        @property
        def sunsensor_neg_xb(self):
            if hasattr(self, '_m_sunsensor_neg_xb'):
                return self._m_sunsensor_neg_xb if hasattr(self, '_m_sunsensor_neg_xb') else None

            self._m_sunsensor_neg_xb = int(self.sunsensor_neg_xb_str)
            return self._m_sunsensor_neg_xb if hasattr(self, '_m_sunsensor_neg_xb') else None

        @property
        def temperature_pos_y_array(self):
            if hasattr(self, '_m_temperature_pos_y_array'):
                return self._m_temperature_pos_y_array if hasattr(self, '_m_temperature_pos_y_array') else None

            self._m_temperature_pos_y_array = int(self.temperature_pos_y_array_str)
            return self._m_temperature_pos_y_array if hasattr(self, '_m_temperature_pos_y_array') else None

        @property
        def temperature_battery_motherboard(self):
            if hasattr(self, '_m_temperature_battery_motherboard'):
                return self._m_temperature_battery_motherboard if hasattr(self, '_m_temperature_battery_motherboard') else None

            self._m_temperature_battery_motherboard = int(self.temperature_battery_motherboard_str)
            return self._m_temperature_battery_motherboard if hasattr(self, '_m_temperature_battery_motherboard') else None

        @property
        def temperature_neg_x_array(self):
            if hasattr(self, '_m_temperature_neg_x_array'):
                return self._m_temperature_neg_x_array if hasattr(self, '_m_temperature_neg_x_array') else None

            self._m_temperature_neg_x_array = int(self.temperature_neg_x_array_str)
            return self._m_temperature_neg_x_array if hasattr(self, '_m_temperature_neg_x_array') else None


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = Ramsat.Callsign(_io__raw_callsign_ror, self, self._root)



