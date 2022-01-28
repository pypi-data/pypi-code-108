# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Gaspacs(KaitaiStruct):
    """:field dest_callsign: frame.payload.data_payload.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: frame.payload.data_payload.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: frame.payload.data_payload.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: frame.payload.data_payload.ax25_header.dest_ssid_raw.ssid
    :field ctl: frame.payload.data_payload.ax25_header.ctl
    :field pid: frame.payload.data_payload.payload.pid
    :field rf_message: frame.payload.data_payload.payload.ax25_info.rf_message
    :field length: frame.length
    :field packet_type: packet_type
    :field timestamp: frame.payload.data_payload.timestamp
    :field ss_1: frame.payload.data_payload.ss_1
    :field ss_2: frame.payload.data_payload.ss_2
    :field ss_3: frame.payload.data_payload.ss_3
    :field ss_4: frame.payload.data_payload.ss_4
    :field ss_5: frame.payload.data_payload.ss_5
    :field mf_x: frame.payload.data_payload.mf_x
    :field mf_y: frame.payload.data_payload.mf_y
    :field mf_z: frame.payload.data_payload.mf_z
    :field mission_mode: frame.payload.data_payload.mission_mode
    :field reboot_count: frame.payload.data_payload.reboot_count
    :field boombox_uv: frame.payload.data_payload.boombox_uv
    :field spx_pos_temp1: frame.payload.data_payload.spx_pos_temp1
    :field spx_pos_temp2: frame.payload.data_payload.spx_pos_temp2
    :field raspberrypi_temp: frame.payload.data_payload.raspberrypi_temp
    :field eps_mcu_temp: frame.payload.data_payload.eps_mcu_temp
    :field cell_1_battery_temp: frame.payload.data_payload.cell_1_battery_temp
    :field cell_2_battery_temp: frame.payload.data_payload.cell_2_battery_temp
    :field battery_voltage: frame.payload.data_payload.battery_voltage
    :field battery_current: frame.payload.data_payload.battery_current
    :field bcr_voltage: frame.payload.data_payload.bcr_voltage
    :field bcr_current: frame.payload.data_payload.bcr_current
    :field eps_3v3_current: frame.payload.data_payload.eps_3v3_current
    :field eps_5v_current: frame.payload.data_payload.eps_5v_current
    :field spx_voltage: frame.payload.data_payload.spx_voltage
    :field spx_pos_current: frame.payload.data_payload.spx_pos_current
    :field spx_neg_current: frame.payload.data_payload.spx_neg_current
    :field spy_voltage: frame.payload.data_payload.spy_voltage
    :field spy_pos_current: frame.payload.data_payload.spy_pos_current
    :field spy_neg_current: frame.payload.data_payload.spy_neg_current
    :field spz_voltage: frame.payload.data_payload.spz_voltage
    :field spz_pos_current: frame.payload.data_payload.spz_pos_current
    :field timestamp_ms: frame.payload.data_payload.timestamp_ms
    :field la_x: frame.payload.data_payload.la_x
    :field la_y: frame.payload.data_payload.la_y
    :field la_z: frame.payload.data_payload.la_z
    :field image_row: frame.payload.image_payload.ssdv_payload.image_row
    :field payload_size: frame.payload.payload_size
    :field framelength: framelength
    :field data_type: data_type
    
    .. seealso::
       Source - https://smallsatgasteam.github.io/GASPACS-Comms-Info/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.frame = Gaspacs.GaspacsFrameT(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Gaspacs.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Gaspacs.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Gaspacs.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Gaspacs.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Gaspacs.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Gaspacs.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Gaspacs.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Gaspacs.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Gaspacs.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Gaspacs.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Gaspacs.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Gaspacs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"N7GAS ") or (self.callsign == u"CQ    ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class ImageT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.image_row = (self._io.read_bytes_full()).decode(u"ASCII")


    class DeploymentT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_bytes(7)
            if not self.header == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.header, self._io, u"/types/deployment_t/seq/0")
            self.packet_type = self._io.read_u1()
            self.timestamp_ms = self._io.read_u8be()
            self.boombox_uv = self._io.read_f4be()
            self.la_x = self._io.read_f4be()
            self.la_y = self._io.read_f4be()
            self.la_z = self._io.read_f4be()
            self.footer = self._io.read_bytes(7)
            if not self.footer == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.footer, self._io, u"/types/deployment_t/seq/7")


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
            self.ax25_info = Gaspacs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class AttitudeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_bytes(7)
            if not self.header == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.header, self._io, u"/types/attitude_t/seq/0")
            self.packet_type = self._io.read_u1()
            self.timestamp = self._io.read_u4be()
            self.ss_1 = self._io.read_f4be()
            self.ss_2 = self._io.read_f4be()
            self.ss_3 = self._io.read_f4be()
            self.ss_4 = self._io.read_f4be()
            self.ss_5 = self._io.read_f4be()
            self.mf_x = self._io.read_f4be()
            self.mf_y = self._io.read_f4be()
            self.mf_z = self._io.read_f4be()
            self.footer = self._io.read_bytes(7)
            if not self.footer == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.footer, self._io, u"/types/attitude_t/seq/11")


    class SsdvT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_ssdv_payload = self._io.read_bytes_full()
            _process = satnogsdecoders.process.Hexl()
            self._raw_ssdv_payload = _process.decode(self._raw__raw_ssdv_payload)
            _io__raw_ssdv_payload = KaitaiStream(BytesIO(self._raw_ssdv_payload))
            self.ssdv_payload = Gaspacs.ImageT(_io__raw_ssdv_payload, self, self._root)


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
            self.callsign_ror = Gaspacs.Callsign(_io__raw_callsign_ror, self, self._root)


    class TelemetryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if ((self._root.data_type & 65280) >> 8) == 71:
                _on = self._root.packet_type
                if _on == 0:
                    self.data_payload = Gaspacs.AttitudeT(self._io, self, self._root)
                elif _on == 1:
                    self.data_payload = Gaspacs.TtcT(self._io, self, self._root)
                elif _on == 2:
                    self.data_payload = Gaspacs.DeploymentT(self._io, self, self._root)
                else:
                    self.data_payload = Gaspacs.Ax25Frame(self._io, self, self._root)

            if self._root.data_type == 21862:
                self.image_payload = Gaspacs.SsdvT(self._io, self, self._root)


        @property
        def payload_size(self):
            if hasattr(self, '_m_payload_size'):
                return self._m_payload_size if hasattr(self, '_m_payload_size') else None

            self._m_payload_size = self._io.size()
            return self._m_payload_size if hasattr(self, '_m_payload_size') else None


    class TtcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_bytes(7)
            if not self.header == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.header, self._io, u"/types/ttc_t/seq/0")
            self.packet_type = self._io.read_u1()
            self.timestamp = self._io.read_u4be()
            self.mission_mode = self._io.read_u1()
            self.reboot_count = self._io.read_u2be()
            self.boombox_uv = self._io.read_f4be()
            self.spx_pos_temp1 = self._io.read_f4be()
            self.spx_pos_temp2 = self._io.read_f4be()
            self.raspberrypi_temp = self._io.read_f4be()
            self.eps_mcu_temp = self._io.read_f4be()
            self.cell_1_battery_temp = self._io.read_f4be()
            self.cell_2_battery_temp = self._io.read_f4be()
            self.battery_voltage = self._io.read_f4be()
            self.battery_current = self._io.read_f4be()
            self.bcr_voltage = self._io.read_f4be()
            self.bcr_current = self._io.read_f4be()
            self.eps_3v3_current = self._io.read_f4be()
            self.eps_5v_current = self._io.read_f4be()
            self.spx_voltage = self._io.read_f4be()
            self.spx_pos_current = self._io.read_f4be()
            self.spx_neg_current = self._io.read_f4be()
            self.spy_voltage = self._io.read_f4be()
            self.spy_pos_current = self._io.read_f4be()
            self.spy_neg_current = self._io.read_f4be()
            self.spz_voltage = self._io.read_f4be()
            self.spz_pos_current = self._io.read_f4be()
            self.footer = self._io.read_bytes(7)
            if not self.footer == b"\x47\x41\x53\x50\x41\x43\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x41\x53\x50\x41\x43\x53", self.footer, self._io, u"/types/ttc_t/seq/26")


    class GaspacsFrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = self._io.read_u1()
            self.payload = Gaspacs.TelemetryT(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rf_message = (self._io.read_bytes_full()).decode(u"ASCII")


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None

    @property
    def packet_type(self):
        if hasattr(self, '_m_packet_type'):
            return self._m_packet_type if hasattr(self, '_m_packet_type') else None

        _pos = self._io.pos()
        self._io.seek(8)
        self._m_packet_type = self._io.read_u1()
        self._io.seek(_pos)
        return self._m_packet_type if hasattr(self, '_m_packet_type') else None

    @property
    def data_type(self):
        if hasattr(self, '_m_data_type'):
            return self._m_data_type if hasattr(self, '_m_data_type') else None

        _pos = self._io.pos()
        self._io.seek(1)
        self._m_data_type = self._io.read_u2be()
        self._io.seek(_pos)
        return self._m_data_type if hasattr(self, '_m_data_type') else None


