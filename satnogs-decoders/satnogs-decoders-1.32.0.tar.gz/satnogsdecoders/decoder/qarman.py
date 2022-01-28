# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Qarman(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.dest_ssid_raw.ssid_mask
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field battery_voltage: ax25_frame.payload.data_payload.mode.eps_payload.battery_voltage
    :field temperature_obc: ax25_frame.payload.data_payload.mode.eps_payload.temperature_obc
    :field battery_current: ax25_frame.payload.data_payload.mode.eps_payload.battery_current
    :field reg_bus_3v3_current: ax25_frame.payload.data_payload.mode.eps_payload.reg_bus_3v3_current
    :field reg_bus_5v0_current: ax25_frame.payload.data_payload.mode.eps_payload.reg_bus_5v0_current
    :field temperature_uhf: ax25_frame.payload.data_payload.mode.eps_payload.temperature_uhf
    :field obc_mode: ax25_frame.payload.data_payload.mode.eps_payload.obc_mode
    :field reason_for_mode_change: ax25_frame.payload.data_payload.mode.eps_payload.reason_for_mode_change
    :field obc_uptime: ax25_frame.payload.data_payload.mode.eps_payload.obc_uptime
    :field obc_boot_counter: ax25_frame.payload.data_payload.mode.eps_payload.obc_boot_counter
    :field obc_packet_counter: ax25_frame.payload.data_payload.mode.eps_payload.obc_packet_counter
    :field obc_tc_frm_received: ax25_frame.payload.data_payload.mode.eps_payload.obc_tc_frm_received
    :field obc_tc_valid: ax25_frame.payload.data_payload.mode.eps_payload.obc_tc_valid
    :field systems_on: ax25_frame.payload.data_payload.mode.eps_payload.systems_on
    :field deployable_status: ax25_frame.payload.data_payload.mode.eps_payload.deployable_status
    :field solar_panel_current_posxi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posxi
    :field solar_panel_current_posxo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posxo
    :field solar_panel_current_negyi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negyi
    :field solar_panel_current_negyo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negyo
    :field solar_panel_current_negxi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negxi
    :field solar_panel_current_negxo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negxo
    :field solar_panel_current_posyi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posyi
    :field solar_panel_current_posyo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posyo
    :field solar_panel_voltage_posx: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_posx
    :field solar_panel_voltage_negy: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_negy
    :field solar_panel_voltage_negx: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_negx
    :field solar_panel_voltage_posy: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_posy
    :field battery_voltage: ax25_frame.payload.data_payload.mode.eps_payload.battery_voltage
    :field temperature_obc: ax25_frame.payload.data_payload.mode.eps_payload.temperature_obc
    :field battery_current: ax25_frame.payload.data_payload.mode.eps_payload.battery_current
    :field reg_bus_3v3_current: ax25_frame.payload.data_payload.mode.eps_payload.reg_bus_3v3_current
    :field reg_bus_5v0_current: ax25_frame.payload.data_payload.mode.eps_payload.reg_bus_5v0_current
    :field temperature_uhf: ax25_frame.payload.data_payload.mode.eps_payload.temperature_uhf
    :field obc_mode: ax25_frame.payload.data_payload.mode.eps_payload.obc_mode
    :field reason_for_mode_change: ax25_frame.payload.data_payload.mode.eps_payload.reason_for_mode_change
    :field obc_uptime: ax25_frame.payload.data_payload.mode.eps_payload.obc_uptime
    :field obc_boot_counter: ax25_frame.payload.data_payload.mode.eps_payload.obc_boot_counter
    :field obc_packet_counter: ax25_frame.payload.data_payload.mode.eps_payload.obc_packet_counter
    :field obc_tc_frm_received: ax25_frame.payload.data_payload.mode.eps_payload.obc_tc_frm_received
    :field obc_tc_valid: ax25_frame.payload.data_payload.mode.eps_payload.obc_tc_valid
    :field systems_on: ax25_frame.payload.data_payload.mode.eps_payload.systems_on
    :field deployable_status: ax25_frame.payload.data_payload.mode.eps_payload.deployable_status
    :field solar_panel_current_posxi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posxi
    :field solar_panel_current_posxo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posxo
    :field solar_panel_current_negyi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negyi
    :field solar_panel_current_negyo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negyo
    :field solar_panel_current_negxi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negxi
    :field solar_panel_current_negxo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_negxo
    :field solar_panel_current_posyi: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posyi
    :field solar_panel_current_posyo: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_current_posyo
    :field solar_panel_voltage_posx: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_posx
    :field solar_panel_voltage_negy: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_negy
    :field solar_panel_voltage_negx: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_negx
    :field solar_panel_voltage_posy: ax25_frame.payload.data_payload.mode.eps_payload.solar_panel_voltage_posy
    :field adcs_state: ax25_frame.payload.data_payload.mode.adcs_payload.adcs_state
    :field attitude_estimation_mode: ax25_frame.payload.data_payload.mode.adcs_payload.attitude_estimation_mode
    :field control_mode: ax25_frame.payload.data_payload.mode.adcs_payload.control_mode
    :field cube_control_3v3_current: ax25_frame.payload.data_payload.mode.adcs_payload.cube_control_3v3_current
    :field cube_control_5v_current: ax25_frame.payload.data_payload.mode.adcs_payload.cube_control_5v_current
    :field cube_control_vbat_current: ax25_frame.payload.data_payload.mode.adcs_payload.cube_control_vbat_current
    :field magnetorquer_current: ax25_frame.payload.data_payload.mode.adcs_payload.magnetorquer_current
    :field momentum_wheel_current: ax25_frame.payload.data_payload.mode.adcs_payload.momentum_wheel_current
    :field magnetic_field_x: ax25_frame.payload.data_payload.mode.adcs_payload.magnetic_field_x
    :field magnetic_field_y: ax25_frame.payload.data_payload.mode.adcs_payload.magnetic_field_y
    :field magnetic_field_z: ax25_frame.payload.data_payload.mode.adcs_payload.magnetic_field_z
    :field y_angular_rate: ax25_frame.payload.data_payload.mode.adcs_payload.y_angular_rate
    :field y_wheel_speed: ax25_frame.payload.data_payload.mode.adcs_payload.y_wheel_speed
    :field estimated_roll_angle: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_roll_angle
    :field estimated_pitch_angle: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_pitch_angle
    :field estimated_yaw_angle: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_yaw_angle
    :field estimated_x_angular_rate: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_x_angular_rate
    :field estimated_y_angular_rate: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_y_angular_rate
    :field estimated_z_angular_rate: ax25_frame.payload.data_payload.mode.adcs_payload.estimated_z_angular_rate
    :field temperature_adcs_arm_cpu: ax25_frame.payload.data_payload.mode.adcs_payload.temperature_adcs_arm_cpu
    :field padding: ax25_frame.payload.data_payload.mode.adcs_payload.padding
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Qarman.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Qarman.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Qarman.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Qarman.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Qarman.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Qarman.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Qarman.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Qarman.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Qarman.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Qarman.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Qarman.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Qarman.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class AdcsPayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_state = self._io.read_bits_int_be(2)
            self.attitude_estimation_mode = self._io.read_bits_int_be(3)
            self.control_mode = self._io.read_bits_int_be(3)
            self.cube_control_3v3_current = self._io.read_bits_int_be(16)
            self.cube_control_5v_current = self._io.read_bits_int_be(16)
            self.cube_control_vbat_current = self._io.read_bits_int_be(16)
            self.magnetorquer_current = self._io.read_bits_int_be(16)
            self.momentum_wheel_current = self._io.read_bits_int_be(16)
            self.magnetic_field_x = self._io.read_bits_int_be(16)
            self.magnetic_field_y = self._io.read_bits_int_be(16)
            self.magnetic_field_z = self._io.read_bits_int_be(16)
            self.y_angular_rate = self._io.read_bits_int_be(16)
            self.y_wheel_speed = self._io.read_bits_int_be(16)
            self.estimated_roll_angle = self._io.read_bits_int_be(16)
            self.estimated_pitch_angle = self._io.read_bits_int_be(16)
            self.estimated_yaw_angle = self._io.read_bits_int_be(16)
            self.estimated_x_angular_rate = self._io.read_bits_int_be(16)
            self.estimated_y_angular_rate = self._io.read_bits_int_be(16)
            self.estimated_z_angular_rate = self._io.read_bits_int_be(16)
            self.temperature_adcs_arm_cpu = self._io.read_bits_int_be(16)
            self.padding = self._io.read_bits_int_be(4)


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._parent.ax25_header.src_callsign_raw.callsign_ror.callsign
            if _on == u"ON05BE":
                self.data_payload = Qarman.QarmanPayloadT(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class EpsPayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_voltage = self._io.read_bits_int_be(12)
            self.temperature_obc = self._io.read_bits_int_be(12)
            self.battery_current = self._io.read_bits_int_be(10)
            self.reg_bus_3v3_current = self._io.read_bits_int_be(10)
            self.reg_bus_5v0_current = self._io.read_bits_int_be(10)
            self.temperature_uhf = self._io.read_bits_int_be(16)
            self.obc_mode = self._io.read_bits_int_be(4)
            self.reason_for_mode_change = self._io.read_bits_int_be(3)
            self.obc_uptime = self._io.read_bits_int_be(32)
            self.obc_boot_counter = self._io.read_bits_int_be(8)
            self.obc_packet_counter = self._io.read_bits_int_be(16)
            self.obc_tc_frm_received = self._io.read_bits_int_be(8)
            self.obc_tc_valid = self._io.read_bits_int_be(8)
            self.systems_on = self._io.read_bits_int_be(26)
            self.deployable_status = self._io.read_bits_int_be(13)
            self.solar_panel_current_posxi = self._io.read_bits_int_be(10)
            self.solar_panel_current_posxo = self._io.read_bits_int_be(10)
            self.solar_panel_current_negyi = self._io.read_bits_int_be(10)
            self.solar_panel_current_negyo = self._io.read_bits_int_be(10)
            self.solar_panel_current_negxi = self._io.read_bits_int_be(10)
            self.solar_panel_current_negxo = self._io.read_bits_int_be(10)
            self.solar_panel_current_posyi = self._io.read_bits_int_be(10)
            self.solar_panel_current_posyo = self._io.read_bits_int_be(10)
            self.solar_panel_voltage_posx = self._io.read_bits_int_be(10)
            self.solar_panel_voltage_negy = self._io.read_bits_int_be(10)
            self.solar_panel_voltage_negx = self._io.read_bits_int_be(10)
            self.solar_panel_voltage_posy = self._io.read_bits_int_be(10)


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


    class LpBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_payload = Qarman.EpsPayloadT(self._io, self, self._root)


    class QarmanPayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.framelength
            if _on == 55:
                self.mode = Qarman.LpBeaconT(self._io, self, self._root)
            elif _on == 90:
                self.mode = Qarman.FullBeaconT(self._io, self, self._root)


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
            self.callsign_ror = Qarman.Callsign(_io__raw_callsign_ror, self, self._root)


    class FullBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_payload = Qarman.EpsPayloadT(self._io, self, self._root)
            self.adcs_payload = Qarman.AdcsPayloadT(self._io, self, self._root)


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


