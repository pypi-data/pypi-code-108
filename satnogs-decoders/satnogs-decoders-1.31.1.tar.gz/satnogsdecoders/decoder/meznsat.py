# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Meznsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field frame_length: frame_length
    :field callsign: ax25_frame.payload.ax25_info.beacon_type.callsign
    :field satellite_mode: ax25_frame.payload.ax25_info.beacon_type.satellite_mode
    :field day_of_month: ax25_frame.payload.ax25_info.beacon_type.day_of_month
    :field day_of_week: ax25_frame.payload.ax25_info.beacon_type.day_of_week
    :field hour: ax25_frame.payload.ax25_info.beacon_type.hour
    :field minute: ax25_frame.payload.ax25_info.beacon_type.minute
    :field sec: ax25_frame.payload.ax25_info.beacon_type.sec
    :field obc_reset_count: ax25_frame.payload.ax25_info.beacon_type.obc_reset_count
    :field obc_temp: ax25_frame.payload.ax25_info.beacon_type.obc_temp
    :field vbatt: ax25_frame.payload.ax25_info.beacon_type.vbatt
    :field sys_current: ax25_frame.payload.ax25_info.beacon_type.sys_current
    :field batt_temp: ax25_frame.payload.ax25_info.beacon_type.batt_temp
    :field ext_batt1_temp: ax25_frame.payload.ax25_info.beacon_type.ext_batt1_temp
    :field ext_batt2_temp: ax25_frame.payload.ax25_info.beacon_type.ext_batt2_temp
    :field eps_reboots: ax25_frame.payload.ax25_info.beacon_type.eps_reboots
    :field receiver_current: ax25_frame.payload.ax25_info.beacon_type.receiver_current
    :field transmitter_current: ax25_frame.payload.ax25_info.beacon_type.transmitter_current
    :field pa_temp: ax25_frame.payload.ax25_info.beacon_type.pa_temp
    :field pa_current: ax25_frame.payload.ax25_info.beacon_type.pa_current
    :field adcs_run_mode: ax25_frame.payload.ax25_info.beacon_type.adcs_run_mode
    :field estimated_x_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_x_angular_rate
    :field estimated_y_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_y_angular_rate
    :field estimated_z_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_z_angular_rate
    :field estimated_q1: ax25_frame.payload.ax25_info.beacon_type.estimated_q1
    :field estimated_q2: ax25_frame.payload.ax25_info.beacon_type.estimated_q2
    :field estimated_q3: ax25_frame.payload.ax25_info.beacon_type.estimated_q3
    :field ant_temp: ax25_frame.payload.ax25_info.beacon_type.ant_temp
    :field minus_z_temp: ax25_frame.payload.ax25_info.beacon_type.minus_z_temp
    :field plus_z_temp: ax25_frame.payload.ax25_info.beacon_type.plus_z_temp
    :field minus_y_temp: ax25_frame.payload.ax25_info.beacon_type.minus_y_temp
    :field plus_y_temp: ax25_frame.payload.ax25_info.beacon_type.plus_y_temp
    :field minus_x_temp: ax25_frame.payload.ax25_info.beacon_type.minus_x_temp
    :field plus_x_temp: ax25_frame.payload.ax25_info.beacon_type.plus_x_temp
    :field message: ax25_frame.payload.ax25_info.beacon_type.message
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    
    .. seealso::
       
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Meznsat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Meznsat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Meznsat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Meznsat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Meznsat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Meznsat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Meznsat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Meznsat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Meznsat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Meznsat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Meznsat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Meznsat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Meznsat.Repeater(self._io, self, self._root)

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
            if _on == u"A68MZ ":
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Meznsat.MeznsatPayload(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


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


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Meznsat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Meznsat.SsidMask(self._io, self, self._root)


    class Repeater(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_instance = []
            i = 0
            while True:
                _ = Meznsat.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class MeznsatTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(7)).decode(u"utf-8")
            self.satellite_mode = self._io.read_u1()
            self.day_of_month = self._io.read_u1()
            self.day_of_week = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.sec = self._io.read_u1()
            self.obc_reset_count = self._io.read_u4le()
            self.obc_temp = self._io.read_s2le()
            self.vbatt = self._io.read_u2le()
            self.sys_current = self._io.read_u2le()
            self.batt_temp = self._io.read_s2le()
            self.ext_batt1_temp = self._io.read_s2le()
            self.ext_batt2_temp = self._io.read_s2le()
            self.eps_reboots = self._io.read_u2le()
            self.receiver_current = self._io.read_u2le()
            self.transmitter_current = self._io.read_u2le()
            self.pa_temp = self._io.read_s2le()
            self.pa_current = self._io.read_u2le()
            self.adcs_run_mode = self._io.read_u1()
            self.estimated_x_angular_rate = self._io.read_s2le()
            self.estimated_y_angular_rate = self._io.read_s2le()
            self.estimated_z_angular_rate = self._io.read_s2le()
            self.estimated_q1 = self._io.read_u2le()
            self.estimated_q2 = self._io.read_u2le()
            self.estimated_q3 = self._io.read_u2le()
            self.ant_temp = self._io.read_s2le()
            self.minus_z_temp = self._io.read_s4le()
            self.plus_z_temp = self._io.read_s4le()
            self.minus_y_temp = self._io.read_s4le()
            self.plus_y_temp = self._io.read_s4le()
            self.minus_x_temp = self._io.read_s4le()
            self.plus_x_temp = self._io.read_s4le()


    class MeznsatPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._io.size()
            if _on == 78:
                self.beacon_type = Meznsat.MeznsatTlm(self._io, self, self._root)
            else:
                self.beacon_type = Meznsat.MeznsatGenericPacket(self._io, self, self._root)


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
            self.callsign_ror = Meznsat.Callsign(_io__raw_callsign_ror, self, self._root)


    class MeznsatGenericPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = (self._io.read_bytes_full()).decode(u"utf-8")


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


