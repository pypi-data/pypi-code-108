# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Asuphoenix(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field priority: ax25_frame.payload.ax25_info.csp_header.priority
    :field source: ax25_frame.payload.ax25_info.csp_header.source
    :field destination: ax25_frame.payload.ax25_info.csp_header.destination
    :field destination_port: ax25_frame.payload.ax25_info.csp_header.destination_port
    :field source_port: ax25_frame.payload.ax25_info.csp_header.source_port
    :field reserved: ax25_frame.payload.ax25_info.csp_header.reserved
    :field hmac: ax25_frame.payload.ax25_info.csp_header.hmac
    :field xtea: ax25_frame.payload.ax25_info.csp_header.xtea
    :field rdp: ax25_frame.payload.ax25_info.csp_header.rdp
    :field crc: ax25_frame.payload.ax25_info.csp_header.crc
    :field comms_idx_int: ax25_frame.payload.ax25_info.csp_node.csp_node_port.comms_idx_int
    :field total_obc_resets: ax25_frame.payload.ax25_info.csp_node.csp_node_port.total_obc_resets
    :field current_bat_volt_flt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.current_bat_volt_flt
    :field obc_clock: ax25_frame.payload.ax25_info.csp_node.csp_node_port.obc_clock
    :field current_3v3_flt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.current_3v3_flt
    :field current_5v_flt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.current_5v_flt
    :field current_adcs_flt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.current_adcs_flt
    :field eps_charge_volt_bat_flt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps_charge_volt_bat_flt
    :field eps_charge_current_bat: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps_charge_current_bat
    :field eps_temp: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps_temp
    :field bat_temp: ax25_frame.payload.ax25_info.csp_node.csp_node_port.bat_temp
    :field brownouts: ax25_frame.payload.ax25_info.csp_node.csp_node_port.brownouts
    :field ax100_rssi: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ax100_rssi
    :field ax100_board_temp: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ax100_board_temp
    :field gps_sats_used: ax25_frame.payload.ax25_info.csp_node.csp_node_port.gps_sats_used
    :field ants_deployed: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ants_deployed
    :field gpio_state: ax25_frame.payload.ax25_info.csp_node.csp_node_port.gpio_state
    :field temp_brd: ax25_frame.payload.ax25_info.csp_node.csp_node_port.temp_brd
    :field temp_pa: ax25_frame.payload.ax25_info.csp_node.csp_node_port.temp_pa
    :field last_rssi: ax25_frame.payload.ax25_info.csp_node.csp_node_port.last_rssi
    :field last_rferr: ax25_frame.payload.ax25_info.csp_node.csp_node_port.last_rferr
    :field tx_count: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tx_count
    :field rx_count: ax25_frame.payload.ax25_info.csp_node.csp_node_port.rx_count
    :field tx_bytes: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tx_bytes
    :field rx_bytes: ax25_frame.payload.ax25_info.csp_node.csp_node_port.rx_bytes
    :field active_conf: ax25_frame.payload.ax25_info.csp_node.csp_node_port.active_conf
    :field boot_count: ax25_frame.payload.ax25_info.csp_node.csp_node_port.boot_count
    :field boot_cause: ax25_frame.payload.ax25_info.csp_node.csp_node_port.boot_cause
    :field last_contact: ax25_frame.payload.ax25_info.csp_node.csp_node_port.last_contact
    :field bgnd_rssi: ax25_frame.payload.ax25_info.csp_node.csp_node_port.bgnd_rssi
    :field tx_duty: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tx_duty
    :field tot_tx_count: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tot_tx_count
    :field tot_rx_count: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tot_rx_count
    :field tot_tx_bytes: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tot_tx_bytes
    :field tot_rx_bytes: ax25_frame.payload.ax25_info.csp_node.csp_node_port.tot_rx_bytes
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Asuphoenix.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Asuphoenix.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Asuphoenix.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Asuphoenix.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Asuphoenix.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Asuphoenix.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Asuphoenix.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Asuphoenix.IFrame(self._io, self, self._root)


    class ObcHkT(KaitaiStruct):
        """
        .. seealso::
           Source - http://phxcubesat.asu.edu/content/amateur-operations
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_type_magic = self._io.read_bytes(3)
            if not self.beacon_type_magic == b"\x68\x6B\x3A":
                raise kaitaistruct.ValidationNotEqualError(b"\x68\x6B\x3A", self.beacon_type_magic, self._io, u"/types/obc_hk_t/seq/0")
            self.int_comms_idx_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.total_obc_resets_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.current_bat_volt_int_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.current_bat_volt_frac_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.obc_disk_space_used_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.obc_clock_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.current_3v3_int_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.current_3v3_frac_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.current_5v_int_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.current_5v_frac_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.current_adcs_int_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.current_adcs_frac_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.eps_charge_volt_bat_int_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.eps_charge_volt_bat_frac_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.eps_charge_current_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.eps_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.bat_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.brownouts_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.ax100_rssi_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.ax100_board_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.gps_sats_used_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.ants_deployed_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.gpio_state_str = (self._io.read_bytes(1)).decode(u"utf-8")

        @property
        def obc_clock(self):
            if hasattr(self, '_m_obc_clock'):
                return self._m_obc_clock if hasattr(self, '_m_obc_clock') else None

            self._m_obc_clock = int(self.obc_clock_str)
            return self._m_obc_clock if hasattr(self, '_m_obc_clock') else None

        @property
        def ax100_board_temp(self):
            if hasattr(self, '_m_ax100_board_temp'):
                return self._m_ax100_board_temp if hasattr(self, '_m_ax100_board_temp') else None

            self._m_ax100_board_temp = int(self.ax100_board_temp_str)
            return self._m_ax100_board_temp if hasattr(self, '_m_ax100_board_temp') else None

        @property
        def total_obc_resets(self):
            if hasattr(self, '_m_total_obc_resets'):
                return self._m_total_obc_resets if hasattr(self, '_m_total_obc_resets') else None

            self._m_total_obc_resets = int(self.total_obc_resets_str)
            return self._m_total_obc_resets if hasattr(self, '_m_total_obc_resets') else None

        @property
        def gps_sats_used(self):
            if hasattr(self, '_m_gps_sats_used'):
                return self._m_gps_sats_used if hasattr(self, '_m_gps_sats_used') else None

            self._m_gps_sats_used = int(self.gps_sats_used_str)
            return self._m_gps_sats_used if hasattr(self, '_m_gps_sats_used') else None

        @property
        def ax100_rssi(self):
            if hasattr(self, '_m_ax100_rssi'):
                return self._m_ax100_rssi if hasattr(self, '_m_ax100_rssi') else None

            self._m_ax100_rssi = int(self.ax100_rssi_str)
            return self._m_ax100_rssi if hasattr(self, '_m_ax100_rssi') else None

        @property
        def current_5v_flt(self):
            if hasattr(self, '_m_current_5v_flt'):
                return self._m_current_5v_flt if hasattr(self, '_m_current_5v_flt') else None

            self._m_current_5v_flt = (int(self.current_5v_int_str) + ((((int(int(self.current_5v_int_str) < 0) * -2) + 1) * int(self.current_5v_frac_str)) / 1000.0))
            return self._m_current_5v_flt if hasattr(self, '_m_current_5v_flt') else None

        @property
        def ants_deployed(self):
            if hasattr(self, '_m_ants_deployed'):
                return self._m_ants_deployed if hasattr(self, '_m_ants_deployed') else None

            self._m_ants_deployed = int(self.ants_deployed_str)
            return self._m_ants_deployed if hasattr(self, '_m_ants_deployed') else None

        @property
        def eps_temp(self):
            if hasattr(self, '_m_eps_temp'):
                return self._m_eps_temp if hasattr(self, '_m_eps_temp') else None

            self._m_eps_temp = int(self.eps_temp_str)
            return self._m_eps_temp if hasattr(self, '_m_eps_temp') else None

        @property
        def current_adcs_flt(self):
            if hasattr(self, '_m_current_adcs_flt'):
                return self._m_current_adcs_flt if hasattr(self, '_m_current_adcs_flt') else None

            self._m_current_adcs_flt = (int(self.current_adcs_int_str) + ((((int(int(self.current_adcs_int_str) < 0) * -2) + 1) * int(self.current_adcs_frac_str)) / 1000.0))
            return self._m_current_adcs_flt if hasattr(self, '_m_current_adcs_flt') else None

        @property
        def bat_temp(self):
            if hasattr(self, '_m_bat_temp'):
                return self._m_bat_temp if hasattr(self, '_m_bat_temp') else None

            self._m_bat_temp = int(self.bat_temp_str)
            return self._m_bat_temp if hasattr(self, '_m_bat_temp') else None

        @property
        def comms_idx_int(self):
            if hasattr(self, '_m_comms_idx_int'):
                return self._m_comms_idx_int if hasattr(self, '_m_comms_idx_int') else None

            self._m_comms_idx_int = int(self.int_comms_idx_str)
            return self._m_comms_idx_int if hasattr(self, '_m_comms_idx_int') else None

        @property
        def current_3v3_flt(self):
            if hasattr(self, '_m_current_3v3_flt'):
                return self._m_current_3v3_flt if hasattr(self, '_m_current_3v3_flt') else None

            self._m_current_3v3_flt = (int(self.current_3v3_int_str) + ((((int(int(self.current_3v3_int_str) < 0) * -2) + 1) * int(self.current_3v3_frac_str)) / 1000.0))
            return self._m_current_3v3_flt if hasattr(self, '_m_current_3v3_flt') else None

        @property
        def gpio_state(self):
            if hasattr(self, '_m_gpio_state'):
                return self._m_gpio_state if hasattr(self, '_m_gpio_state') else None

            self._m_gpio_state = int(self.gpio_state_str)
            return self._m_gpio_state if hasattr(self, '_m_gpio_state') else None

        @property
        def current_bat_volt_flt(self):
            if hasattr(self, '_m_current_bat_volt_flt'):
                return self._m_current_bat_volt_flt if hasattr(self, '_m_current_bat_volt_flt') else None

            self._m_current_bat_volt_flt = (int(self.current_bat_volt_int_str) + ((((int(int(self.current_bat_volt_int_str) < 0) * -2) + 1) * int(self.current_bat_volt_frac_str)) / 100.0))
            return self._m_current_bat_volt_flt if hasattr(self, '_m_current_bat_volt_flt') else None

        @property
        def eps_charge_current_bat(self):
            if hasattr(self, '_m_eps_charge_current_bat'):
                return self._m_eps_charge_current_bat if hasattr(self, '_m_eps_charge_current_bat') else None

            self._m_eps_charge_current_bat = int(self.eps_charge_current_bat_str)
            return self._m_eps_charge_current_bat if hasattr(self, '_m_eps_charge_current_bat') else None

        @property
        def brownouts(self):
            if hasattr(self, '_m_brownouts'):
                return self._m_brownouts if hasattr(self, '_m_brownouts') else None

            self._m_brownouts = int(self.brownouts_str)
            return self._m_brownouts if hasattr(self, '_m_brownouts') else None

        @property
        def eps_charge_volt_bat_flt(self):
            if hasattr(self, '_m_eps_charge_volt_bat_flt'):
                return self._m_eps_charge_volt_bat_flt if hasattr(self, '_m_eps_charge_volt_bat_flt') else None

            self._m_eps_charge_volt_bat_flt = (int(self.eps_charge_volt_bat_int_str) + ((((int(int(self.eps_charge_volt_bat_int_str) < 0) * -2) + 1) * int(self.eps_charge_volt_bat_frac_str)) / 100.0))
            return self._m_eps_charge_volt_bat_flt if hasattr(self, '_m_eps_charge_volt_bat_flt') else None


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Asuphoenix.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Asuphoenix.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Asuphoenix.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Asuphoenix.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Asuphoenix.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Ax100ControlPortT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temp_brd = self._io.read_s2be()
            self.temp_pa = self._io.read_s2be()
            self.last_rssi = self._io.read_s2be()
            self.last_rferr = self._io.read_s2be()
            self.tx_count = self._io.read_u4be()
            self.rx_count = self._io.read_u4be()
            self.tx_bytes = self._io.read_u4be()
            self.rx_bytes = self._io.read_u4be()
            self.active_conf = self._io.read_u1()
            self.boot_count = self._io.read_u2be()
            self.boot_cause = self._io.read_u4be()
            self.last_contact = self._io.read_u4be()
            self.bgnd_rssi = self._io.read_s2be()
            self.tx_duty = self._io.read_u1()
            self.tot_tx_count = self._io.read_u4be()
            self.tot_rx_count = self._io.read_u4be()
            self.tot_tx_bytes = self._io.read_u4be()
            self.tot_rx_bytes = self._io.read_u4be()


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
            self.ax25_info = Asuphoenix.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
            self.rpt_callsign_raw = Asuphoenix.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Asuphoenix.SsidMask(self._io, self, self._root)


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
                _ = Asuphoenix.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
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


    class Ax100T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.csp_header.source_port
            if _on == 0:
                self.csp_node_port = Asuphoenix.Ax100ControlPortT(self._io, self, self._root)


    class ObcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.csp_header.source_port
            if _on == 27:
                self.csp_node_port = Asuphoenix.ObcHkT(self._io, self, self._root)


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (0), 1)
            _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = Asuphoenix.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = Asuphoenix.CspHeaderT(self._io, self, self._root)
            _on = self.csp_header.source
            if _on == 2:
                self.csp_node = Asuphoenix.ObcT(self._io, self, self._root)
            elif _on == 5:
                self.csp_node = Asuphoenix.Ax100T(self._io, self, self._root)



