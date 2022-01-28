# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aausat4(KaitaiStruct):
    """:field data_plus_hmac_length: packet.data_length.data_plus_hmac_length
    :field frame_length: frame_length
    :field csp_hdr_crc: packet.csp_header.crc
    :field csp_hdr_rdp: packet.csp_header.rdp
    :field csp_hdr_xtea: packet.csp_header.xtea
    :field csp_hdr_hmac: packet.csp_header.hmac
    :field csp_hdr_src_port: packet.csp_header.src_port
    :field csp_hdr_dst_port: packet.csp_header.dst_port
    :field csp_hdr_destination: packet.csp_header.destination
    :field csp_hdr_source: packet.csp_header.source
    :field csp_hdr_priority: packet.csp_header.priority
    :field subsystems_valid: packet.data.beacon.valid
    :field eps_boot_count: packet.data.beacon.eps.boot_count
    :field eps_boot_cause: packet.data.beacon.eps.boot_cause
    :field eps_uptime: packet.data.beacon.eps.uptime
    :field eps_rt_clock: packet.data.beacon.eps.rt_clock
    :field eps_ping_status: packet.data.beacon.eps.ping_status
    :field eps_subsystem_selfstatus: packet.data.beacon.eps.subsystem_selfstatus
    :field eps_battery_voltage: packet.data.beacon.eps.battery_voltage
    :field eps_cell_diff: packet.data.beacon.eps.cell_diff
    :field eps_battery_current: packet.data.beacon.eps.battery_current
    :field eps_solar_power: packet.data.beacon.eps.solar_power
    :field eps_temp: packet.data.beacon.eps.temp
    :field eps_pa_temp: packet.data.beacon.eps.pa_temp
    :field eps_main_voltage: packet.data.beacon.eps.main_voltage
    :field com_boot_count: packet.data.beacon.com.boot_count
    :field com_boot_cause: packet.data.beacon.com.boot_cause
    
    .. seealso::
       Source - https://github.com/aausat/aausat4_beacon_parser/blob/master/beacon.py
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.packet = Aausat4.Aausat4DataT(self._io, self, self._root)

    class ComT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boot_count_raw = self._io.read_u2be()

        @property
        def boot_count(self):
            if hasattr(self, '_m_boot_count'):
                return self._m_boot_count if hasattr(self, '_m_boot_count') else None

            self._m_boot_count = (self.boot_count_raw & 8191)
            return self._m_boot_count if hasattr(self, '_m_boot_count') else None

        @property
        def boot_cause(self):
            if hasattr(self, '_m_boot_cause'):
                return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

            self._m_boot_cause = ((self.boot_count_raw & 57344) >> 13)
            return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None


    class Aausat4HmacT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hmac = self._io.read_u2be()


    class EpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boot_count_raw = self._io.read_u2be()
            self.uptime = self._io.read_u4be()
            self.rt_clock = self._io.read_u4be()
            self.ping_status = self._io.read_u1()
            self.subsystem_selfstatus = self._io.read_u2be()
            self.battery_voltage = self._io.read_u1()
            self.cell_diff = self._io.read_s1()
            self.battery_current = self._io.read_s1()
            self.solar_power = self._io.read_u1()
            self.temp = self._io.read_s1()
            self.pa_temp = self._io.read_s1()
            self.main_voltage = self._io.read_s1()

        @property
        def boot_count(self):
            if hasattr(self, '_m_boot_count'):
                return self._m_boot_count if hasattr(self, '_m_boot_count') else None

            self._m_boot_count = (self.boot_count_raw & 8191)
            return self._m_boot_count if hasattr(self, '_m_boot_count') else None

        @property
        def boot_cause(self):
            if hasattr(self, '_m_boot_cause'):
                return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

            self._m_boot_cause = ((self.boot_count_raw & 57344) >> 13)
            return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None


    class Aausat4DataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.frame_length == 92:
                self.data_length = Aausat4.Aausat4LenT(self._io, self, self._root)

            self.csp_header = Aausat4.CspHeaderT(self._io, self, self._root)
            self.data = Aausat4.CspDataT(self._io, self, self._root)
            if  ((self._root.frame_length == 90) or (self._root.frame_length == 92)) :
                self.hmac = Aausat4.Aausat4HmacT(self._io, self, self._root)



    class Adcs1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(7)


    class Aausat4LenT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_plus_hmac_length = self._io.read_u2be()


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if  ((self._parent.csp_header.dst_port == 10) and (self._parent.csp_header.destination == 9)) :
                self.beacon = Aausat4.Aausat4BeaconT(self._io, self, self._root)



    class Ais2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(20)


    class Aausat4BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.valid = self._io.read_u1()
            self._raw_eps = self._io.read_bytes(20)
            _io__raw_eps = KaitaiStream(BytesIO(self._raw_eps))
            self.eps = Aausat4.EpsT(_io__raw_eps, self, self._root)
            self._raw_com = self._io.read_bytes(10)
            _io__raw_com = KaitaiStream(BytesIO(self._raw_com))
            self.com = Aausat4.ComT(_io__raw_com, self, self._root)
            self.adcs1 = Aausat4.Adcs1T(self._io, self, self._root)
            self.adcs2 = Aausat4.Adcs2T(self._io, self, self._root)
            self.ais1 = Aausat4.Ais1T(self._io, self, self._root)
            self.ais2 = Aausat4.Ais2T(self._io, self, self._root)


    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_flags = [None] * (4)
            for i in range(4):
                self.csp_flags[i] = self._io.read_u1()


        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source if hasattr(self, '_m_source') else None

            self._m_source = ((self.csp_flags[3] >> 1) & 31)
            return self._m_source if hasattr(self, '_m_source') else None

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp if hasattr(self, '_m_rdp') else None

            self._m_rdp = ((self.csp_flags[0] >> 1) & 1)
            return self._m_rdp if hasattr(self, '_m_rdp') else None

        @property
        def src_port(self):
            if hasattr(self, '_m_src_port'):
                return self._m_src_port if hasattr(self, '_m_src_port') else None

            self._m_src_port = (self.csp_flags[1] & 63)
            return self._m_src_port if hasattr(self, '_m_src_port') else None

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination if hasattr(self, '_m_destination') else None

            self._m_destination = (((self.csp_flags[2] | (self.csp_flags[3] << 8)) >> 4) & 31)
            return self._m_destination if hasattr(self, '_m_destination') else None

        @property
        def dst_port(self):
            if hasattr(self, '_m_dst_port'):
                return self._m_dst_port if hasattr(self, '_m_dst_port') else None

            self._m_dst_port = (((self.csp_flags[1] | (self.csp_flags[2] << 8)) >> 6) & 63)
            return self._m_dst_port if hasattr(self, '_m_dst_port') else None

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority if hasattr(self, '_m_priority') else None

            self._m_priority = (self.csp_flags[3] >> 6)
            return self._m_priority if hasattr(self, '_m_priority') else None

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved if hasattr(self, '_m_reserved') else None

            self._m_reserved = (self.csp_flags[0] >> 4)
            return self._m_reserved if hasattr(self, '_m_reserved') else None

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea if hasattr(self, '_m_xtea') else None

            self._m_xtea = ((self.csp_flags[0] >> 2) & 1)
            return self._m_xtea if hasattr(self, '_m_xtea') else None

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac if hasattr(self, '_m_hmac') else None

            self._m_hmac = ((self.csp_flags[0] >> 3) & 1)
            return self._m_hmac if hasattr(self, '_m_hmac') else None

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc if hasattr(self, '_m_crc') else None

            self._m_crc = (self.csp_flags[0] & 1)
            return self._m_crc if hasattr(self, '_m_crc') else None


    class Adcs2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(6)


    class Ais1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(20)


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


