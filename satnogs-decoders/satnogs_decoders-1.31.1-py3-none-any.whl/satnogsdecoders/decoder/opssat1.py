# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Opssat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field priority: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.priority
    :field source: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.source
    :field destination: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.destination
    :field destination_port: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.destination_port
    :field source_port: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.source_port
    :field reserved: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.reserved
    :field csp_hmac: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.hmac
    :field csp_xtea: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.xtea
    :field csp_rdp: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.rdp
    :field csp_crc: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.header.crc
    :field board_temperature: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.board_temperature
    :field pa_temperature: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.pa_temperature
    :field last_received_rssi: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.last_received_rssi
    :field last_received_rf_error: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.last_received_rf_error
    :field number_of_tx_packets_since_reboot: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.number_of_tx_packets_since_reboot
    :field number_of_rx_packets_since_reboot: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.number_of_rx_packets_since_reboot
    :field number_of_tx_bytes_since_reboot: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.number_of_tx_bytes_since_reboot
    :field number_of_rx_bytes_since_reboot: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.number_of_rx_bytes_since_reboot
    :field active_system_configuration: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.active_system_configuration
    :field reboot_number: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.reboot_number
    :field reboot_cause: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.reboot_cause
    :field last_valid_packet_timestamp: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.last_valid_packet_timestamp
    :field background_rssi_level: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.background_rssi_level
    :field tx_duty_time_since_reboot: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.tx_duty_time_since_reboot
    :field total_tx_packets: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.total_tx_packets
    :field total_rx_packets: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.total_rx_packets
    :field total_tx_bytes: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.total_tx_bytes
    :field total_rx_bytes: ax25_frame.payload.info.pld_id.payload_dscrm.opssat_payload.beacon_data.total_rx_bytes
    
    .. seealso::
       Source - https://github.com/esa/gr-opssat/blob/master/docs/os-uhf-specs.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Opssat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Opssat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 3:
                self.payload = Opssat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Opssat1.UiFrame(self._io, self, self._root)


    class CspBeaconData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.board_temperature = self._io.read_s2be()
            self.pa_temperature = self._io.read_s2be()
            self.last_received_rssi = self._io.read_s2be()
            self.last_received_rf_error = self._io.read_s2be()
            self.number_of_tx_packets_since_reboot = self._io.read_u4be()
            self.number_of_rx_packets_since_reboot = self._io.read_u4be()
            self.number_of_tx_bytes_since_reboot = self._io.read_u4be()
            self.number_of_rx_bytes_since_reboot = self._io.read_u4be()
            self.active_system_configuration = self._io.read_u1()
            self.reboot_number = self._io.read_u2be()
            self.reboot_cause = self._io.read_u4be()
            self.last_valid_packet_timestamp = self._io.read_u4be()
            self.background_rssi_level = self._io.read_s2be()
            self.tx_duty_time_since_reboot = self._io.read_u1()
            self.total_tx_packets = self._io.read_u4be()
            self.total_rx_packets = self._io.read_u4be()
            self.total_tx_bytes = self._io.read_u4be()
            self.total_rx_bytes = self._io.read_u4be()


    class CspHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.id_magic
            if _on == 12625866:
                self.raw_csp_header = self._io.read_u4le()
            else:
                self.raw_csp_header = self._io.read_u4be()

        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source if hasattr(self, '_m_source') else None

            self._m_source = ((self.raw_csp_header >> 25) & 31)
            return self._m_source if hasattr(self, '_m_source') else None

        @property
        def source_port(self):
            if hasattr(self, '_m_source_port'):
                return self._m_source_port if hasattr(self, '_m_source_port') else None

            self._m_source_port = ((self.raw_csp_header >> 8) & 63)
            return self._m_source_port if hasattr(self, '_m_source_port') else None

        @property
        def destination_port(self):
            if hasattr(self, '_m_destination_port'):
                return self._m_destination_port if hasattr(self, '_m_destination_port') else None

            self._m_destination_port = ((self.raw_csp_header >> 14) & 63)
            return self._m_destination_port if hasattr(self, '_m_destination_port') else None

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp if hasattr(self, '_m_rdp') else None

            self._m_rdp = ((self.raw_csp_header & 2) >> 1)
            return self._m_rdp if hasattr(self, '_m_rdp') else None

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination if hasattr(self, '_m_destination') else None

            self._m_destination = ((self.raw_csp_header >> 20) & 31)
            return self._m_destination if hasattr(self, '_m_destination') else None

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority if hasattr(self, '_m_priority') else None

            self._m_priority = (self.raw_csp_header >> 30)
            return self._m_priority if hasattr(self, '_m_priority') else None

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved if hasattr(self, '_m_reserved') else None

            self._m_reserved = ((self.raw_csp_header >> 4) & 15)
            return self._m_reserved if hasattr(self, '_m_reserved') else None

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea if hasattr(self, '_m_xtea') else None

            self._m_xtea = ((self.raw_csp_header & 4) >> 2)
            return self._m_xtea if hasattr(self, '_m_xtea') else None

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac if hasattr(self, '_m_hmac') else None

            self._m_hmac = ((self.raw_csp_header & 8) >> 3)
            return self._m_hmac if hasattr(self, '_m_hmac') else None

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc if hasattr(self, '_m_crc') else None

            self._m_crc = (self.raw_csp_header & 1)
            return self._m_crc if hasattr(self, '_m_crc') else None


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Opssat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Opssat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Opssat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Opssat1.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Opssat1.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class OpssatPayloadPreprocessed(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_payload_dscrm = self._io.read_bytes_full()
            _io__raw_payload_dscrm = KaitaiStream(BytesIO(self._raw_payload_dscrm))
            self.payload_dscrm = Opssat1.OpssatPayload(_io__raw_payload_dscrm, self, self._root)

        @property
        def payload_size(self):
            if hasattr(self, '_m_payload_size'):
                return self._m_payload_size if hasattr(self, '_m_payload_size') else None

            self._m_payload_size = self._io.size()
            return self._m_payload_size if hasattr(self, '_m_payload_size') else None


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._parent.ax25_header.src_callsign_raw.callsign_ror.callsign
            if _on == u"DP0OPS":
                self.info = Opssat1.OpssatPayloadIdentify(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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
            self.rpt_callsign_raw = Opssat1.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Opssat1.SsidMask(self._io, self, self._root)


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
                _ = Opssat1.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class OpssatPayloadIdentify(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.id_magic
            if _on == 904908480:
                self.pld_id = Opssat1.OpssatPayloadDscrm(self._io, self, self._root)
            elif _on == 12625866:
                self.pld_id = Opssat1.OpssatPayloadPreprocessed(self._io, self, self._root)
            elif _on == 3399991296:
                self.pld_id = Opssat1.OpssatPayloadPreprocessed(self._io, self, self._root)


    class CubeSatProtocol(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Opssat1.CspHeader(self._io, self, self._root)
            if  ((self.header.destination == 10) and (self.header.priority == 3) and (self.header.source == 5) and (self.header.destination_port == 31)) :
                self.beacon_data = Opssat1.CspBeaconData(self._io, self, self._root)



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
            self.callsign_ror = Opssat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class OpssatPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.opssat_payload = Opssat1.CubeSatProtocol(self._io, self, self._root)


    class OpssatPayloadDscrm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_payload_dscrm = self._io.read_bytes_full()
            _process = satnogsdecoders.process.Scrambler(169, 255, 7)
            self._raw_payload_dscrm = _process.decode(self._raw__raw_payload_dscrm)
            _io__raw_payload_dscrm = KaitaiStream(BytesIO(self._raw_payload_dscrm))
            self.payload_dscrm = Opssat1.OpssatPayload(_io__raw_payload_dscrm, self, self._root)

        @property
        def payload_size(self):
            if hasattr(self, '_m_payload_size'):
                return self._m_payload_size if hasattr(self, '_m_payload_size') else None

            self._m_payload_size = self._io.size()
            return self._m_payload_size if hasattr(self, '_m_payload_size') else None


    @property
    def id_magic(self):
        if hasattr(self, '_m_id_magic'):
            return self._m_id_magic if hasattr(self, '_m_id_magic') else None

        _pos = self._io.pos()
        self._io.seek(16)
        self._m_id_magic = self._io.read_u4be()
        self._io.seek(_pos)
        return self._m_id_magic if hasattr(self, '_m_id_magic') else None


