# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Entrysat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_id: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.packet_id
    :field packet_seq_ctl: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.packet_seq_ctl
    :field packet_length: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.packet_length
    :field service: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.service
    :field subservice: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.subservice
    :field clock: ax25_frame.payload.ax25_info.pus_packet.tm_packet_header.clock
    :field sid: ax25_frame.payload.ax25_info.pus_packet.payload.sid
    :field mode: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.mode
    :field eps_vbatt: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.eps_vbatt
    :field eps_batt_vcurrent: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.eps_batt_vcurrent
    :field eps_3v3_current: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.eps_3v3_current
    :field eps_5v_current: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.eps_5v_current
    :field trx_temp: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.trx_temp
    :field eps_temp: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.eps_temp
    :field batt_temp: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.batt_temp
    :field frame_status: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.frame_status
    :field timestamp: ax25_frame.payload.ax25_info.pus_packet.payload.tm_payload.timestamp
    
    
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
        self.ax25_frame = Entrysat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Entrysat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Entrysat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Entrysat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Entrysat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Entrysat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Entrysat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Entrysat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Entrysat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Entrysat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Entrysat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Entrysat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Entrysat.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Entrysat.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Entrysat.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class PusPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp_unused = self._io.read_u4be()
            self.tm_packet_header = Entrysat.TmPacketHeaderT(self._io, self, self._root)
            self.payload = Entrysat.TmPacketT(self._io, self, self._root)


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
            self.rpt_callsign_raw = Entrysat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Entrysat.SsidMask(self._io, self, self._root)


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
                _ = Entrysat.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class TmPacketHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_id = self._io.read_u2be()
            self.packet_seq_ctl = self._io.read_u2be()
            self.packet_length = self._io.read_u2be()
            self.spare_tm = self._io.read_u1()
            self.service = self._io.read_u1()
            self.subservice = self._io.read_u1()
            self.clock_array = [None] * (5)
            for i in range(5):
                self.clock_array[i] = self._io.read_u1()


        @property
        def clock(self):
            if hasattr(self, '_m_clock'):
                return self._m_clock if hasattr(self, '_m_clock') else None

            self._m_clock = (((((((self.clock_array[0] * 256) * 256) * 256) + ((self.clock_array[1] * 256) * 256)) + (self.clock_array[2] * 256)) + self.clock_array[3]) + (self.clock_array[4] / 256.0))
            return self._m_clock if hasattr(self, '_m_clock') else None


    class TmPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sid = self._io.read_u1()
            _on = self.sid
            if _on == 6:
                self.tm_payload = Entrysat.EpsPacketT(self._io, self, self._root)


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
            self.callsign_ror = Entrysat.Callsign(_io__raw_callsign_ror, self, self._root)


    class EpsPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = self._io.read_u1()
            self.eps_vbatt = self._io.read_u1()
            self.eps_batt_vcurrent = self._io.read_u1()
            self.eps_3v3_current = self._io.read_u1()
            self.eps_5v_current = self._io.read_u1()
            self.trx_temp = self._io.read_u1()
            self.eps_temp = self._io.read_u1()
            self.batt_temp = self._io.read_u1()
            self.crc = self._io.read_u2be()
            self.frame_status = self._io.read_u1()
            self.timestamp = self._io.read_u4le()


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pus_packet = Entrysat.PusPacketT(self._io, self, self._root)



