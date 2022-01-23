# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Neutron1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_type: ax25_frame.payload.ax25_info.packet_type
    :field utc: ax25_frame.payload.ax25_info.utc
    :field pos_eci_0: ax25_frame.payload.ax25_info.pos_eci_0
    :field pos_eci_1: ax25_frame.payload.ax25_info.pos_eci_1
    :field pos_eci_2: ax25_frame.payload.ax25_info.pos_eci_2
    :field vel_eci_0: ax25_frame.payload.ax25_info.vel_eci_0
    :field vel_eci_1: ax25_frame.payload.ax25_info.vel_eci_1
    :field vel_eci_2: ax25_frame.payload.ax25_info.vel_eci_2
    :field att_icrf_s_w: ax25_frame.payload.ax25_info.att_icrf_s_w
    :field att_icrf_s_x: ax25_frame.payload.ax25_info.att_icrf_s_x
    :field att_icrf_s_y: ax25_frame.payload.ax25_info.att_icrf_s_y
    :field att_icrf_s_z: ax25_frame.payload.ax25_info.att_icrf_s_z
    :field last_rssi_time: ax25_frame.payload.ax25_info.last_rssi_time
    :field batt_percent: ax25_frame.payload.ax25_info.batt_percent
    :field batt_volt: ax25_frame.payload.ax25_info.batt_volt
    :field batt_current: ax25_frame.payload.ax25_info.batt_current
    :field powgen: ax25_frame.payload.ax25_info.powgen
    :field eps_temp: ax25_frame.payload.ax25_info.eps_temp
    :field batt_temp: ax25_frame.payload.ax25_info.batt_temp
    :field cpu_temp: ax25_frame.payload.ax25_info.cpu_temp
    :field duplex_flag: ax25_frame.payload.ax25_info.duplex_flag
    :field nframes_recv_buf: ax25_frame.payload.ax25_info.nframes_recv_buf
    :field last_rssi: ax25_frame.payload.ax25_info.last_rssi
    :field antenna_deployed_status: ax25_frame.payload.ax25_info.antenna_deployed_status
    :field powmode: ax25_frame.payload.ax25_info.powmode
    :field callsign: ax25_frame.payload.ax25_info.callsign
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Neutron1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Neutron1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Neutron1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Neutron1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Neutron1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Neutron1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Neutron1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Neutron1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Neutron1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Neutron1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Neutron1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Neutron1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = Neutron1.Neutron1BeaconT(self._io, self, self._root)


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


    class Neutron1BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_type = self._io.read_u1()
            self.utc = self._io.read_f8le()
            self.pos_eci_0 = self._io.read_f8le()
            self.pos_eci_1 = self._io.read_f8le()
            self.pos_eci_2 = self._io.read_f8le()
            self.vel_eci_0 = self._io.read_f8le()
            self.vel_eci_1 = self._io.read_f8le()
            self.vel_eci_2 = self._io.read_f8le()
            self.att_icrf_s_w = self._io.read_f8le()
            self.att_icrf_s_x = self._io.read_f8le()
            self.att_icrf_s_y = self._io.read_f8le()
            self.att_icrf_s_z = self._io.read_f8le()
            self.last_rssi_time = self._io.read_f8le()
            self.batt_percent = self._io.read_f4le()
            self.batt_volt = self._io.read_f4le()
            self.batt_current = self._io.read_f4le()
            self.powgen = self._io.read_f4le()
            self.eps_temp = self._io.read_f4le()
            self.batt_temp = self._io.read_f4le()
            self.cpu_temp = self._io.read_f4le()
            self.duplex_flag = self._io.read_u4le()
            self.nframes_recv_buf = self._io.read_u2le()
            self.last_rssi = self._io.read_u2le()
            self.antenna_deployed_status = self._io.read_u2le()
            self.powmode = self._io.read_s2le()
            self.callsign = (self._io.read_bytes(6)).decode(u"utf-8")


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
            self.callsign_ror = Neutron1.Callsign(_io__raw_callsign_ror, self, self._root)



