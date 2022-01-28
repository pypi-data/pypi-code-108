# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Painani(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field short_internal_temperature: ax25_frame.payload.info.pld_id.short_internal_temperature
    :field short_pa_temperature: ax25_frame.payload.info.pld_id.short_pa_temperature
    :field short_current_3v3: ax25_frame.payload.info.pld_id.short_current_3v3
    :field short_voltage_3v3: ax25_frame.payload.info.pld_id.short_voltage_3v3
    :field short_current_5v: ax25_frame.payload.info.pld_id.short_current_5v
    :field short_voltage_5v: ax25_frame.payload.info.pld_id.short_voltage_5v
    :field id: ax25_frame.payload.info.pld_id.id
    :field length: ax25_frame.payload.info.pld_id.length
    :field antenna: ax25_frame.payload.info.pld_id.antenna
    :field temp_panel_1: ax25_frame.payload.info.pld_id.temp_panel_1
    :field temp_panel_2: ax25_frame.payload.info.pld_id.temp_panel_2
    :field temp_panel_3: ax25_frame.payload.info.pld_id.temp_panel_3
    :field temp_bank_1: ax25_frame.payload.info.pld_id.temp_bank_1
    :field temp_bank_2: ax25_frame.payload.info.pld_id.temp_bank_2
    :field charge_bank_1: ax25_frame.payload.info.pld_id.charge_bank_1
    :field charge_bank_2: ax25_frame.payload.info.pld_id.charge_bank_2
    :field gyro_x: ax25_frame.payload.info.pld_id.gyro_x
    :field gyro_y: ax25_frame.payload.info.pld_id.gyro_y
    :field gyro_z: ax25_frame.payload.info.pld_id.gyro_z
    :field state: ax25_frame.payload.info.pld_id.state
    :field reboots: ax25_frame.payload.info.pld_id.reboots
    :field rtc: ax25_frame.payload.info.pld_id.rtc
    :field voltage_bank_1: ax25_frame.payload.info.pld_id.voltage_bank_1
    :field voltage_bank_2: ax25_frame.payload.info.pld_id.voltage_bank_2
    :field current_bank_1: ax25_frame.payload.info.pld_id.current_bank_1
    :field current_bank_2: ax25_frame.payload.info.pld_id.current_bank_2
    :field gps: ax25_frame.payload.info.pld_id.gps
    :field voltage_3v3: ax25_frame.payload.info.pld_id.voltage_3v3
    :field battery_voltage: ax25_frame.payload.info.pld_id.byttery_voltage
    :field lna_voltage: ax25_frame.payload.info.pld_id.lna_voltage
    :field voltage_5v: ax25_frame.payload.info.pld_id.voltage_5v
    :field gps_voltage: ax25_frame.payload.info.pld_id.gps_voltage
    :field camera_voltage: ax25_frame.payload.info.pld_id.camera_voltage
    
    .. seealso::
       Source - https://dep.cicese.mx/csa/painani/telemetry.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Painani.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Painani.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 3:
                self.payload = Painani.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Painani.UiFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Painani.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Painani.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Painani.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Painani.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Painani.Repeater(self._io, self, self._root)

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
            if _on == u"SPACE ":
                self.info = Painani.PainaniPayloadIdentify(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class PainaniBeaconShort(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved = self._io.read_u4be()
            self.short_internal_temperature = self._io.read_s1()
            self.short_pa_temperature = self._io.read_s1()
            self.short_current_3v3 = self._io.read_s2be()
            self.short_voltage_3v3 = self._io.read_u2be()
            self.short_current_5v = self._io.read_s2be()
            self.short_voltage_5v = self._io.read_u2be()

        @property
        def cu33(self):
            if hasattr(self, '_m_cu33'):
                return self._m_cu33 if hasattr(self, '_m_cu33') else None

            self._m_cu33 = ((self.short_current_3v3 * 3) * 0.000001)
            return self._m_cu33 if hasattr(self, '_m_cu33') else None

        @property
        def v33(self):
            if hasattr(self, '_m_v33'):
                return self._m_v33 if hasattr(self, '_m_v33') else None

            self._m_v33 = ((self.short_voltage_3v3 * 4) * 0.001)
            return self._m_v33 if hasattr(self, '_m_v33') else None

        @property
        def cu5(self):
            if hasattr(self, '_m_cu5'):
                return self._m_cu5 if hasattr(self, '_m_cu5') else None

            self._m_cu5 = ((self.short_current_5v * 62) * 0.000001)
            return self._m_cu5 if hasattr(self, '_m_cu5') else None

        @property
        def v5(self):
            if hasattr(self, '_m_v5'):
                return self._m_v5 if hasattr(self, '_m_v5') else None

            self._m_v5 = ((self.short_voltage_5v * 4) * 0.001)
            return self._m_v5 if hasattr(self, '_m_v5') else None


    class PainaniBeaconLong(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id_magic = self._io.read_bytes(2)
            if not self.id_magic == b"\x3C\xC3":
                raise kaitaistruct.ValidationNotEqualError(b"\x3C\xC3", self.id_magic, self._io, u"/types/painani_beacon_long/seq/0")
            self.length = self._io.read_u1()
            self.antenna = self._io.read_u1()
            self.temp_panel_1 = self._io.read_s2be()
            self.temp_panel_2 = self._io.read_s2be()
            self.temp_panel_3 = self._io.read_s2be()
            self.temp_bank_1 = self._io.read_s2be()
            self.temp_bank_2 = self._io.read_s2be()
            self.charge_bank_1 = self._io.read_s2be()
            self.charge_bank_2 = self._io.read_s2be()
            self.gyro_x = self._io.read_s2be()
            self.gyro_y = self._io.read_s2be()
            self.gyro_z = self._io.read_s2be()
            self.state = self._io.read_u1()
            self.reboots = self._io.read_u2be()
            self.rtc_raw = [None] * (6)
            for i in range(6):
                self.rtc_raw[i] = self._io.read_u1()

            self.voltage_bank_1 = self._io.read_u2be()
            self.voltage_bank_2 = self._io.read_u2be()
            self.current_bank_1 = self._io.read_s2be()
            self.current_bank_2 = self._io.read_s2be()
            self.gps = self._io.read_u1()
            self.voltage_3v3 = self._io.read_u2be()
            self.battery_voltage = self._io.read_u2be()
            self.lna_voltage = self._io.read_u2be()
            self.voltage_5v = self._io.read_u2be()
            self.gps_voltage = self._io.read_u2be()
            self.camera_voltage = self._io.read_u2be()
            self.unparsed = self._io.read_bytes_full()

        @property
        def rtc(self):
            if hasattr(self, '_m_rtc'):
                return self._m_rtc if hasattr(self, '_m_rtc') else None

            self._m_rtc = ((((((self.rtc_raw[0] << 40) | (self.rtc_raw[1] << 32)) | (self.rtc_raw[2] << 24)) | (self.rtc_raw[3] << 16)) | (self.rtc_raw[4] << 8)) | self.rtc_raw[5])
            return self._m_rtc if hasattr(self, '_m_rtc') else None


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


    class PainaniPayloadIdentify(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.framelength
            if _on == 30:
                self.pld_id = Painani.PainaniBeaconShort(self._io, self, self._root)
            elif _on == 72:
                self.pld_id = Painani.PainaniBeaconLong(self._io, self, self._root)


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Painani.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Painani.SsidMask(self._io, self, self._root)


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
                _ = Painani.Repeaters(self._io, self, self._root)
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
            self.callsign_ror = Painani.Callsign(_io__raw_callsign_ror, self, self._root)


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


