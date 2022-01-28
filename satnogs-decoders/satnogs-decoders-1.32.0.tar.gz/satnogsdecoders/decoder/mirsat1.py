# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mirsat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_type: ax25_frame.payload.payload.beacon.beacon_header.packet_type
    :field apid: ax25_frame.payload.payload.beacon.beacon_header.apid
    :field sequence_count: ax25_frame.payload.payload.beacon.beacon_header.sequence_count
    :field length: ax25_frame.payload.payload.beacon.beacon_header.length
    :field service_type: ax25_frame.payload.payload.beacon.beacon_header.service_type
    :field sub_service_type: ax25_frame.payload.payload.beacon.beacon_header.sub_service_type
    :field obc_boot_image: ax25_frame.payload.payload.beacon.obc_boot_image
    :field on_board_time: ax25_frame.payload.payload.beacon.on_board_time
    :field uptime: ax25_frame.payload.payload.beacon.uptime
    :field spacecraft_mode: ax25_frame.payload.payload.beacon.spacecraft_mode
    :field seperation_sequence_state: ax25_frame.payload.payload.beacon.seperation_sequence_state
    :field solar_array_deployment_state_0: ax25_frame.payload.payload.beacon.solar_array_deployment_state_0
    :field solar_array_deployment_state_1: ax25_frame.payload.payload.beacon.solar_array_deployment_state_1
    :field solar_array_deployment_state_2: ax25_frame.payload.payload.beacon.solar_array_deployment_state_2
    :field solar_array_deployment_state_3: ax25_frame.payload.payload.beacon.solar_array_deployment_state_3
    :field antenna_deployment_state_0: ax25_frame.payload.payload.beacon.antenna_deployment_state_0
    :field antenna_deployment_state_1: ax25_frame.payload.payload.beacon.antenna_deployment_state_1
    :field antenna_deployment_state_2: ax25_frame.payload.payload.beacon.antenna_deployment_state_2
    :field antenna_deployment_state_3: ax25_frame.payload.payload.beacon.antenna_deployment_state_3
    :field antenna_deployment_state_4: ax25_frame.payload.payload.beacon.antenna_deployment_state_4
    :field antenna_deployment_state_5: ax25_frame.payload.payload.beacon.antenna_deployment_state_5
    :field antenna_deployment_state_6: ax25_frame.payload.payload.beacon.antenna_deployment_state_6
    :field antenna_deployment_state_7: ax25_frame.payload.payload.beacon.antenna_deployment_state_7
    :field adm_soft_fire_counter: ax25_frame.payload.payload.beacon.adm_soft_fire_counter
    :field adm_hard_fire_counter: ax25_frame.payload.payload.beacon.adm_hard_fire_counter
    :field sadm_check_counter: ax25_frame.payload.payload.beacon.sadm_check_counter
    :field i2c_nack_addr_count: ax25_frame.payload.payload.beacon.i2c_nack_addr_count
    :field i2c_hw_state_error_count: ax25_frame.payload.payload.beacon.i2c_hw_state_error_count
    :field i2c_isr_error_count: ax25_frame.payload.payload.beacon.i2c_isr_error_count
    :field battery_current_direction: ax25_frame.payload.payload.beacon.battery_current_direction
    :field battery_current_0: ax25_frame.payload.payload.beacon.battery_current_0
    :field battery_current_1_msb: ax25_frame.payload.payload.beacon.battery_current_1_msb
    :field adm_telemetry_0: ax25_frame.payload.payload.beacon.adm_telemetry_0
    :field adm_telemetry_1: ax25_frame.payload.payload.beacon.adm_telemetry_1
    :field adm_telemetry_2: ax25_frame.payload.payload.beacon.adm_telemetry_2
    :field adm_telemetry_3: ax25_frame.payload.payload.beacon.adm_telemetry_3
    :field adm_telemetry_4: ax25_frame.payload.payload.beacon.adm_telemetry_4
    :field adm_telemetry_5: ax25_frame.payload.payload.beacon.adm_telemetry_5
    :field adm_telemetry_6: ax25_frame.payload.payload.beacon.adm_telemetry_6
    :field adm_telemetry_7: ax25_frame.payload.payload.beacon.adm_telemetry_7
    :field adm_telemetry_8: ax25_frame.payload.payload.beacon.adm_telemetry_8
    :field adm_telemetry_9: ax25_frame.payload.payload.beacon.adm_telemetry_9
    :field sadm_telemetry_0: ax25_frame.payload.payload.beacon.sadm_telemetry_0
    :field sadm_telemetry_1: ax25_frame.payload.payload.beacon.sadm_telemetry_1
    :field sadm_telemetry_2: ax25_frame.payload.payload.beacon.sadm_telemetry_2
    :field sadm_telemetry_3: ax25_frame.payload.payload.beacon.sadm_telemetry_3
    :field sadm_telemetry_4: ax25_frame.payload.payload.beacon.sadm_telemetry_4
    :field sadm_telemetry_5: ax25_frame.payload.payload.beacon.sadm_telemetry_5
    :field sadm_telemetry_6: ax25_frame.payload.payload.beacon.sadm_telemetry_6
    :field sadm_telemetry_7: ax25_frame.payload.payload.beacon.sadm_telemetry_7
    :field sadm_telemetry_8: ax25_frame.payload.payload.beacon.sadm_telemetry_8
    :field sadm_telemetry_9: ax25_frame.payload.payload.beacon.sadm_telemetry_9
    :field battery_current_1_lsbs: ax25_frame.payload.payload.beacon.battery_current_1_lsbs
    :field battery_current_2: ax25_frame.payload.payload.beacon.battery_current_2
    :field battery_voltage_0: ax25_frame.payload.payload.beacon.battery_voltage_0
    :field battery_voltage_1: ax25_frame.payload.payload.beacon.battery_voltage_1
    :field battery_voltage_2: ax25_frame.payload.payload.beacon.battery_voltage_2
    :field battery_temperature: ax25_frame.payload.payload.beacon.battery_temperature
    :field solar_array_current_0: ax25_frame.payload.payload.beacon.solar_array_current_0
    :field solar_array_voltage_0: ax25_frame.payload.payload.beacon.solar_array_voltage_0
    :field solar_array_voltage_1: ax25_frame.payload.payload.beacon.solar_array_voltage_1
    :field solar_array_voltage_2: ax25_frame.payload.payload.beacon.solar_array_voltage_2
    :field solar_array_voltage_3: ax25_frame.payload.payload.beacon.solar_array_voltage_3
    :field solar_array_voltage_4: ax25_frame.payload.payload.beacon.solar_array_voltage_4
    :field solar_array_voltage_5: ax25_frame.payload.payload.beacon.solar_array_voltage_5
    :field solar_array_voltage_6: ax25_frame.payload.payload.beacon.solar_array_voltage_6
    :field solar_array_voltage_7: ax25_frame.payload.payload.beacon.solar_array_voltage_7
    :field solar_array_voltage_8: ax25_frame.payload.payload.beacon.solar_array_voltage_8
    :field eps_bus_voltage_0: ax25_frame.payload.payload.beacon.eps_bus_voltage_0
    :field eps_bus_voltage_1: ax25_frame.payload.payload.beacon.eps_bus_voltage_1
    :field eps_bus_voltage_2: ax25_frame.payload.payload.beacon.eps_bus_voltage_2
    :field eps_bus_voltage_3: ax25_frame.payload.payload.beacon.eps_bus_voltage_3
    :field eps_bus_current_0: ax25_frame.payload.payload.beacon.eps_bus_current_0
    :field eps_bus_current_1: ax25_frame.payload.payload.beacon.eps_bus_current_1
    :field eps_bus_current_2: ax25_frame.payload.payload.beacon.eps_bus_current_2
    :field eps_bus_current_3: ax25_frame.payload.payload.beacon.eps_bus_current_3
    :field adcs_raw_gyro_rate_0: ax25_frame.payload.payload.beacon.adcs_raw_gyro_rate_0
    :field adcs_raw_gyro_rate_1: ax25_frame.payload.payload.beacon.adcs_raw_gyro_rate_1
    :field adcs_raw_gyro_rate_2: ax25_frame.payload.payload.beacon.adcs_raw_gyro_rate_2
    :field adcs_mtq_direction_duty_0: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_0
    :field adcs_mtq_direction_duty_1: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_1
    :field adcs_mtq_direction_duty_2: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_2
    :field adcs_mtq_direction_duty_3: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_3
    :field adcs_mtq_direction_duty_4: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_4
    :field adcs_mtq_direction_duty_5: ax25_frame.payload.payload.beacon.adcs_mtq_direction_duty_5
    :field adcs_status: ax25_frame.payload.payload.beacon.adcs_status
    :field adcs_bus_voltage_0: ax25_frame.payload.payload.beacon.adcs_bus_voltage_0
    :field adcs_bus_voltage_1: ax25_frame.payload.payload.beacon.adcs_bus_voltage_1
    :field adcs_bus_voltage_2: ax25_frame.payload.payload.beacon.adcs_bus_voltage_2
    :field adcs_bus_current_0: ax25_frame.payload.payload.beacon.adcs_bus_current_0
    :field adcs_bus_current_1: ax25_frame.payload.payload.beacon.adcs_bus_current_1
    :field adcs_bus_current_2: ax25_frame.payload.payload.beacon.adcs_bus_current_2
    :field adcs_board_temperature: ax25_frame.payload.payload.beacon.adcs_board_temperature
    :field adcs_adc_reference: ax25_frame.payload.payload.beacon.adcs_adc_reference
    :field adcs_sensor_current: ax25_frame.payload.payload.beacon.adcs_sensor_current
    :field adcs_mtq_current: ax25_frame.payload.payload.beacon.adcs_mtq_current
    :field adcs_array_temperature_0: ax25_frame.payload.payload.beacon.adcs_array_temperature_0
    :field adcs_array_temperature_1: ax25_frame.payload.payload.beacon.adcs_array_temperature_1
    :field adcs_array_temperature_2: ax25_frame.payload.payload.beacon.adcs_array_temperature_2
    :field adcs_array_temperature_3: ax25_frame.payload.payload.beacon.adcs_array_temperature_3
    :field adcs_array_temperature_4: ax25_frame.payload.payload.beacon.adcs_array_temperature_4
    :field adcs_array_temperature_5: ax25_frame.payload.payload.beacon.adcs_array_temperature_5
    :field adcs_css_raw_0: ax25_frame.payload.payload.beacon.adcs_css_raw_0
    :field adcs_css_raw_1: ax25_frame.payload.payload.beacon.adcs_css_raw_1
    :field adcs_css_raw_2: ax25_frame.payload.payload.beacon.adcs_css_raw_2
    :field adcs_css_raw_3: ax25_frame.payload.payload.beacon.adcs_css_raw_3
    :field adcs_css_raw_4: ax25_frame.payload.payload.beacon.adcs_css_raw_4
    :field adcs_css_raw_5: ax25_frame.payload.payload.beacon.adcs_css_raw_5
    :field fss_active_0: ax25_frame.payload.payload.beacon.fss_active_0
    :field fss_active_1: ax25_frame.payload.payload.beacon.fss_active_1
    :field fss_active_2: ax25_frame.payload.payload.beacon.fss_active_2
    :field fss_active_3: ax25_frame.payload.payload.beacon.fss_active_3
    :field fss_active_4: ax25_frame.payload.payload.beacon.fss_active_4
    :field fss_active_5: ax25_frame.payload.payload.beacon.fss_active_5
    :field css_active_selected_0: ax25_frame.payload.payload.beacon.css_active_selected_0
    :field css_active_selected_1: ax25_frame.payload.payload.beacon.css_active_selected_1
    :field css_active_selected_2: ax25_frame.payload.payload.beacon.css_active_selected_2
    :field css_active_selected_3: ax25_frame.payload.payload.beacon.css_active_selected_3
    :field css_active_selected_4: ax25_frame.payload.payload.beacon.css_active_selected_4
    :field css_active_selected_5: ax25_frame.payload.payload.beacon.css_active_selected_5
    :field adcs_sun_processed_0: ax25_frame.payload.payload.beacon.adcs_sun_processed_0
    :field adcs_sun_processed_1: ax25_frame.payload.payload.beacon.adcs_sun_processed_1
    :field adcs_sun_processed_2: ax25_frame.payload.payload.beacon.adcs_sun_processed_2
    :field adcs_detumble_counter: ax25_frame.payload.payload.beacon.adcs_detumble_counter
    :field adcs_mode: ax25_frame.payload.payload.beacon.adcs_mode
    :field adcs_state: ax25_frame.payload.payload.beacon.adcs_state
    :field cmc_rx_lock: ax25_frame.payload.payload.beacon.cmc_rx_lock
    :field cmc_rx_frame_count: ax25_frame.payload.payload.beacon.cmc_rx_frame_count
    :field cmc_rx_packet_count: ax25_frame.payload.payload.beacon.cmc_rx_packet_count
    :field cmc_rx_dropped_error_count: ax25_frame.payload.payload.beacon.cmc_rx_dropped_error_count
    :field cmc_rx_crc_error_count: ax25_frame.payload.payload.beacon.cmc_rx_crc_error_count
    :field cmc_rx_overrun_error_count: ax25_frame.payload.payload.beacon.cmc_rx_overrun_error_count
    :field cmc_rx_protocol_error_count: ax25_frame.payload.payload.beacon.cmc_rx_protocol_error_count
    :field cmc_smps_temperature: ax25_frame.payload.payload.beacon.cmc_smps_temperature
    :field cmc_pa_temperature: ax25_frame.payload.payload.beacon.cmc_pa_temperature
    :field ax25_mux_channel_enabled_0: ax25_frame.payload.payload.beacon.ax25_mux_channel_enabled_0
    :field ax25_mux_channel_enabled_1: ax25_frame.payload.payload.beacon.ax25_mux_channel_enabled_1
    :field ax25_mux_channel_enabled_2: ax25_frame.payload.payload.beacon.ax25_mux_channel_enabled_2
    :field digipeater_enabled: ax25_frame.payload.payload.beacon.digipeater_enabled
    :field pacsat_broadcast_enabled: ax25_frame.payload.payload.beacon.pacsat_broadcast_enabled
    :field pacsat_broadcast_in_progress: ax25_frame.payload.payload.beacon.pacsat_broadcast_in_progress
    :field paramvalid_flags_0: ax25_frame.payload.payload.beacon.paramvalid_flags_0
    :field paramvalid_flags_1: ax25_frame.payload.payload.beacon.paramvalid_flags_1
    :field paramvalid_flags_2: ax25_frame.payload.payload.beacon.paramvalid_flags_2
    :field paramvalid_flags_3: ax25_frame.payload.payload.beacon.paramvalid_flags_3
    :field paramvalid_flags_4: ax25_frame.payload.payload.beacon.paramvalid_flags_4
    :field paramvalid_flags_5: ax25_frame.payload.payload.beacon.paramvalid_flags_5
    :field paramvalid_flags_6: ax25_frame.payload.payload.beacon.paramvalid_flags_6
    :field paramvalid_flags_7: ax25_frame.payload.payload.beacon.paramvalid_flags_7
    :field paramvalid_flags_8: ax25_frame.payload.payload.beacon.paramvalid_flags_8
    :field paramvalid_flags_9: ax25_frame.payload.payload.beacon.paramvalid_flags_9
    :field paramvalid_flags_10: ax25_frame.payload.payload.beacon.paramvalid_flags_10
    :field paramvalid_flags_11: ax25_frame.payload.payload.beacon.paramvalid_flags_11
    :field paramvalid_flags_12: ax25_frame.payload.payload.beacon.paramvalid_flags_12
    :field paramvalid_flags_13: ax25_frame.payload.payload.beacon.paramvalid_flags_13
    :field paramvalid_flags_14: ax25_frame.payload.payload.beacon.paramvalid_flags_14
    :field paramvalid_flags_15: ax25_frame.payload.payload.beacon.paramvalid_flags_15
    :field paramvalid_flags_16: ax25_frame.payload.payload.beacon.paramvalid_flags_16
    :field paramvalid_flags_17: ax25_frame.payload.payload.beacon.paramvalid_flags_17
    :field paramvalid_flags_18: ax25_frame.payload.payload.beacon.paramvalid_flags_18
    :field paramvalid_flags_19: ax25_frame.payload.payload.beacon.paramvalid_flags_19
    :field paramvalid_flags_20: ax25_frame.payload.payload.beacon.paramvalid_flags_20
    :field paramvalid_flags_21: ax25_frame.payload.payload.beacon.paramvalid_flags_21
    :field paramvalid_flags_22: ax25_frame.payload.payload.beacon.paramvalid_flags_22
    :field paramvalid_flags_23: ax25_frame.payload.payload.beacon.paramvalid_flags_23
    :field paramvalid_flags_24: ax25_frame.payload.payload.beacon.paramvalid_flags_24
    :field paramvalid_flags_25: ax25_frame.payload.payload.beacon.paramvalid_flags_25
    :field paramvalid_flags_26: ax25_frame.payload.payload.beacon.paramvalid_flags_26
    :field paramvalid_flags_27: ax25_frame.payload.payload.beacon.paramvalid_flags_27
    :field paramvalid_flags_28: ax25_frame.payload.payload.beacon.paramvalid_flags_28
    :field paramvalid_flags_29: ax25_frame.payload.payload.beacon.paramvalid_flags_29
    :field paramvalid_flags_30: ax25_frame.payload.payload.beacon.paramvalid_flags_30
    :field paramvalid_flags_31: ax25_frame.payload.payload.beacon.paramvalid_flags_31
    :field paramvalid_flags_32: ax25_frame.payload.payload.beacon.paramvalid_flags_32
    :field paramvalid_flags_33: ax25_frame.payload.payload.beacon.paramvalid_flags_33
    :field paramvalid_flags_34: ax25_frame.payload.payload.beacon.paramvalid_flags_34
    :field paramvalid_flags_35: ax25_frame.payload.payload.beacon.paramvalid_flags_35
    :field paramvalid_flags_36: ax25_frame.payload.payload.beacon.paramvalid_flags_36
    :field paramvalid_flags_37: ax25_frame.payload.payload.beacon.paramvalid_flags_37
    :field paramvalid_flags_38: ax25_frame.payload.payload.beacon.paramvalid_flags_38
    :field paramvalid_flags_39: ax25_frame.payload.payload.beacon.paramvalid_flags_39
    :field checksumbytes: ax25_frame.payload.payload.beacon.checksumbytes
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Mirsat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Mirsat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Mirsat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Mirsat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Mirsat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Mirsat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Mirsat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Mirsat1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Mirsat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Mirsat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Mirsat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Mirsat1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.payload = Mirsat1.PayloadT(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"3B8MRC") or (self.callsign == u"3B8MIR")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class BeaconAT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_header = Mirsat1.BeaconHeaderT(self._io, self, self._root)
            self.start_byte = self._io.read_bytes(1)
            if not self.start_byte == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.start_byte, self._io, u"/types/beacon_a_t/seq/1")
            self.obc_boot_image = self._io.read_bits_int_be(8)
            self.on_board_time = self._io.read_bits_int_be(32)
            self.uptime = self._io.read_bits_int_be(32)
            self.spacecraft_mode = self._io.read_bits_int_be(3)
            self.seperation_sequence_state = self._io.read_bits_int_be(4)
            self.solar_array_deployment_state_0 = self._io.read_bits_int_be(4)
            self.solar_array_deployment_state_1 = self._io.read_bits_int_be(4)
            self.solar_array_deployment_state_2 = self._io.read_bits_int_be(4)
            self.solar_array_deployment_state_3 = self._io.read_bits_int_be(4)
            self.antenna_deployment_state_0 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_1 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_2 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_3 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_4 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_5 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_6 = self._io.read_bits_int_be(16)
            self.antenna_deployment_state_7 = self._io.read_bits_int_be(16)
            self.adm_soft_fire_counter = self._io.read_bits_int_be(8)
            self.adm_hard_fire_counter = self._io.read_bits_int_be(8)
            self.adm_telemetry_0_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_0_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_0_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_1_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_1_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_1_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_2_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_2_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_2_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_3_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_3_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_3_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_4_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_4_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_4_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_5_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_5_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_5_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_6_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_6_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_6_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_7_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_7_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_7_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_8_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_8_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_8_l = self._io.read_bits_int_be(16)
            self.adm_telemetry_9_h = self._io.read_bits_int_be(32)
            self.adm_telemetry_9_m = self._io.read_bits_int_be(32)
            self.adm_telemetry_9_l = self._io.read_bits_int_be(16)
            self.sadm_check_counter = self._io.read_bits_int_be(5)
            self.sadm_telemetry_0_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_0_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_1_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_1_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_2_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_2_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_3_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_3_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_4_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_4_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_5_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_5_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_6_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_6_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_7_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_7_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_8_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_8_l = self._io.read_bits_int_be(32)
            self.sadm_telemetry_9_h = self._io.read_bits_int_be(32)
            self.sadm_telemetry_9_l = self._io.read_bits_int_be(32)
            self.i2c_nack_addr_count = self._io.read_bits_int_be(32)
            self.i2c_hw_state_error_count = self._io.read_bits_int_be(32)
            self.i2c_isr_error_count = self._io.read_bits_int_be(32)
            self.battery_current_direction = self._io.read_bits_int_be(1) != 0
            self.battery_current_0 = self._io.read_bits_int_be(10)
            self.battery_current_1_msb = self._io.read_bits_int_be(1) != 0

        @property
        def sadm_telemetry_4(self):
            if hasattr(self, '_m_sadm_telemetry_4'):
                return self._m_sadm_telemetry_4 if hasattr(self, '_m_sadm_telemetry_4') else None

            self._m_sadm_telemetry_4 = ((self.sadm_telemetry_4_h << 32) | self.sadm_telemetry_4_l)
            return self._m_sadm_telemetry_4 if hasattr(self, '_m_sadm_telemetry_4') else None

        @property
        def adm_telemetry_9(self):
            if hasattr(self, '_m_adm_telemetry_9'):
                return self._m_adm_telemetry_9 if hasattr(self, '_m_adm_telemetry_9') else None

            self._m_adm_telemetry_9 = (((self.adm_telemetry_9_h << 48) | (self.adm_telemetry_9_m << 32)) | self.adm_telemetry_9_l)
            return self._m_adm_telemetry_9 if hasattr(self, '_m_adm_telemetry_9') else None

        @property
        def adm_telemetry_7(self):
            if hasattr(self, '_m_adm_telemetry_7'):
                return self._m_adm_telemetry_7 if hasattr(self, '_m_adm_telemetry_7') else None

            self._m_adm_telemetry_7 = (((self.adm_telemetry_7_h << 48) | (self.adm_telemetry_7_m << 32)) | self.adm_telemetry_7_l)
            return self._m_adm_telemetry_7 if hasattr(self, '_m_adm_telemetry_7') else None

        @property
        def adm_telemetry_4(self):
            if hasattr(self, '_m_adm_telemetry_4'):
                return self._m_adm_telemetry_4 if hasattr(self, '_m_adm_telemetry_4') else None

            self._m_adm_telemetry_4 = (((self.adm_telemetry_4_h << 48) | (self.adm_telemetry_4_m << 32)) | self.adm_telemetry_4_l)
            return self._m_adm_telemetry_4 if hasattr(self, '_m_adm_telemetry_4') else None

        @property
        def adm_telemetry_6(self):
            if hasattr(self, '_m_adm_telemetry_6'):
                return self._m_adm_telemetry_6 if hasattr(self, '_m_adm_telemetry_6') else None

            self._m_adm_telemetry_6 = (((self.adm_telemetry_6_h << 48) | (self.adm_telemetry_6_m << 32)) | self.adm_telemetry_6_l)
            return self._m_adm_telemetry_6 if hasattr(self, '_m_adm_telemetry_6') else None

        @property
        def sadm_telemetry_1(self):
            if hasattr(self, '_m_sadm_telemetry_1'):
                return self._m_sadm_telemetry_1 if hasattr(self, '_m_sadm_telemetry_1') else None

            self._m_sadm_telemetry_1 = ((self.sadm_telemetry_1_h << 32) | self.sadm_telemetry_1_l)
            return self._m_sadm_telemetry_1 if hasattr(self, '_m_sadm_telemetry_1') else None

        @property
        def sadm_telemetry_6(self):
            if hasattr(self, '_m_sadm_telemetry_6'):
                return self._m_sadm_telemetry_6 if hasattr(self, '_m_sadm_telemetry_6') else None

            self._m_sadm_telemetry_6 = ((self.sadm_telemetry_6_h << 32) | self.sadm_telemetry_6_l)
            return self._m_sadm_telemetry_6 if hasattr(self, '_m_sadm_telemetry_6') else None

        @property
        def adm_telemetry_3(self):
            if hasattr(self, '_m_adm_telemetry_3'):
                return self._m_adm_telemetry_3 if hasattr(self, '_m_adm_telemetry_3') else None

            self._m_adm_telemetry_3 = (((self.adm_telemetry_3_h << 48) | (self.adm_telemetry_3_m << 16)) | self.adm_telemetry_3_l)
            return self._m_adm_telemetry_3 if hasattr(self, '_m_adm_telemetry_3') else None

        @property
        def sadm_telemetry_0(self):
            if hasattr(self, '_m_sadm_telemetry_0'):
                return self._m_sadm_telemetry_0 if hasattr(self, '_m_sadm_telemetry_0') else None

            self._m_sadm_telemetry_0 = ((self.sadm_telemetry_0_h << 32) | self.sadm_telemetry_0_l)
            return self._m_sadm_telemetry_0 if hasattr(self, '_m_sadm_telemetry_0') else None

        @property
        def adm_telemetry_8(self):
            if hasattr(self, '_m_adm_telemetry_8'):
                return self._m_adm_telemetry_8 if hasattr(self, '_m_adm_telemetry_8') else None

            self._m_adm_telemetry_8 = (((self.adm_telemetry_8_h << 48) | (self.adm_telemetry_8_m << 32)) | self.adm_telemetry_8_l)
            return self._m_adm_telemetry_8 if hasattr(self, '_m_adm_telemetry_8') else None

        @property
        def adm_telemetry_0(self):
            if hasattr(self, '_m_adm_telemetry_0'):
                return self._m_adm_telemetry_0 if hasattr(self, '_m_adm_telemetry_0') else None

            self._m_adm_telemetry_0 = (((self.adm_telemetry_0_h << 48) | (self.adm_telemetry_0_m << 16)) | self.adm_telemetry_0_l)
            return self._m_adm_telemetry_0 if hasattr(self, '_m_adm_telemetry_0') else None

        @property
        def sadm_telemetry_3(self):
            if hasattr(self, '_m_sadm_telemetry_3'):
                return self._m_sadm_telemetry_3 if hasattr(self, '_m_sadm_telemetry_3') else None

            self._m_sadm_telemetry_3 = ((self.sadm_telemetry_3_h << 32) | self.sadm_telemetry_3_l)
            return self._m_sadm_telemetry_3 if hasattr(self, '_m_sadm_telemetry_3') else None

        @property
        def sadm_telemetry_9(self):
            if hasattr(self, '_m_sadm_telemetry_9'):
                return self._m_sadm_telemetry_9 if hasattr(self, '_m_sadm_telemetry_9') else None

            self._m_sadm_telemetry_9 = ((self.sadm_telemetry_9_h << 32) | self.sadm_telemetry_9_l)
            return self._m_sadm_telemetry_9 if hasattr(self, '_m_sadm_telemetry_9') else None

        @property
        def adm_telemetry_5(self):
            if hasattr(self, '_m_adm_telemetry_5'):
                return self._m_adm_telemetry_5 if hasattr(self, '_m_adm_telemetry_5') else None

            self._m_adm_telemetry_5 = (((self.adm_telemetry_5_h << 48) | (self.adm_telemetry_5_m << 32)) | self.adm_telemetry_5_l)
            return self._m_adm_telemetry_5 if hasattr(self, '_m_adm_telemetry_5') else None

        @property
        def sadm_telemetry_5(self):
            if hasattr(self, '_m_sadm_telemetry_5'):
                return self._m_sadm_telemetry_5 if hasattr(self, '_m_sadm_telemetry_5') else None

            self._m_sadm_telemetry_5 = ((self.sadm_telemetry_5_h << 32) | self.sadm_telemetry_5_l)
            return self._m_sadm_telemetry_5 if hasattr(self, '_m_sadm_telemetry_5') else None

        @property
        def adm_telemetry_2(self):
            if hasattr(self, '_m_adm_telemetry_2'):
                return self._m_adm_telemetry_2 if hasattr(self, '_m_adm_telemetry_2') else None

            self._m_adm_telemetry_2 = (((self.adm_telemetry_2_h << 48) | (self.adm_telemetry_2_m << 16)) | self.adm_telemetry_2_l)
            return self._m_adm_telemetry_2 if hasattr(self, '_m_adm_telemetry_2') else None

        @property
        def sadm_telemetry_2(self):
            if hasattr(self, '_m_sadm_telemetry_2'):
                return self._m_sadm_telemetry_2 if hasattr(self, '_m_sadm_telemetry_2') else None

            self._m_sadm_telemetry_2 = ((self.sadm_telemetry_2_h << 32) | self.sadm_telemetry_2_l)
            return self._m_sadm_telemetry_2 if hasattr(self, '_m_sadm_telemetry_2') else None

        @property
        def sadm_telemetry_8(self):
            if hasattr(self, '_m_sadm_telemetry_8'):
                return self._m_sadm_telemetry_8 if hasattr(self, '_m_sadm_telemetry_8') else None

            self._m_sadm_telemetry_8 = ((self.sadm_telemetry_8_h << 32) | self.sadm_telemetry_8_l)
            return self._m_sadm_telemetry_8 if hasattr(self, '_m_sadm_telemetry_8') else None

        @property
        def sadm_telemetry_7(self):
            if hasattr(self, '_m_sadm_telemetry_7'):
                return self._m_sadm_telemetry_7 if hasattr(self, '_m_sadm_telemetry_7') else None

            self._m_sadm_telemetry_7 = ((self.sadm_telemetry_7_h << 32) | self.sadm_telemetry_7_l)
            return self._m_sadm_telemetry_7 if hasattr(self, '_m_sadm_telemetry_7') else None

        @property
        def adm_telemetry_1(self):
            if hasattr(self, '_m_adm_telemetry_1'):
                return self._m_adm_telemetry_1 if hasattr(self, '_m_adm_telemetry_1') else None

            self._m_adm_telemetry_1 = (((self.adm_telemetry_1_h << 48) | (self.adm_telemetry_1_m << 16)) | self.adm_telemetry_1_l)
            return self._m_adm_telemetry_1 if hasattr(self, '_m_adm_telemetry_1') else None


    class BeaconHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_type = self._io.read_u1()
            self.apid = self._io.read_u1()
            self.sequence_count = self._io.read_u2be()
            self.length = self._io.read_u2be()
            self.reserved = self._io.read_u1()
            self.service_type = self._io.read_u1()
            self.sub_service_type = self._io.read_u1()


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon = self._io.read_bytes_full()


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


    class PayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_bytes(6)
            _on = self._root.frametype
            if _on == 793:
                self.beacon = Mirsat1.BeaconAT(self._io, self, self._root)
            else:
                self.beacon = Mirsat1.BeaconBT(self._io, self, self._root)


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
            self.callsign_ror = Mirsat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class BeaconBT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_current_1_lsbs = self._io.read_bits_int_be(9)
            self.battery_current_2 = self._io.read_bits_int_be(10)
            self.battery_voltage_0 = self._io.read_bits_int_be(10)
            self.battery_voltage_1 = self._io.read_bits_int_be(10)
            self.battery_voltage_2 = self._io.read_bits_int_be(10)
            self.battery_temperature = self._io.read_bits_int_be(10)
            self.solar_array_current_0 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_0 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_1 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_2 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_3 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_4 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_5 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_6 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_7 = self._io.read_bits_int_be(10)
            self.solar_array_voltage_8 = self._io.read_bits_int_be(10)
            self.eps_bus_voltage_0 = self._io.read_bits_int_be(10)
            self.eps_bus_voltage_1 = self._io.read_bits_int_be(10)
            self.eps_bus_voltage_2 = self._io.read_bits_int_be(10)
            self.eps_bus_voltage_3 = self._io.read_bits_int_be(10)
            self.eps_bus_current_0 = self._io.read_bits_int_be(10)
            self.eps_bus_current_1 = self._io.read_bits_int_be(10)
            self.eps_bus_current_2 = self._io.read_bits_int_be(10)
            self.eps_bus_current_3 = self._io.read_bits_int_be(10)
            self.adcs_raw_gyro_rate_0_bits = self._io.read_bits_int_be(16)
            self.adcs_raw_gyro_rate_1_bits = self._io.read_bits_int_be(16)
            self.adcs_raw_gyro_rate_2_bits = self._io.read_bits_int_be(16)
            self.adcs_mtq_direction_duty_0 = self._io.read_bits_int_be(8)
            self.adcs_mtq_direction_duty_1 = self._io.read_bits_int_be(8)
            self.adcs_mtq_direction_duty_2 = self._io.read_bits_int_be(8)
            self.adcs_mtq_direction_duty_3 = self._io.read_bits_int_be(8)
            self.adcs_mtq_direction_duty_4 = self._io.read_bits_int_be(8)
            self.adcs_mtq_direction_duty_5 = self._io.read_bits_int_be(8)
            self.adcs_status = self._io.read_bits_int_be(16)
            self.adcs_bus_voltage_0 = self._io.read_bits_int_be(16)
            self.adcs_bus_voltage_1 = self._io.read_bits_int_be(16)
            self.adcs_bus_voltage_2 = self._io.read_bits_int_be(16)
            self.adcs_bus_current_0 = self._io.read_bits_int_be(16)
            self.adcs_bus_current_1 = self._io.read_bits_int_be(16)
            self.adcs_bus_current_2 = self._io.read_bits_int_be(16)
            self.adcs_board_temperature = self._io.read_bits_int_be(16)
            self.adcs_adc_reference = self._io.read_bits_int_be(16)
            self.adcs_sensor_current = self._io.read_bits_int_be(16)
            self.adcs_mtq_current = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_0 = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_1 = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_2 = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_3 = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_4 = self._io.read_bits_int_be(16)
            self.adcs_array_temperature_5 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_0 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_1 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_2 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_3 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_4 = self._io.read_bits_int_be(16)
            self.adcs_css_raw_5 = self._io.read_bits_int_be(16)
            self.fss_active_0 = self._io.read_bits_int_be(2)
            self.fss_active_1 = self._io.read_bits_int_be(2)
            self.fss_active_2 = self._io.read_bits_int_be(2)
            self.fss_active_3 = self._io.read_bits_int_be(2)
            self.fss_active_4 = self._io.read_bits_int_be(2)
            self.fss_active_5 = self._io.read_bits_int_be(2)
            self.css_active_selected_0 = self._io.read_bits_int_be(2)
            self.css_active_selected_1 = self._io.read_bits_int_be(2)
            self.css_active_selected_2 = self._io.read_bits_int_be(2)
            self.css_active_selected_3 = self._io.read_bits_int_be(2)
            self.css_active_selected_4 = self._io.read_bits_int_be(2)
            self.css_active_selected_5 = self._io.read_bits_int_be(2)
            self.adcs_sun_processed_0 = self._io.read_bits_int_be(16)
            self.adcs_sun_processed_1 = self._io.read_bits_int_be(16)
            self.adcs_sun_processed_2 = self._io.read_bits_int_be(16)
            self.reserved_0 = self._io.read_bits_int_be(16)
            self.reserved_1 = self._io.read_bits_int_be(16)
            self.reserved_2 = self._io.read_bits_int_be(16)
            self.reserved_3 = self._io.read_bits_int_be(16)
            self.adcs_detumble_counter = self._io.read_bits_int_be(16)
            self.adcs_mode = self._io.read_bits_int_be(16)
            self.adcs_state = self._io.read_bits_int_be(16)
            self.reserved_4 = self._io.read_bits_int_be(10)
            self.reserved_5 = self._io.read_bits_int_be(4)
            self.reserved_6 = self._io.read_bits_int_be(16)
            self.reserved_7 = self._io.read_bits_int_be(3)
            self.reserved_8 = self._io.read_bits_int_be(4)
            self.cmc_rx_lock = self._io.read_bits_int_be(1) != 0
            self.cmc_rx_frame_count = self._io.read_bits_int_be(16)
            self.cmc_rx_packet_count = self._io.read_bits_int_be(16)
            self.cmc_rx_dropped_error_count = self._io.read_bits_int_be(16)
            self.cmc_rx_crc_error_count = self._io.read_bits_int_be(16)
            self.cmc_rx_overrun_error_count = self._io.read_bits_int_be(8)
            self.cmc_rx_protocol_error_count = self._io.read_bits_int_be(16)
            self.cmc_smps_temperature_bits = self._io.read_bits_int_be(8)
            self.cmc_pa_temperature_bits = self._io.read_bits_int_be(8)
            self.ax25_mux_channel_enabled_0 = self._io.read_bits_int_be(1) != 0
            self.ax25_mux_channel_enabled_1 = self._io.read_bits_int_be(1) != 0
            self.ax25_mux_channel_enabled_2 = self._io.read_bits_int_be(1) != 0
            self.digipeater_enabled = self._io.read_bits_int_be(1) != 0
            self.pacsat_broadcast_enabled = self._io.read_bits_int_be(1) != 0
            self.pacsat_broadcast_in_progress = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_0 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_1 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_2 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_3 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_4 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_5 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_6 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_7 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_8 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_9 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_10 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_11 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_12 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_13 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_14 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_15 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_16 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_17 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_18 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_19 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_20 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_21 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_22 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_23 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_24 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_25 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_26 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_27 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_28 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_29 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_30 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_31 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_32 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_33 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_34 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_35 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_36 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_37 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_38 = self._io.read_bits_int_be(1) != 0
            self.paramvalid_flags_39 = self._io.read_bits_int_be(1) != 0
            self.padding = self._io.read_bits_int_be(5)
            self.checksumbytes = self._io.read_bits_int_be(16)
            self._io.align_to_byte()
            self.tail = self._io.read_bytes(97)

        @property
        def cmc_pa_temperature(self):
            if hasattr(self, '_m_cmc_pa_temperature'):
                return self._m_cmc_pa_temperature if hasattr(self, '_m_cmc_pa_temperature') else None

            self._m_cmc_pa_temperature = ((-1 * (self.cmc_pa_temperature_bits & 127)) if (self.cmc_pa_temperature_bits & 128) == 1 else (self.cmc_pa_temperature_bits & 127))
            return self._m_cmc_pa_temperature if hasattr(self, '_m_cmc_pa_temperature') else None

        @property
        def adcs_raw_gyro_rate_1(self):
            if hasattr(self, '_m_adcs_raw_gyro_rate_1'):
                return self._m_adcs_raw_gyro_rate_1 if hasattr(self, '_m_adcs_raw_gyro_rate_1') else None

            self._m_adcs_raw_gyro_rate_1 = ((-1 * (self.adcs_raw_gyro_rate_1_bits & 32767)) if (self.adcs_raw_gyro_rate_1_bits & 32768) == 1 else (self.adcs_raw_gyro_rate_1_bits & 32767))
            return self._m_adcs_raw_gyro_rate_1 if hasattr(self, '_m_adcs_raw_gyro_rate_1') else None

        @property
        def adcs_raw_gyro_rate_2(self):
            if hasattr(self, '_m_adcs_raw_gyro_rate_2'):
                return self._m_adcs_raw_gyro_rate_2 if hasattr(self, '_m_adcs_raw_gyro_rate_2') else None

            self._m_adcs_raw_gyro_rate_2 = ((-1 * (self.adcs_raw_gyro_rate_1_bits & 32767)) if (self.adcs_raw_gyro_rate_1_bits & 32768) == 1 else (self.adcs_raw_gyro_rate_1_bits & 32767))
            return self._m_adcs_raw_gyro_rate_2 if hasattr(self, '_m_adcs_raw_gyro_rate_2') else None

        @property
        def adcs_raw_gyro_rate_0(self):
            if hasattr(self, '_m_adcs_raw_gyro_rate_0'):
                return self._m_adcs_raw_gyro_rate_0 if hasattr(self, '_m_adcs_raw_gyro_rate_0') else None

            self._m_adcs_raw_gyro_rate_0 = ((-1 * (self.adcs_raw_gyro_rate_0_bits & 32767)) if (self.adcs_raw_gyro_rate_0_bits & 32768) == 1 else (self.adcs_raw_gyro_rate_0_bits & 32767))
            return self._m_adcs_raw_gyro_rate_0 if hasattr(self, '_m_adcs_raw_gyro_rate_0') else None

        @property
        def cmc_smps_temperature(self):
            if hasattr(self, '_m_cmc_smps_temperature'):
                return self._m_cmc_smps_temperature if hasattr(self, '_m_cmc_smps_temperature') else None

            self._m_cmc_smps_temperature = ((-1 * (self.cmc_smps_temperature_bits & 127)) if (self.cmc_smps_temperature_bits & 128) == 1 else (self.cmc_smps_temperature_bits & 127))
            return self._m_cmc_smps_temperature if hasattr(self, '_m_cmc_smps_temperature') else None


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None

    @property
    def frametype(self):
        if hasattr(self, '_m_frametype'):
            return self._m_frametype if hasattr(self, '_m_frametype') else None

        _pos = self._io.pos()
        self._io.seek(29)
        self._m_frametype = self._io.read_u2be()
        self._io.seek(_pos)
        return self._m_frametype if hasattr(self, '_m_frametype') else None


