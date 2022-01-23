# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Alsat1n(KaitaiStruct):
    """:field callsign: callsign
    :field strx_header_seq: alsat1n_payload.strx_header.strx_header_seq
    :field strx_header_len: alsat1n_payload.strx_header.strx_header_len
    :field strx_header_id: alsat1n_payload.strx_header.strx_header_id
    :field payload_id: alsat1n_payload.ssc_header.payload_id
    :field msg_id: alsat1n_payload.ssc_header.msg_id
    :field response_code: alsat1n_payload.ssc_header.response_code
    :field p8_state: alsat1n_payload.ssc_channel.payload_type.msg_type.p8_state
    :field p8_current: alsat1n_payload.ssc_channel.payload_type.msg_type.p8_current
    :field p8_voltage: alsat1n_payload.ssc_channel.payload_type.msg_type.p8_voltage
    :field p7_state: alsat1n_payload.ssc_channel.payload_type.msg_type.p7_state
    :field p7_current: alsat1n_payload.ssc_channel.payload_type.msg_type.p7_current
    :field p7_voltage: alsat1n_payload.ssc_channel.payload_type.msg_type.p7_voltage
    :field ipcm5v: alsat1n_payload.ssc_channel.payload_type.msg_type.ipcm5v
    :field ipcm3v3: alsat1n_payload.ssc_channel.payload_type.msg_type.ipcm3v3
    :field ipcmbatv: alsat1n_payload.ssc_channel.payload_type.msg_type.ipcmbatv
    :field vpcmbatv: alsat1n_payload.ssc_channel.payload_type.msg_type.vpcmbatv
    :field eps_temperature: alsat1n_payload.ssc_channel.payload_type.msg_type.eps_temperature
    :field s1_state_3v3: alsat1n_payload.ssc_channel.payload_type.msg_type.s1_state_3v3
    :field s1_current_3v3: alsat1n_payload.ssc_channel.payload_type.msg_type.s1_current_3v3
    :field s1_voltage_3v3: alsat1n_payload.ssc_channel.payload_type.msg_type.s1_voltage_3v3
    :field s2_state_5v: alsat1n_payload.ssc_channel.payload_type.msg_type.s2_state_5v
    :field s2_current_5v: alsat1n_payload.ssc_channel.payload_type.msg_type.s2_current_5v
    :field s2_voltage_5v: alsat1n_payload.ssc_channel.payload_type.msg_type.s2_voltage_5v
    :field pdm_uptime_payload_h: alsat1n_payload.ssc_channel.payload_type.msg_type.pdm_uptime_payload_h
    :field pdm_uptime_payload_l: alsat1n_payload.ssc_channel.payload_type.msg_type.pdm_uptime_payload_l
    :field pdm_uptime_platform_h: alsat1n_payload.ssc_channel.payload_type.msg_type.pdm_uptime_platform_h
    :field pdm_uptime_platform_l: alsat1n_payload.ssc_channel.payload_type.msg_type.pdm_uptime_platform_l
    :field software_ident: alsat1n_payload.ssc_channel.payload_type.msg_type.software_ident
    :field uptime: alsat1n_payload.ssc_channel.payload_type.msg_type.uptime
    :field eps_voltage_battery: alsat1n_payload.ssc_channel.payload_type.msg_type.eps_voltage_battery
    :field eps_current_battery: alsat1n_payload.ssc_channel.payload_type.msg_type.eps_current_battery
    :field safe_mode: alsat1n_payload.ssc_channel.payload_type.msg_type.safe_mode
    :field safe_reason: alsat1n_payload.ssc_channel.payload_type.msg_type.safe_reason
    :field unix_time: alsat1n_payload.ssc_channel.payload_type.msg_type.unix_time
    :field reboot_num: alsat1n_payload.ssc_channel.payload_type.msg_type.reboot_num
    :field reboot_cause: alsat1n_payload.ssc_channel.payload_type.msg_type.reboot_cause
    :field i2c_traffic_cnt: alsat1n_payload.ssc_channel.payload_type.msg_type.i2c_traffic_cnt
    :field watchdog_time_remaining: alsat1n_payload.ssc_channel.payload_type.msg_type.watchdog_time_remaining
    :field amrad: alsat1n_payload.ssc_channel.payload_type.msg_type.amrad
    :field current_packet: alsat1n_payload.ssc_channel.payload_type.msg_type.current_packet
    :field block_id: alsat1n_payload.ssc_channel.payload_type.msg_type.block_id
    :field file_data: alsat1n_payload.ssc_channel.payload_type.msg_type.bin_file_data.file_data
    :field file_store: alsat1n_payload.ssc_channel.payload_type.msg_type.file_store
    :field file_type: alsat1n_payload.ssc_channel.payload_type.msg_type.file_type
    :field file_count: alsat1n_payload.ssc_channel.payload_type.msg_type.file_count
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(5), 0, False)).decode(u"ASCII")
        _on = self.callsign
        if _on == u"AL1N":
            self.alsat1n_payload = Alsat1n.Alsat1nPayloadT(self._io, self, self._root)

    class WatchdogTimeRemaining(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.watchdog_time_remaining = self._io.read_u4le()


    class AmradMsg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.amrad = (self._io.read_bytes(40)).decode(u"ASCII")


    class PdmPlatform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pdm_uptime_platform_h = self._io.read_u4le()
            self.pdm_uptime_platform_l = self._io.read_u4le()


    class EpsPlatform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.s1_state_3v3 = self._io.read_u1()
            self.s1_current_3v3 = self._io.read_u2le()
            self.s1_voltage_3v3 = self._io.read_u2le()
            self.s2_state_5v = self._io.read_u1()
            self.s2_current_5v = self._io.read_u2le()
            self.s2_voltage_5v = self._io.read_u2le()


    class P7Psu(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.p7_state = self._io.read_u1()
            self.p7_current = self._io.read_u2le()
            self.p7_voltage = self._io.read_u2le()


    class SscHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.payload_id = self._io.read_u1()
            self.msg_id = self._io.read_u1()
            self.response_code = self._io.read_u1()


    class StrxHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.strx_header_seq = self._io.read_u1()
            self.strx_header_len = self._io.read_u2le()
            self.strx_header_id = self._io.read_u2le()


    class DownloadData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current_packet = self._io.read_u2le()
            self.block_id = self._io.read_u2le()
            self._raw__raw_bin_file_data = self._io.read_bytes_full()
            _process = satnogsdecoders.process.B85encode()
            self._raw_bin_file_data = _process.decode(self._raw__raw_bin_file_data)
            _io__raw_bin_file_data = KaitaiStream(BytesIO(self._raw_bin_file_data))
            self.bin_file_data = Alsat1n.EncodedDataT(_io__raw_bin_file_data, self, self._root)


    class EncodedDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_data = (self._io.read_bytes_full()).decode(u"ASCII")


    class SscChannelT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.ssc_header.payload_id
            if _on == 5:
                self.payload_type = Alsat1n.Obc(self._io, self, self._root)
            elif _on == 19:
                self.payload_type = Alsat1n.File(self._io, self, self._root)
            elif _on == 46:
                self.payload_type = Alsat1n.Eps(self._io, self, self._root)


    class I2cTraffic(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_traffic_cnt = self._io.read_u4le()


    class PdmPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pdm_uptime_payload_h = self._io.read_u4le()
            self.pdm_uptime_payload_l = self._io.read_u4le()


    class Eps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent._parent.ssc_header.msg_id
            if _on == 244:
                self.msg_type = Alsat1n.EpsPlatform(self._io, self, self._root)
            elif _on == 161:
                self.msg_type = Alsat1n.P7Psu(self._io, self, self._root)
            elif _on == 63:
                self.msg_type = Alsat1n.EpsPsuCurrent5v(self._io, self, self._root)
            elif _on == 166:
                self.msg_type = Alsat1n.P8Psu(self._io, self, self._root)
            elif _on == 65:
                self.msg_type = Alsat1n.EpsPsuCurrent3v3(self._io, self, self._root)
            elif _on == 122:
                self.msg_type = Alsat1n.PdmPlatform(self._io, self, self._root)
            elif _on == 240:
                self.msg_type = Alsat1n.EpsSys(self._io, self, self._root)
            elif _on == 175:
                self.msg_type = Alsat1n.PdmPayload(self._io, self, self._root)


    class Alsat1nPayloadT(KaitaiStruct):
        """
        .. seealso::
           Source - https://amsat-uk.org/2016/09/24/alsat-1n-pratham-launch/
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.strx_header = Alsat1n.StrxHeaderT(self._io, self, self._root)
            self.ssc_header = Alsat1n.SscHeaderT(self._io, self, self._root)
            self.ssc_channel = Alsat1n.SscChannelT(self._io, self, self._root)


    class EpsPsuCurrent3v3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ipcm3v3 = self._io.read_u2le()


    class File(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent._parent.ssc_header.msg_id
            if _on == 21:
                self.msg_type = Alsat1n.DownloadData(self._io, self, self._root)
            elif _on == 30:
                self.msg_type = Alsat1n.FileCount(self._io, self, self._root)


    class FileCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_store = self._io.read_u1()
            self.file_type = self._io.read_u1()
            self.file_count = self._io.read_u2le()


    class Obc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent._parent.ssc_header.msg_id
            if _on == 1:
                self.msg_type = Alsat1n.ObcHealth(self._io, self, self._root)
            elif _on == 32:
                self.msg_type = Alsat1n.I2cTraffic(self._io, self, self._root)
            elif _on == 127:
                self.msg_type = Alsat1n.WatchdogTimeRemaining(self._io, self, self._root)
            elif _on == 176:
                self.msg_type = Alsat1n.AmradMsg(self._io, self, self._root)


    class EpsSys(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ipcmbatv = self._io.read_u2le()
            self.vpcmbatv = self._io.read_u2le()
            self.eps_temperature = self._io.read_u2le()


    class P8Psu(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.p8_state = self._io.read_u1()
            self.p8_current = self._io.read_u2le()
            self.p8_voltage = self._io.read_u2le()


    class ObcHealth(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.software_ident = self._io.read_u1()
            self.uptime = self._io.read_u4le()
            self.eps_voltage_battery = self._io.read_u2le()
            self.eps_current_battery = self._io.read_u2le()
            self.safe_mode = self._io.read_u1()
            self.safe_reason = self._io.read_u1()
            self.unix_time = self._io.read_u4le()
            self.reboot_num = self._io.read_u1()
            self.reboot_cause = self._io.read_u1()


    class EpsPsuCurrent5v(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ipcm5v = self._io.read_u2le()



