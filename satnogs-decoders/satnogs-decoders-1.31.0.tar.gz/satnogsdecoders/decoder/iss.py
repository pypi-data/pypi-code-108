# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Iss(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field data_type: ax25_frame.payload.info.data_type
    :field longitude: ax25_frame.payload.info.longitude
    :field speed_and_course: ax25_frame.payload.info.speed_and_course
    :field symbol_code: ax25_frame.payload.info.symbol_code
    :field sym_table_id: ax25_frame.payload.info.sym_table_id
    :field tlm_flag: ax25_frame.payload.info.tlm_flag
    :field status_message: ax25_frame.payload.info.tlm_data.status_message
    :field mode: ax25_frame.payload.info.tlm_data.mode
    :field temp: ax25_frame.payload.info.temp
    :field aprs_message: ax25_frame.payload.info.aprs_message
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Iss.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Iss.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Iss.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Iss.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Iss.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Iss.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Iss.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Iss.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Iss.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Iss.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Iss.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Iss.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Iss.Repeater(self._io, self, self._root)

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
            if _on == u"NA1SS ":
                self._raw_info = self._io.read_bytes_full()
                _io__raw_info = KaitaiStream(BytesIO(self._raw_info))
                self.info = Iss.AprsMicET(_io__raw_info, self, self._root)
            else:
                self._raw_info = self._io.read_bytes_full()
                _io__raw_info = KaitaiStream(BytesIO(self._raw_info))
                self.info = Iss.AprsT(_io__raw_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class AprsMicET(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_type = (self._io.read_bytes(1)).decode(u"ASCII")
            self.longitude = (self._io.read_bytes(3)).decode(u"ASCII")
            self.speed_and_course = (self._io.read_bytes(3)).decode(u"ASCII")
            self.symbol_code = (self._io.read_bytes(1)).decode(u"ASCII")
            self.sym_table_id = (self._io.read_bytes(1)).decode(u"ASCII")
            self.tlm_flag = (self._io.read_bytes(1)).decode(u"ASCII")
            _on = self.tlm_flag
            if _on == u"]":
                self._raw_tlm_data = self._io.read_bytes_full()
                _io__raw_tlm_data = KaitaiStream(BytesIO(self._raw_tlm_data))
                self.tlm_data = Iss.KenwoodTmd700T(_io__raw_tlm_data, self, self._root)
            else:
                self.tlm_data = self._io.read_bytes_full()

        @property
        def mic_e_callsign(self):
            if hasattr(self, '_m_mic_e_callsign'):
                return self._m_mic_e_callsign if hasattr(self, '_m_mic_e_callsign') else None

            io = self._root._io
            _pos = io.pos()
            io.seek(0)
            self._m_mic_e_callsign = [None] * (6)
            for i in range(6):
                self._m_mic_e_callsign[i] = io.read_u1()

            io.seek(_pos)
            return self._m_mic_e_callsign if hasattr(self, '_m_mic_e_callsign') else None

        @property
        def temp(self):
            if hasattr(self, '_m_temp'):
                return self._m_temp if hasattr(self, '_m_temp') else None

            self._m_temp = ((((self.mic_e_callsign[4] >> 1) - 80) * 10) + ((self.mic_e_callsign[5] >> 1) - 48))
            return self._m_temp if hasattr(self, '_m_temp') else None

        @property
        def aprs_message(self):
            if hasattr(self, '_m_aprs_message'):
                return self._m_aprs_message if hasattr(self, '_m_aprs_message') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_aprs_message = (self._io.read_bytes_full()).decode(u"ASCII")
            self._io.seek(_pos)
            return self._m_aprs_message if hasattr(self, '_m_aprs_message') else None


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class AprsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.aprs_message = (self._io.read_bytes_full()).decode(u"ASCII")


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
            self.rpt_callsign_raw = Iss.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Iss.SsidMask(self._io, self, self._root)


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
                _ = Iss.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


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
            self.callsign_ror = Iss.Callsign(_io__raw_callsign_ror, self, self._root)


    class KenwoodTmd700T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status_message = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def mode(self):
            if hasattr(self, '_m_mode'):
                return self._m_mode if hasattr(self, '_m_mode') else None

            _pos = self._io.pos()
            self._io.seek(10)
            self._m_mode = (self._io.read_bytes(3)).decode(u"ASCII")
            self._io.seek(_pos)
            return self._m_mode if hasattr(self, '_m_mode') else None



