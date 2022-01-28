# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Spoc(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field obc_curr_boot_image: ax25_frame.payload.ax25_info.obc_curr_boot_image
    :field mmm_mode: ax25_frame.payload.ax25_info.mmm_mode
    :field obt_uptime: ax25_frame.payload.ax25_info.obt_uptime
    :field bat_battery_current_dir: ax25_frame.payload.ax25_info.bat_battery_current_dir
    :field bat_battery_current_0: ax25_frame.payload.ax25_info.bat_battery_current_0
    :field bat_battery_current_1: ax25_frame.payload.ax25_info.bat_battery_current_1
    :field bat_battery_current_2: ax25_frame.payload.ax25_info.bat_battery_current_2
    :field bat_battery_voltage_0: ax25_frame.payload.ax25_info.bat_battery_voltage_0
    :field bat_battery_voltage_1: ax25_frame.payload.ax25_info.bat_battery_voltage_1
    :field bat_battery_voltage_2: ax25_frame.payload.ax25_info.bat_battery_voltage_2
    :field bat_battery_temperature_0: ax25_frame.payload.ax25_info.bat_battery_temperature_0
    :field bat_battery_temperature_1: ax25_frame.payload.ax25_info.bat_battery_temperature_1
    :field bat_battery_temperature_2: ax25_frame.payload.ax25_info.bat_battery_temperature_2
    :field bat_battery_temperature_3: ax25_frame.payload.ax25_info.bat_battery_temperature_3
    :field bat_battery_heater_status_0: ax25_frame.payload.ax25_info.bat_battery_heater_status_0
    :field bat_battery_heater_status_1: ax25_frame.payload.ax25_info.bat_battery_heater_status_1
    :field bat_battery_heater_status_2: ax25_frame.payload.ax25_info.bat_battery_heater_status_2
    :field bat_battery_heater_status_3: ax25_frame.payload.ax25_info.bat_battery_heater_status_3
    :field bat_status: ax25_frame.payload.ax25_info.bat_status
    :field bat_last_error: ax25_frame.payload.ax25_info.bat_last_error
    :field eps_status_0: ax25_frame.payload.ax25_info.eps_status_0
    :field eps_status_1: ax25_frame.payload.ax25_info.eps_status_1
    :field eps_last_error_0: ax25_frame.payload.ax25_info.eps_last_error_0
    :field eps_last_error_1: ax25_frame.payload.ax25_info.eps_last_error_1
    :field eps_switch_voltages_0: ax25_frame.payload.ax25_info.eps_switch_voltages_0
    :field eps_switch_voltages_1: ax25_frame.payload.ax25_info.eps_switch_voltages_1
    :field eps_switch_voltages_2: ax25_frame.payload.ax25_info.eps_switch_voltages_2
    :field eps_switch_voltages_3: ax25_frame.payload.ax25_info.eps_switch_voltages_3
    :field eps_switch_voltages_4: ax25_frame.payload.ax25_info.eps_switch_voltages_4
    :field eps_switch_voltages_5: ax25_frame.payload.ax25_info.eps_switch_voltages_5
    :field eps_switch_voltages_6: ax25_frame.payload.ax25_info.eps_switch_voltages_6
    :field eps_switch_voltages_7: ax25_frame.payload.ax25_info.eps_switch_voltages_7
    :field eps_switch_voltages_8: ax25_frame.payload.ax25_info.eps_switch_voltages_8
    :field eps_switch_voltages_9: ax25_frame.payload.ax25_info.eps_switch_voltages_9
    :field eps_switch_currents_0: ax25_frame.payload.ax25_info.eps_switch_currents_0
    :field eps_switch_currents_1: ax25_frame.payload.ax25_info.eps_switch_currents_1
    :field eps_switch_currents_2: ax25_frame.payload.ax25_info.eps_switch_currents_2
    :field eps_switch_currents_3: ax25_frame.payload.ax25_info.eps_switch_currents_3
    :field eps_switch_currents_4: ax25_frame.payload.ax25_info.eps_switch_currents_4
    :field eps_switch_currents_5: ax25_frame.payload.ax25_info.eps_switch_currents_5
    :field eps_switch_currents_6: ax25_frame.payload.ax25_info.eps_switch_currents_6
    :field eps_switch_currents_7: ax25_frame.payload.ax25_info.eps_switch_currents_7
    :field eps_switch_currents_8: ax25_frame.payload.ax25_info.eps_switch_currents_8
    :field eps_switch_currents_9: ax25_frame.payload.ax25_info.eps_switch_currents_9
    :field eps_expected_switch_states_bitmap: ax25_frame.payload.ax25_info.eps_expected_switch_states_bitmap
    :field eps_board_temperatures_0: ax25_frame.payload.ax25_info.eps_board_temperatures_0
    :field eps_board_temperatures_1: ax25_frame.payload.ax25_info.eps_board_temperatures_1
    :field eps_bus_voltages_0: ax25_frame.payload.ax25_info.eps_bus_voltages_0
    :field eps_bus_voltages_1: ax25_frame.payload.ax25_info.eps_bus_voltages_1
    :field eps_bus_voltages_2: ax25_frame.payload.ax25_info.eps_bus_voltages_2
    :field eps_bus_voltages_3: ax25_frame.payload.ax25_info.eps_bus_voltages_3
    :field eps_bus_currents_0: ax25_frame.payload.ax25_info.eps_bus_currents_0
    :field eps_bus_currents_1: ax25_frame.payload.ax25_info.eps_bus_currents_1
    :field eps_bus_currents_2: ax25_frame.payload.ax25_info.eps_bus_currents_2
    :field eps_bus_currents_3: ax25_frame.payload.ax25_info.eps_bus_currents_3
    :field cmc_rx_lock: ax25_frame.payload.ax25_info.cmc_rx_lock
    :field cmc_rx_frame_count: ax25_frame.payload.ax25_info.cmc_rx_frame_count
    :field cmc_rx_packet_count: ax25_frame.payload.ax25_info.cmc_rx_packet_count
    :field cmc_rx_dropped_error_count: ax25_frame.payload.ax25_info.cmc_rx_dropped_error_count
    :field cmc_rx_crc_error_count: ax25_frame.payload.ax25_info.cmc_rx_crc_error_count
    :field cmc_rx_overrun_error_count: ax25_frame.payload.ax25_info.cmc_rx_overrun_error_count
    :field cmc_rx_protocol_error_count: ax25_frame.payload.ax25_info.cmc_rx_protocol_error_count
    :field cmc_temperature_smps: ax25_frame.payload.ax25_info.cmc_temperature_smps
    :field cmc_temperature_pa: ax25_frame.payload.ax25_info.cmc_temperature_pa
    
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
        self.ax25_frame = Spoc.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Spoc.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Spoc.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Spoc.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Spoc.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Spoc.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Spoc.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Spoc.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Spoc.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Spoc.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Spoc.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Spoc.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Spoc.Repeater(self._io, self, self._root)

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
            if _on == u"SPOC  ":
                self.ax25_info = Spoc.SpocTlm(self._io, self, self._root)
            elif _on == u"MOCI  ":
                self.ax25_info = Spoc.SpocTlm(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class SpocTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_bytes(23)
            self.obc_curr_boot_image = self._io.read_bits_int_be(8)
            self.mmm_mode = self._io.read_bits_int_be(3)
            self.obt_uptime = self._io.read_bits_int_be(32)
            self.bat_battery_current_dir = self._io.read_bits_int_be(1) != 0
            self.bat_battery_current_0 = self._io.read_bits_int_be(10)
            self.bat_battery_current_1 = self._io.read_bits_int_be(10)
            self.bat_battery_current_2 = self._io.read_bits_int_be(10)
            self.bat_battery_voltage_0 = self._io.read_bits_int_be(10)
            self.bat_battery_voltage_1 = self._io.read_bits_int_be(10)
            self.bat_battery_voltage_2 = self._io.read_bits_int_be(10)
            self.bat_battery_temperature_0 = self._io.read_bits_int_be(10)
            self.bat_battery_temperature_1 = self._io.read_bits_int_be(10)
            self.bat_battery_temperature_2 = self._io.read_bits_int_be(10)
            self.bat_battery_temperature_3 = self._io.read_bits_int_be(10)
            self.bat_battery_heater_status_0 = self._io.read_bits_int_be(10)
            self.bat_battery_heater_status_1 = self._io.read_bits_int_be(10)
            self.bat_battery_heater_status_2 = self._io.read_bits_int_be(10)
            self.bat_battery_heater_status_3 = self._io.read_bits_int_be(10)
            self.bat_status = self._io.read_bits_int_be(16)
            self.bat_last_error = self._io.read_bits_int_be(8)
            self.eps_status_0 = self._io.read_bits_int_be(16)
            self.eps_status_1 = self._io.read_bits_int_be(16)
            self.eps_last_error_0 = self._io.read_bits_int_be(16)
            self.eps_last_error_1 = self._io.read_bits_int_be(16)
            self.eps_switch_voltages_0 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_1 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_2 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_3 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_4 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_5 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_6 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_7 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_8 = self._io.read_bits_int_be(10)
            self.eps_switch_voltages_9 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_0 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_1 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_2 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_3 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_4 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_5 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_6 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_7 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_8 = self._io.read_bits_int_be(10)
            self.eps_switch_currents_9 = self._io.read_bits_int_be(10)
            self.eps_expected_switch_states_bitmap = self._io.read_bits_int_be(10)
            self.eps_board_temperatures_0 = self._io.read_bits_int_be(10)
            self.eps_board_temperatures_1 = self._io.read_bits_int_be(10)
            self.eps_bus_voltages_0 = self._io.read_bits_int_be(10)
            self.eps_bus_voltages_1 = self._io.read_bits_int_be(10)
            self.eps_bus_voltages_2 = self._io.read_bits_int_be(10)
            self.eps_bus_voltages_3 = self._io.read_bits_int_be(10)
            self.eps_bus_currents_0 = self._io.read_bits_int_be(10)
            self.eps_bus_currents_1 = self._io.read_bits_int_be(10)
            self.eps_bus_currents_2 = self._io.read_bits_int_be(10)
            self.eps_bus_currents_3 = self._io.read_bits_int_be(10)
            self.cmc_rx_lock = self._io.read_bits_int_be(1) != 0
            self.cmc_rx_frame_count = self._io.read_bits_int_be(16)
            self.cmc_rx_packet_count = self._io.read_bits_int_be(16)
            self.cmc_rx_dropped_error_count = self._io.read_bits_int_be(16)
            self.cmc_rx_crc_error_count = self._io.read_bits_int_be(16)
            self.cmc_rx_overrun_error_count = self._io.read_bits_int_be(8)
            self.cmc_rx_protocol_error_count = self._io.read_bits_int_be(16)
            self._io.align_to_byte()
            self.cmc_temperature_smps = self._io.read_s1()
            self.cmc_temperature_pa = self._io.read_s1()


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
            self.rpt_callsign_raw = Spoc.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Spoc.SsidMask(self._io, self, self._root)


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
                _ = Spoc.Repeaters(self._io, self, self._root)
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
            self.callsign_ror = Spoc.Callsign(_io__raw_callsign_ror, self, self._root)



