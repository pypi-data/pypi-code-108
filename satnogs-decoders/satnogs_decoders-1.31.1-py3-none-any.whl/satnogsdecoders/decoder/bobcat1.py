# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bobcat1(KaitaiStruct):
    """:field data: frame.cspheader.data
    :field callsign: frame.data.callsigns.callsign
    :field bobcat1: frame.data.callsigns.bobcat1
    :field bat_v: frame.data.bat_v
    :field bat_i_out: frame.data.bat_i_out
    :field bat_i_in: frame.data.bat_i_in
    :field bootcount_a3200: frame.data.bootcount_a3200
    :field resetcause_a3200: frame.data.resetcause_a3200
    :field bootcause_a3200: frame.data.bootcause_a3200
    :field uptime_a3200: frame.data.uptime_a3200
    :field bootcount_ax100: frame.data.bootcount_ax100
    :field bootcause_ax100: frame.data.bootcause_ax100
    :field i_pwm: frame.data.i_pwm
    :field fs_mounted: frame.data.fs_mounted
    :field antennas_deployed: frame.data.antennas_deployed
    :field deploy_attempts1: frame.data.deploy_attempts1
    :field deploy_attempts2: frame.data.deploy_attempts2
    :field deploy_attempts3: frame.data.deploy_attempts3
    :field deploy_attempts4: frame.data.deploy_attempts4
    :field gyro_x: frame.data.gyro_x
    :field gyro_y: frame.data.gyro_y
    :field gyro_z: frame.data.gyro_z
    :field timestamp: frame.data.timestamp
    :field protocol_version: frame.hk_header.protocol_version
    :field type: frame.hk_header.type
    :field version: frame.hk_header.version
    :field satid: frame.hk_header.satid
    :field checksum: frame.hk_frame.a3200_hktable0.checksum
    :field a3200_hktable0_timestamp: frame.hk_frame.a3200_hktable0.timestamp
    :field source: frame.hk_frame.a3200_hktable0.source
    :field callsign: frame.hk_frame.callsigns.callsign
    :field bobcat1: frame.hk_frame.callsigns.bobcat1
    :field bat_v: frame.hk_frame.bat_v
    :field bat_i_in: frame.hk_frame.bat_i_in
    :field bat_i_out: frame.hk_frame.bat_i_out
    :field solar1_i: frame.hk_frame.solar1_i
    :field solar1_v: frame.hk_frame.solar1_v
    :field solar2_i: frame.hk_frame.solar2_i
    :field solar2_v: frame.hk_frame.solar2_v
    :field solar3_i: frame.hk_frame.solar3_i
    :field solar3_v: frame.hk_frame.solar3_v
    :field novatel_i: frame.hk_frame.novatel_i
    :field sdr_i: frame.hk_frame.sdr_i
    :field bootcount_p31: frame.hk_frame.bootcount_p31
    :field bootcause_p31: frame.hk_frame.bootcause_p31
    :field bootcount_a3200: frame.hk_frame.bootcount_a3200
    :field bootcause_a3200: frame.hk_frame.bootcause_a3200
    :field resetcause_a3200: frame.hk_frame.resetcause_a3200
    :field uptime_a3200: frame.hk_frame.uptime_a3200
    :field temp_mcu: frame.hk_frame.temp_mcu
    :field i_gssb1: frame.hk_frame.i_gssb1
    :field i_pwm: frame.hk_frame.i_pwm
    :field panel_temp1: frame.hk_frame.panel_temp1
    :field panel_temp2: frame.hk_frame.panel_temp2
    :field panel_temp3: frame.hk_frame.panel_temp3
    :field panel_temp4: frame.hk_frame.panel_temp4
    :field panel_temp5: frame.hk_frame.panel_temp5
    :field panel_temp6: frame.hk_frame.panel_temp6
    :field panel_temp7: frame.hk_frame.panel_temp7
    :field panel_temp8: frame.hk_frame.panel_temp8
    :field panel_temp9: frame.hk_frame.panel_temp9
    :field p31_temp1: frame.hk_frame.p31_temp1
    :field p31_temp2: frame.hk_frame.p31_temp2
    :field p31_temp3: frame.hk_frame.p31_temp3
    :field p31_temp4: frame.hk_frame.p31_temp4
    :field p31_temp5: frame.hk_frame.p31_temp5
    :field p31_temp6: frame.hk_frame.p31_temp6
    :field flash0_free: frame.hk_frame.flash0_free
    :field flash1_free: frame.hk_frame.flash1_free
    :field coll_running: frame.hk_frame.coll_running
    :field ax100_telemtable_checksum: frame.hk_frame.ax100_telemtable.checksum
    :field ax100_telemtable_timestamp: frame.hk_frame.ax100_telemtable.timestamp
    :field ax100_telemtable_source: frame.hk_frame.ax100_telemtable.source
    :field temp_brd: frame.hk_frame.temp_brd
    :field temp_pa: frame.hk_frame.temp_pa
    :field bgnd_rssi: frame.hk_frame.bgnd_rssi
    :field tot_tx_count: frame.hk_frame.tot_tx_count
    :field tot_rx_count: frame.hk_frame.tot_rx_count
    :field tot_tx_bytes: frame.hk_frame.tot_tx_bytes
    :field tot_rx_bytes: frame.hk_frame.tot_rx_bytes
    :field bootcount_ax100: frame.hk_frame.bootcount_ax100
    :field bootcause_ax100: frame.hk_frame.bootcause_ax100
    :field a3200_hktable_17_1_checksum: frame.extra_frame.a3200_hktable_17_1.checksum
    :field a3200_hktable_17_1_timestamp: frame.extra_frame.a3200_hktable_17_1.timestamp
    :field a3200_hktable_17_1_source: frame.extra_frame.a3200_hktable_17_1.source
    :field callsign: frame.extra_frame.callsigns.callsign
    :field bobcat1: frame.extra_frame.callsigns.bobcat1
    :field coll_running: frame.extra_frame.coll_running
    :field lat: frame.extra_frame.lat
    :field long: frame.extra_frame.long
    :field height: frame.extra_frame.height
    :field sec_of_week: frame.extra_frame.sec_of_week
    :field a3200_hktable_10_checksum: frame.extra_frame.a3200_hktable_10.checksum
    :field a3200_hktable_10_timestamp: frame.extra_frame.a3200_hktable_10.timestamp
    :field a3200_hktable_10_source: frame.extra_frame.a3200_hktable_10.source
    :field cfg_path: frame.extra_frame.cfg_path
    :field bc1_wdcnt: frame.extra_frame.bc1_wdcnt
    :field collect_id: frame.extra_frame.collect_id
    :field adcs_mode: frame.extra_frame.adcs_mode
    :field a3200_hktable_17_2_checksum: frame.extra_frame.a3200_hktable_17_2.checksum
    :field a3200_hktable_17_2_timestamp: frame.extra_frame.a3200_hktable_17_2.timestamp
    :field a3200_hktable_17_2_source: frame.extra_frame.a3200_hktable_17_2.source
    :field custom_message: frame.extra_frame.custom_message
    :field framelength: framelength
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        _on = self._root.framelength
        if _on == 69:
            self.frame = Bobcat1.Bc1BasicFrame(self._io, self, self._root)
        elif _on == 156:
            self.frame = Bobcat1.Bc1HkFrame(self._io, self, self._root)
        elif _on == 150:
            self.frame = Bobcat1.Bc1ExtraFrame(self._io, self, self._root)

    class BeaconElementHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.checksum = self._io.read_u2be()
            self.timestamp = self._io.read_u4be()
            self.source = self._io.read_u2be()


    class Cspheader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_u4be()


    class Bc1HkFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cspheader = Bobcat1.Cspheader(self._io, self, self._root)
            self.hk_header = Bobcat1.HkHeader(self._io, self, self._root)
            self.hk_frame = Bobcat1.HkData(self._io, self, self._root)


    class ExtraData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a3200_hktable_17_1 = Bobcat1.BeaconElementHeader(self._io, self, self._root)
            self.callsigns = Bobcat1.Callsigns(self._io, self, self._root)
            self.coll_running = self._io.read_u1()
            self.lat = self._io.read_f4be()
            self.long = self._io.read_f4be()
            self.height = self._io.read_f4be()
            self.sec_of_week = self._io.read_u2be()
            self.a3200_hktable_10 = Bobcat1.BeaconElementHeader(self._io, self, self._root)
            self.cfg_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(50), 0, False)).decode(u"ASCII")
            self.bc1_wdcnt = self._io.read_u4be()
            self.collect_id = self._io.read_u4be()
            self.adcs_mode = self._io.read_u1()
            self.a3200_hktable_17_2 = Bobcat1.BeaconElementHeader(self._io, self, self._root)
            self.custom_message = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")


    class HkData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a3200_hktable0 = Bobcat1.BeaconElementHeader(self._io, self, self._root)
            self.callsigns = Bobcat1.Callsigns(self._io, self, self._root)
            self.bat_v = self._io.read_u2be()
            self.bat_i_in = self._io.read_u2be()
            self.bat_i_out = self._io.read_u2be()
            self.solar1_i = self._io.read_u2be()
            self.solar1_v = self._io.read_u2be()
            self.solar2_i = self._io.read_u2be()
            self.solar2_v = self._io.read_u2be()
            self.solar3_i = self._io.read_u2be()
            self.solar3_v = self._io.read_u2be()
            self.novatel_i = self._io.read_u2be()
            self.sdr_i = self._io.read_u2be()
            self.bootcount_p31 = self._io.read_u4be()
            self.bootcause_p31 = self._io.read_u1()
            self.bootcount_a3200 = self._io.read_u2be()
            self.bootcause_a3200 = self._io.read_u1()
            self.resetcause_a3200 = self._io.read_u1()
            self.uptime_a3200 = self._io.read_u4be()
            self.temp_mcu = self._io.read_s2be()
            self.i_gssb1 = self._io.read_u2be()
            self.i_pwm = self._io.read_u2be()
            self.panel_temp1 = self._io.read_s2be()
            self.panel_temp2 = self._io.read_s2be()
            self.panel_temp3 = self._io.read_s2be()
            self.panel_temp4 = self._io.read_s2be()
            self.panel_temp5 = self._io.read_s2be()
            self.panel_temp6 = self._io.read_s2be()
            self.panel_temp7 = self._io.read_s2be()
            self.panel_temp8 = self._io.read_s2be()
            self.panel_temp9 = self._io.read_s2be()
            self.p31_temp1 = self._io.read_s2be()
            self.p31_temp2 = self._io.read_s2be()
            self.p31_temp3 = self._io.read_s2be()
            self.p31_temp4 = self._io.read_s2be()
            self.p31_temp5 = self._io.read_s2be()
            self.p31_temp6 = self._io.read_s2be()
            self.flash0_free = self._io.read_u4be()
            self.flash1_free = self._io.read_u4be()
            self.coll_running = self._io.read_u1()
            self.ax100_telemtable = Bobcat1.BeaconElementHeader(self._io, self, self._root)
            self.temp_brd = self._io.read_s2be()
            self.temp_pa = self._io.read_s2be()
            self.bgnd_rssi = self._io.read_s2be()
            self.tot_tx_count = self._io.read_u4be()
            self.tot_rx_count = self._io.read_u4be()
            self.tot_tx_bytes = self._io.read_u4be()
            self.tot_rx_bytes = self._io.read_u4be()
            self.bootcount_ax100 = self._io.read_u2be()
            self.bootcause_ax100 = self._io.read_u4be()


    class Bc1ExtraFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cspheader = Bobcat1.Cspheader(self._io, self, self._root)
            self.hk_header = Bobcat1.HkHeader(self._io, self, self._root)
            self.extra_frame = Bobcat1.ExtraData(self._io, self, self._root)


    class HkHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.protocol_version = self._io.read_u1()
            self.type = self._io.read_u1()
            self.version = self._io.read_u1()
            self.satid = self._io.read_u2be()


    class Basic(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsigns = Bobcat1.Callsigns(self._io, self, self._root)
            self.bat_v = self._io.read_u2be()
            self.bat_i_out = self._io.read_u2be()
            self.bat_i_in = self._io.read_u2be()
            self.bootcount_a3200 = self._io.read_u2be()
            self.resetcause_a3200 = self._io.read_u1()
            self.bootcause_a3200 = self._io.read_u1()
            self.uptime_a3200 = self._io.read_u4be()
            self.bootcount_ax100 = self._io.read_u2be()
            self.bootcause_ax100 = self._io.read_u4be()
            self.i_pwm = self._io.read_u2be()
            self.fs_mounted = self._io.read_u1()
            self.antennas_deployed = self._io.read_u1()
            self.deploy_attempts1 = self._io.read_u2be()
            self.deploy_attempts2 = self._io.read_u2be()
            self.deploy_attempts3 = self._io.read_u2be()
            self.deploy_attempts4 = self._io.read_u2be()
            self.gyro_x = self._io.read_s2be()
            self.gyro_y = self._io.read_s2be()
            self.gyro_z = self._io.read_s2be()
            self.timestamp = self._io.read_u4be()


    class Callsigns(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            if not self.callsign == u"W8PZS":
                raise kaitaistruct.ValidationNotEqualError(u"W8PZS", self.callsign, self._io, u"/types/callsigns/seq/0")
            self.bobcat1 = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            if not self.bobcat1 == u"BOBCAT-1":
                raise kaitaistruct.ValidationNotEqualError(u"BOBCAT-1", self.bobcat1, self._io, u"/types/callsigns/seq/1")


    class Bc1BasicFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cspheader = Bobcat1.Cspheader(self._io, self, self._root)
            self.data = Bobcat1.Basic(self._io, self, self._root)


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


