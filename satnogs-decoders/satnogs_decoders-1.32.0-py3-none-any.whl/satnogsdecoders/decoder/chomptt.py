# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Chomptt(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field identifier: ax25_frame.payload.ax25_info.identifier
    :field msg_num: ax25_frame.payload.ax25_info.chomptb85.msg_num
    :field time: ax25_frame.payload.ax25_info.chomptb85.time
    :field mode: ax25_frame.payload.ax25_info.chomptb85.mode
    :field idle_timer: ax25_frame.payload.ax25_info.chomptb85.idle_timer
    :field vbat: ax25_frame.payload.ax25_info.chomptb85.vbat
    :field spc_xp: ax25_frame.payload.ax25_info.chomptb85.spc_xp
    :field spc_xn: ax25_frame.payload.ax25_info.chomptb85.spc_xn
    :field spc_yp: ax25_frame.payload.ax25_info.chomptb85.spc_yp
    :field spc_zp: ax25_frame.payload.ax25_info.chomptb85.spc_zp
    :field spc_zn: ax25_frame.payload.ax25_info.chomptb85.spc_zn
    :field temp_b1: ax25_frame.payload.ax25_info.chomptb85.temp_b1
    :field temp_b3: ax25_frame.payload.ax25_info.chomptb85.temp_b3
    :field temp_b4: ax25_frame.payload.ax25_info.chomptb85.temp_b4
    :field temp_b5: ax25_frame.payload.ax25_info.chomptb85.temp_b5
    :field temp_b6: ax25_frame.payload.ax25_info.chomptb85.temp_b6
    :field temp_b9: ax25_frame.payload.ax25_info.chomptb85.temp_b9
    :field temp_xn: ax25_frame.payload.ax25_info.chomptb85.temp_xn
    :field temp_xp: ax25_frame.payload.ax25_info.chomptb85.temp_xp
    :field temp_yp: ax25_frame.payload.ax25_info.chomptb85.temp_yp
    :field temp_zn: ax25_frame.payload.ax25_info.chomptb85.temp_zn
    :field temp_zp: ax25_frame.payload.ax25_info.chomptb85.temp_zp
    :field v_bat: ax25_frame.payload.ax25_info.chomptb85.v_bat
    :field i_dog: ax25_frame.payload.ax25_info.chomptb85.i_dog
    :field i_sat: ax25_frame.payload.ax25_info.chomptb85.i_sat
    :field i_temp: ax25_frame.payload.ax25_info.chomptb85.i_temp
    :field i_gps_arduino: ax25_frame.payload.ax25_info.chomptb85.i_gps_arduino
    :field i_gps_novatel: ax25_frame.payload.ax25_info.chomptb85.i_gps_novatel
    :field i_sten: ax25_frame.payload.ax25_info.chomptb85.i_sten
    :field i_acs: ax25_frame.payload.ax25_info.chomptb85.i_acs
    :field i_rout: ax25_frame.payload.ax25_info.chomptb85.i_rout
    :field i_lit: ax25_frame.payload.ax25_info.chomptb85.i_lit
    :field mag_x: ax25_frame.payload.ax25_info.chomptb85.mag_x
    :field mag_y: ax25_frame.payload.ax25_info.chomptb85.mag_y
    :field mag_z: ax25_frame.payload.ax25_info.chomptb85.mag_z
    :field identifier: ax25_frame.payload.ax25_info.identifier
    :field flags: ax25_frame.payload.ax25_info.optib85.flags
    :field sup_t1: ax25_frame.payload.ax25_info.optib85.sup_t1
    :field sup_t2: ax25_frame.payload.ax25_info.optib85.sup_t2
    :field sup_vbat: ax25_frame.payload.ax25_info.optib85.sup_vbat
    :field ch1_flags: ax25_frame.payload.ax25_info.optib85.ch1_flags
    :field ch1_temp: ax25_frame.payload.ax25_info.optib85.ch1_temp
    :field csac1_temp: ax25_frame.payload.ax25_info.optib85.csac1_temp
    :field ch1_current: ax25_frame.payload.ax25_info.optib85.ch1_current
    :field ch2_flags: ax25_frame.payload.ax25_info.optib85.ch2_flags
    :field ch2_temp: ax25_frame.payload.ax25_info.optib85.ch2_temp
    :field csac2_temp: ax25_frame.payload.ax25_info.optib85.csac2_temp
    :field ch2_current: ax25_frame.payload.ax25_info.optib85.ch2_current
    :field count: ax25_frame.payload.ax25_info.optib85.count
    :field overflow: ax25_frame.payload.ax25_info.optib85.overflow
    
    .. seealso::
       Source - https://pssl.mae.ufl.edu/#chomptt/page/beacondecode
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Chomptt.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Chomptt.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Chomptt.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Chomptt.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Chomptt.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Chomptt.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Chomptt.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Chomptt.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Chomptt.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Chomptt.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Chomptt.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Chomptt.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Chomptt.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._root.framelength
            if _on == 69:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Chomptt.Optib85T(_io__raw_ax25_info, self, self._root)
            elif _on == 128:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Chomptt.Chomptb85T(_io__raw_ax25_info, self, self._root)
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
            self.rpt_callsign_raw = Chomptt.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Chomptt.SsidMask(self._io, self, self._root)


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
                _ = Chomptt.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class Optib85T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes(4)).decode(u"ASCII")
            self.sod = self._io.read_bytes(2)
            self._raw__raw_optib85 = self._io.read_bytes(38)
            _process = satnogsdecoders.process.B85decode()
            self._raw_optib85 = _process.decode(self._raw__raw_optib85)
            _io__raw_optib85 = KaitaiStream(BytesIO(self._raw_optib85))
            self.optib85 = Chomptt.OptiT(_io__raw_optib85, self, self._root)
            self.eod = self._io.read_bytes(2)


    class OptiT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u2le()
            self.sup_t1 = self._io.read_s2le()
            self.sup_t2 = self._io.read_s2le()
            self.sup_vbat = self._io.read_s2le()
            self.ch1_flags = self._io.read_u2le()
            self.ch1_temp = self._io.read_s2le()
            self.csac1_temp = self._io.read_s2le()
            self.ch1_current = self._io.read_s2le()
            self.ch2_flags = self._io.read_u2le()
            self.ch2_temp = self._io.read_s2le()
            self.csac2_temp = self._io.read_s2le()
            self.ch2_current = self._io.read_s2le()
            self.count = self._io.read_u2le()
            self.overflow = self._io.read_u4le()


    class ChomptT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.msg_num = self._io.read_u2le()
            self.time = self._io.read_u4le()
            self.mode = self._io.read_u1()
            self.idle_timer = self._io.read_u2le()
            self.vbat = self._io.read_u2le()
            self.spc_xp = self._io.read_s2le()
            self.spc_xn = self._io.read_s2le()
            self.spc_yp = self._io.read_s2le()
            self.spc_zp = self._io.read_s2le()
            self.spc_zn = self._io.read_s2le()
            self.temp_b1 = self._io.read_u2le()
            self.temp_b3 = self._io.read_u2le()
            self.temp_b4 = self._io.read_u2le()
            self.temp_b5 = self._io.read_u2le()
            self.temp_b6 = self._io.read_u2le()
            self.temp_b9 = self._io.read_u2le()
            self.temp_xn = self._io.read_s2le()
            self.temp_xp = self._io.read_s2le()
            self.temp_yp = self._io.read_s2le()
            self.temp_zn = self._io.read_s2le()
            self.temp_zp = self._io.read_s2le()
            self.v_bat = self._io.read_s2le()
            self.i_dog = self._io.read_s2le()
            self.i_sat = self._io.read_s2le()
            self.i_temp = self._io.read_s2le()
            self.i_gps_arduino = self._io.read_s2le()
            self.i_gps_novatel = self._io.read_s2le()
            self.i_sten = self._io.read_s2le()
            self.i_acs = self._io.read_s2le()
            self.i_rout = self._io.read_s2le()
            self.i_lit = self._io.read_s2le()
            self.mag_x = self._io.read_f4le()
            self.mag_y = self._io.read_f4le()
            self.mag_z = self._io.read_f4le()


    class Chomptb85T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes_term(92, False, True, True)).decode(u"ASCII")
            self.sod = self._io.read_bytes(2)
            self._raw__raw_chomptb85 = self._io.read_bytes(94)
            _process = satnogsdecoders.process.B85decode()
            self._raw_chomptb85 = _process.decode(self._raw__raw_chomptb85)
            _io__raw_chomptb85 = KaitaiStream(BytesIO(self._raw_chomptb85))
            self.chomptb85 = Chomptt.ChomptT(_io__raw_chomptb85, self, self._root)
            self.eod = self._io.read_bytes(2)


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
            self.callsign_ror = Chomptt.Callsign(_io__raw_callsign_ror, self, self._root)


    @property
    def rpt1_callsign(self):
        if hasattr(self, '_m_rpt1_callsign'):
            return self._m_rpt1_callsign if hasattr(self, '_m_rpt1_callsign') else None

        self._m_rpt1_callsign = self.ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
        return self._m_rpt1_callsign if hasattr(self, '_m_rpt1_callsign') else None

    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


