# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Armadillo(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field time: ax25_frame.payload.data_payload.time
    :field uptime: ax25_frame.payload.data_payload.uptime
    :field avail_nvmem: ax25_frame.payload.data_payload.avail_nvmem
    :field pos_x: ax25_frame.payload.data_payload.pos_x
    :field pos_y: ax25_frame.payload.data_payload.pos_y
    :field pos_z: ax25_frame.payload.data_payload.pos_z
    :field vel_x: ax25_frame.payload.data_payload.vel_x
    :field vel_y: ax25_frame.payload.data_payload.vel_y
    :field vel_z: ax25_frame.payload.data_payload.vel_z
    :field pwr_states_reserved: ax25_frame.payload.data_payload.pwr_states_reserved
    :field gps_power: ax25_frame.payload.data_payload.gps_power
    :field adc_power: ax25_frame.payload.data_payload.adc_power
    :field antenna_power: ax25_frame.payload.data_payload.antenna_power
    :field pdd_power: ax25_frame.payload.data_payload.pdd_power
    :field spacecraft_mode: ax25_frame.payload.data_payload.spacecraft_mode
    :field vbatt: ax25_frame.payload.data_payload.vbatt
    :field input_current: ax25_frame.payload.data_payload.input_current
    :field output_current: ax25_frame.payload.data_payload.output_current
    :field boot_count: ax25_frame.payload.data_payload.boot_count
    :field boot_cause: ax25_frame.payload.data_payload.boot_cause
    :field eps_temp_1: ax25_frame.payload.data_payload.eps_temp_1
    :field eps_temp_2: ax25_frame.payload.data_payload.eps_temp_2
    :field eps_temp_3: ax25_frame.payload.data_payload.eps_temp_3
    :field eps_temp_4: ax25_frame.payload.data_payload.eps_temp_4
    :field eps_bp4a: ax25_frame.payload.data_payload.eps_bp4a
    :field eps_bp4b: ax25_frame.payload.data_payload.eps_bp4b
    :field eps_output_1_current: ax25_frame.payload.data_payload.eps_output_1_current
    :field eps_output_2_current: ax25_frame.payload.data_payload.eps_output_2_current
    :field eps_output_3_current: ax25_frame.payload.data_payload.eps_output_3_current
    :field eps_output_4_current: ax25_frame.payload.data_payload.eps_output_4_current
    :field eps_output_5_current: ax25_frame.payload.data_payload.eps_output_5_current
    :field eps_output_6_current: ax25_frame.payload.data_payload.eps_output_6_current
    :field rxwl_temp_x: ax25_frame.payload.data_payload.rxwl_temp_x
    :field rxwl_temp_y: ax25_frame.payload.data_payload.rxwl_temp_y
    :field rxwl_temp_z: ax25_frame.payload.data_payload.rxwl_temp_z
    :field gyro_temp_x: ax25_frame.payload.data_payload.gyro_temp_x
    :field gyro_temp_y: ax25_frame.payload.data_payload.gyro_temp_y
    :field gyro_temp_z: ax25_frame.payload.data_payload.gyro_temp_z
    :field desired_quaternion_a: ax25_frame.payload.data_payload.desired_quaternion_a
    :field desired_quaternion_b: ax25_frame.payload.data_payload.desired_quaternion_b
    :field desired_quaternion_c: ax25_frame.payload.data_payload.desired_quaternion_c
    :field desired_quaternion_d: ax25_frame.payload.data_payload.desired_quaternion_d
    :field estimated_quaternion_a: ax25_frame.payload.data_payload.estimated_quaternion_a
    :field estimated_quaternion_b: ax25_frame.payload.data_payload.estimated_quaternion_b
    :field estimated_quaternion_c: ax25_frame.payload.data_payload.estimated_quaternion_c
    :field estimated_quaternion_d: ax25_frame.payload.data_payload.estimated_quaternion_d
    :field rotation_rate_x: ax25_frame.payload.data_payload.rotation_rate_x
    :field rotation_rate_y: ax25_frame.payload.data_payload.rotation_rate_y
    :field rotation_rate_z: ax25_frame.payload.data_payload.rotation_rate_z
    :field sun_sensor_address: ax25_frame.payload.data_payload.sun_sensor_address
    :field message: ax25_frame.payload.data_payload.message
    """

    class BootCauses(Enum):
        unknown_reset = 0
        dedicated_wdt_reset = 1
        i2c_wdt_reset = 2
        hard_reset = 3
        soft_reset = 4
        stack_overflow = 5
        timer_overflow = 6
        brownout_or_power_on_reset = 7
        internal_wdt_reset = 8
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Armadillo.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Armadillo.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Armadillo.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Armadillo.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Armadillo.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Armadillo.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Armadillo.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Armadillo.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Armadillo.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Armadillo.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Armadillo.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Armadillo.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._parent.ax25_header.src_callsign_raw.callsign_ror.callsign
            if _on == u"KE5DTW":
                self.data_payload = Armadillo.ArmadilloPayload(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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


    class ArmadilloPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pb_magic = self._io.read_bytes(5)
            self.time = self._io.read_u4le()
            self.uptime = self._io.read_u4le()
            self.avail_nvmem = self._io.read_u4le()
            self.pos_x = self._io.read_f4le()
            self.pos_y = self._io.read_f4le()
            self.pos_z = self._io.read_f4le()
            self.vel_x = self._io.read_f4le()
            self.vel_y = self._io.read_f4le()
            self.vel_z = self._io.read_f4le()
            self.pwr_states_reserved = self._io.read_bits_int_be(3)
            self.gps_power = self._io.read_bits_int_be(1) != 0
            self.adc_power = self._io.read_bits_int_be(1) != 0
            self.antenna_power = self._io.read_bits_int_be(1) != 0
            self.pdd_power = self._io.read_bits_int_be(1) != 0
            self.spacecraft_mode = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.vbatt = self._io.read_u2le()
            self.input_current = self._io.read_u2le()
            self.output_current = self._io.read_u2le()
            self.boot_count = self._io.read_u4le()
            self.boot_cause = self._io.read_u1()
            self.eps_temp_1 = self._io.read_s2le()
            self.eps_temp_2 = self._io.read_s2le()
            self.eps_temp_3 = self._io.read_s2le()
            self.eps_temp_4 = self._io.read_s2le()
            self.eps_bp4a = self._io.read_s2le()
            self.eps_bp4b = self._io.read_s2le()
            self.eps_output_1_current = self._io.read_u2le()
            self.eps_output_2_current = self._io.read_u2le()
            self.eps_output_3_current = self._io.read_u2le()
            self.eps_output_4_current = self._io.read_u2le()
            self.eps_output_5_current = self._io.read_u2le()
            self.eps_output_6_current = self._io.read_u2le()
            self.rxwl_temp_x = self._io.read_f4le()
            self.rxwl_temp_y = self._io.read_f4le()
            self.rxwl_temp_z = self._io.read_f4le()
            self.gyro_temp_x = self._io.read_f4le()
            self.gyro_temp_y = self._io.read_f4le()
            self.gyro_temp_z = self._io.read_f4le()
            self.desired_quaternion_a = self._io.read_f4le()
            self.desired_quaternion_b = self._io.read_f4le()
            self.desired_quaternion_c = self._io.read_f4le()
            self.desired_quaternion_d = self._io.read_f4le()
            self.estimated_quaternion_a = self._io.read_f4le()
            self.estimated_quaternion_b = self._io.read_f4le()
            self.estimated_quaternion_c = self._io.read_f4le()
            self.estimated_quaternion_d = self._io.read_f4le()
            self.rotation_rate_x = self._io.read_f4le()
            self.rotation_rate_y = self._io.read_f4le()
            self.rotation_rate_z = self._io.read_f4le()
            self.sun_sensor_address = self._io.read_u1()
            self.message = (KaitaiStream.bytes_terminate(self._io.read_bytes(110), 0, False)).decode(u"ASCII")


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
            self.callsign_ror = Armadillo.Callsign(_io__raw_callsign_ror, self, self._root)



