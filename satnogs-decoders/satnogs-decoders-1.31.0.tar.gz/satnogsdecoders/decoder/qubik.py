# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Qubik(KaitaiStruct):
    """:field channel_id: osdlp_tm_frame.tm_tf_primary_header.channel_id
    :field master_channel_frame_count: osdlp_tm_frame.tm_tf_primary_header.master_channel_frame_count
    :field virtual_channel_frame_count: osdlp_tm_frame.tm_tf_primary_header.virtual_channel_frame_count
    :field transfer_frame_data_field_status: osdlp_tm_frame.tm_tf_primary_header.transfer_frame_data_field_status
    :field master_channel_id: osdlp_tm_frame.tm_tf_primary_header.master_channel_id
    :field tf_version_number: osdlp_tm_frame.tm_tf_primary_header.tf_version_number
    :field spacecraft_id: osdlp_tm_frame.tm_tf_primary_header.spacecraft_id
    :field virtual_channel_id: osdlp_tm_frame.tm_tf_primary_header.virtual_channel_id
    :field ocf_flag: osdlp_tm_frame.tm_tf_primary_header.ocf_flag
    :field tf_secondary_header_flag: osdlp_tm_frame.tm_tf_primary_header.tf_secondary_header_flag
    :field synch_flag: osdlp_tm_frame.tm_tf_primary_header.synch_flag
    :field packet_order_flag: osdlp_tm_frame.tm_tf_primary_header.packet_order_flag
    :field segment_length_id: osdlp_tm_frame.tm_tf_primary_header.segment_length_id
    :field first_header_pointer: osdlp_tm_frame.tm_tf_primary_header.first_header_pointer
    :field length: osdlp_tm_frame.tm_tf_data_field.payload.length
    :field curr_ins: osdlp_tm_frame.tm_tf_data_field.payload.curr_ins
    :field volt_ins: osdlp_tm_frame.tm_tf_data_field.payload.volt_ins
    :field temp_die: osdlp_tm_frame.tm_tf_data_field.payload.temp_die
    :field temp_bat: osdlp_tm_frame.tm_tf_data_field.payload.temp_bat
    :field curr_min: osdlp_tm_frame.tm_tf_data_field.payload.curr_min
    :field volt_min: osdlp_tm_frame.tm_tf_data_field.payload.volt_min
    :field temp_bat_min: osdlp_tm_frame.tm_tf_data_field.payload.temp_bat_min
    :field curr_max: osdlp_tm_frame.tm_tf_data_field.payload.curr_max
    :field volt_max: osdlp_tm_frame.tm_tf_data_field.payload.volt_max
    :field temp_bat_max: osdlp_tm_frame.tm_tf_data_field.payload.temp_bat_max
    :field curr_av: osdlp_tm_frame.tm_tf_data_field.payload.curr_av
    :field volt_av: osdlp_tm_frame.tm_tf_data_field.payload.volt_av
    :field temp_bat_av: osdlp_tm_frame.tm_tf_data_field.payload.temp_bat_av
    :field time_empty: osdlp_tm_frame.tm_tf_data_field.payload.time_empty
    :field cap_remain: osdlp_tm_frame.tm_tf_data_field.payload.cap_remain
    :field cap_full: osdlp_tm_frame.tm_tf_data_field.payload.cap_full
    :field charge_state: osdlp_tm_frame.tm_tf_data_field.payload.charge_state
    :field ant_test_volt: osdlp_tm_frame.tm_tf_data_field.payload.ant_test_volt
    :field ant_test_curr: osdlp_tm_frame.tm_tf_data_field.payload.ant_test_curr
    :field ant_test_res: osdlp_tm_frame.tm_tf_data_field.payload.ant_test_res
    :field ant_avg_volt: osdlp_tm_frame.tm_tf_data_field.payload.ant_avg_volt
    :field ant_avg_curr: osdlp_tm_frame.tm_tf_data_field.payload.ant_avg_curr
    :field ant_dep_duration: osdlp_tm_frame.tm_tf_data_field.payload.ant_dep_duration
    :field ant_dep_status: osdlp_tm_frame.tm_tf_data_field.payload.ant_dep_status
    :field ant_dep_retries: osdlp_tm_frame.tm_tf_data_field.payload.ant_dep_retries
    :field uptime: osdlp_tm_frame.tm_tf_data_field.payload.uptime
    :field temp_internal: osdlp_tm_frame.tm_tf_data_field.payload.temp_internal
    :field rtc_bat_volt: osdlp_tm_frame.tm_tf_data_field.payload.rtc_bat_volt
    :field deploy_first: osdlp_tm_frame.tm_tf_data_field.payload.deploy_first
    :field deploy_first_ant: osdlp_tm_frame.tm_tf_data_field.payload.deploy_first_ant
    :field ror_unknown: osdlp_tm_frame.tm_tf_data_field.payload.ror_unknown
    :field ror_low_power: osdlp_tm_frame.tm_tf_data_field.payload.ror_low_power
    :field ror_window_watchdog: osdlp_tm_frame.tm_tf_data_field.payload.ror_window_watchdog
    :field ror_independent_watchdog_reset: osdlp_tm_frame.tm_tf_data_field.payload.ror_independent_watchdog_reset
    :field ror_software: osdlp_tm_frame.tm_tf_data_field.payload.ror_software
    :field ror_power_on_power_down: osdlp_tm_frame.tm_tf_data_field.payload.ror_power_on_power_down
    :field ror_external_reset_pin: osdlp_tm_frame.tm_tf_data_field.payload.ror_external_reset_pin
    :field ror_brownout: osdlp_tm_frame.tm_tf_data_field.payload.ror_brownout
    :field dropped_frames: osdlp_tm_frame.tm_tf_data_field.payload.dropped_frames
    :field rorc_low_power: osdlp_tm_frame.tm_tf_data_field.payload.rorc_low_power
    :field rorc_ind_wdg: osdlp_tm_frame.tm_tf_data_field.payload.rorc_ind_wdg
    :field rorc_software: osdlp_tm_frame.tm_tf_data_field.payload.rorc_software
    :field rorc_brownout: osdlp_tm_frame.tm_tf_data_field.payload.rorc_brownout
    :field power_save: osdlp_tm_frame.tm_tf_data_field.payload.power_save
    :field power_monitor_fail: osdlp_tm_frame.tm_tf_data_field.payload.power_monitor_fail
    :field clcw_0_cw_type: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.cw_type
    :field clcw_0_clcw_ver: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.clcw_ver
    :field clcw_0_status_field: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.status_field
    :field clcw_0_cop: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.cop
    :field clcw_0_vcid: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.vcid
    :field clcw_0_rsvd_a: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.rsvd_a
    :field clcw_0_flag_norf: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.flag_norf
    :field clcw_0_flag_nobitlock: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.flag_nobitlock
    :field clcw_0_flag_lockout: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.flag_lockout
    :field clcw_0_flag_wait: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.flag_wait
    :field clcw_0_flag_retransmit: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.flag_retransmit
    :field clcw_0_farm_b_counter: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.farm_b_counter
    :field clcw_0_rsvd_b: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.rsvd_b
    :field clcw_0_report_value: osdlp_tm_frame.tm_tf_data_field.payload.clcw_0.report_value
    :field clcw_1_cw_type: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.cw_type
    :field clcw_1_clcw_ver: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.clcw_ver
    :field clcw_1_status_field: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.status_field
    :field clcw_1_cop: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.cop
    :field clcw_1_vcid: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.vcid
    :field clcw_1_rsvd_a: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.rsvd_a
    :field clcw_1_flag_norf: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.flag_norf
    :field clcw_1_flag_nobitlock: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.flag_nobitlock
    :field clcw_1_flag_lockout: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.flag_lockout
    :field clcw_1_flag_wait: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.flag_wait
    :field clcw_1_flag_retransmit: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.flag_retransmit
    :field clcw_1_farm_b_counter: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.farm_b_counter
    :field clcw_1_rsvd_b: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.rsvd_b
    :field clcw_1_report_value: osdlp_tm_frame.tm_tf_data_field.payload.clcw_1.report_value
    :field clcw_2_cw_type: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.cw_type
    :field clcw_2_clcw_ver: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.clcw_ver
    :field clcw_2_status_field: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.status_field
    :field clcw_2_cop: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.cop
    :field clcw_2_vcid: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.vcid
    :field clcw_2_rsvd_a: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.rsvd_a
    :field clcw_2_flag_norf: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.flag_norf
    :field clcw_2_flag_nobitlock: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.flag_nobitlock
    :field clcw_2_flag_lockout: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.flag_lockout
    :field clcw_2_flag_wait: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.flag_wait
    :field clcw_2_flag_retransmit: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.flag_retransmit
    :field clcw_2_farm_b_counter: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.farm_b_counter
    :field clcw_2_rsvd_b: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.rsvd_b
    :field clcw_2_report_value: osdlp_tm_frame.tm_tf_data_field.payload.clcw_2.report_value
    :field clcw_3_cw_type: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.cw_type
    :field clcw_3_clcw_ver: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.clcw_ver
    :field clcw_3_status_field: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.status_field
    :field clcw_3_cop: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.cop
    :field clcw_3_vcid: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.vcid
    :field clcw_3_rsvd_a: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.rsvd_a
    :field clcw_3_flag_norf: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.flag_norf
    :field clcw_3_flag_nobitlock: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.flag_nobitlock
    :field clcw_3_flag_lockout: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.flag_lockout
    :field clcw_3_flag_wait: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.flag_wait
    :field clcw_3_flag_retransmit: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.flag_retransmit
    :field clcw_3_farm_b_counter: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.farm_b_counter
    :field clcw_3_rsvd_b: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.rsvd_b
    :field clcw_3_report_value: osdlp_tm_frame.tm_tf_data_field.payload.clcw_3.report_value
    :field clcw_4_cw_type: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.cw_type
    :field clcw_4_clcw_ver: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.clcw_ver
    :field clcw_4_status_field: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.status_field
    :field clcw_4_cop: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.cop
    :field clcw_4_vcid: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.vcid
    :field clcw_4_rsvd_a: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.rsvd_a
    :field clcw_4_flag_norf: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.flag_norf
    :field clcw_4_flag_nobitlock: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.flag_nobitlock
    :field clcw_4_flag_lockout: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.flag_lockout
    :field clcw_4_flag_wait: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.flag_wait
    :field clcw_4_flag_retransmit: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.flag_retransmit
    :field clcw_4_farm_b_counter: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.farm_b_counter
    :field clcw_4_rsvd_b: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.rsvd_b
    :field clcw_4_report_value: osdlp_tm_frame.tm_tf_data_field.payload.clcw_4.report_value
    :field tx_frames: osdlp_tm_frame.tm_tf_data_field.payload.tx_frames
    :field rx_frames: osdlp_tm_frame.tm_tf_data_field.payload.rx_frames
    :field rx_corrected_bits: osdlp_tm_frame.tm_tf_data_field.payload.rx_corrected_bits
    :field rssi: osdlp_tm_frame.tm_tf_data_field.payload.rssi
    :field freq_tracking: osdlp_tm_frame.tm_tf_data_field.payload.freq_tracking
    :field agc: osdlp_tm_frame.tm_tf_data_field.payload.agc
    :field datarate_tracking: osdlp_tm_frame.tm_tf_data_field.payload.datarate_tracking
    :field phase_tracking: osdlp_tm_frame.tm_tf_data_field.payload.phase_tracking
    :field rf_freq_tracking: osdlp_tm_frame.tm_tf_data_field.payload.rf_freq_tracking
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.osdlp_tm_frame = Qubik.TmTransferFrameT(self._io, self, self._root)

    class VcidTmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = self._io.read_u2be()
            self.curr_ins = self._io.read_s2be()
            self.volt_ins = self._io.read_u2be()
            self.temp_die = self._io.read_s1()
            self.temp_bat = self._io.read_s1()
            self.curr_min = self._io.read_s2be()
            self.volt_min = self._io.read_u2be()
            self.temp_bat_min = self._io.read_s1()
            self.curr_max = self._io.read_s2be()
            self.volt_max = self._io.read_u2be()
            self.temp_bat_max = self._io.read_s1()
            self.curr_av = self._io.read_s2be()
            self.volt_av = self._io.read_u2be()
            self.temp_bat_av = self._io.read_s1()
            self.time_empty = self._io.read_u2be()
            self.cap_remain = self._io.read_s2be()
            self.cap_full = self._io.read_s2be()
            self.charge_state = self._io.read_s1()
            self.ant_test_volt = self._io.read_s2be()
            self.ant_test_curr = self._io.read_s2be()
            self.ant_test_res = self._io.read_u1()
            self.ant_avg_volt = self._io.read_s2be()
            self.ant_avg_curr = self._io.read_s2be()
            self.ant_dep_duration = self._io.read_u1()
            self.ant_dep_status = self._io.read_u1()
            self.ant_dep_retries = self._io.read_u1()
            self.uptime = self._io.read_u4be()
            self.temp_internal = self._io.read_s1()
            self.rtc_bat_volt = self._io.read_u2be()
            self.deploy_first = self._io.read_u1()
            self.deploy_first_ant = self._io.read_u1()
            self.ror_unknown = self._io.read_bits_int_be(1) != 0
            self.ror_low_power = self._io.read_bits_int_be(1) != 0
            self.ror_window_watchdog = self._io.read_bits_int_be(1) != 0
            self.ror_independent_watchdog_reset = self._io.read_bits_int_be(1) != 0
            self.ror_software = self._io.read_bits_int_be(1) != 0
            self.ror_power_on_power_down = self._io.read_bits_int_be(1) != 0
            self.ror_external_reset_pin = self._io.read_bits_int_be(1) != 0
            self.ror_brownout = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.dropped_frames = self._io.read_u2be()
            self.rorc_low_power = self._io.read_u2be()
            self.rorc_ind_wdg = self._io.read_u2be()
            self.rorc_software = self._io.read_u2be()
            self.rorc_brownout = self._io.read_u2be()
            self.power_save = self._io.read_u1()
            self.power_monitor_fail = self._io.read_u1()
            self.clcw_0 = Qubik.Clcw(self._io, self, self._root)
            self.clcw_1 = Qubik.Clcw(self._io, self, self._root)
            self.clcw_2 = Qubik.Clcw(self._io, self, self._root)
            self.clcw_3 = Qubik.Clcw(self._io, self, self._root)
            self.clcw_4 = Qubik.Clcw(self._io, self, self._root)
            self.tx_frames = self._io.read_u2be()
            self.rx_frames = self._io.read_u2be()
            self.rx_corrected_bits = self._io.read_u4be()
            self.rssi = self._io.read_s1()
            self.freq_tracking = self._io.read_s2be()
            self.agc = self._io.read_s1()
            self.datarate_tracking = self._io.read_s4be()
            self.phase_tracking = self._io.read_s2be()
            self.rf_freq_tracking = self._io.read_s4be()


    class VcidExperimentT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes_full()


    class PrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel_id = self._io.read_u2be()
            self.master_channel_frame_count = self._io.read_u1()
            self.virtual_channel_frame_count = self._io.read_u1()
            self.transfer_frame_data_field_status = self._io.read_u2be()

        @property
        def synch_flag(self):
            if hasattr(self, '_m_synch_flag'):
                return self._m_synch_flag if hasattr(self, '_m_synch_flag') else None

            self._m_synch_flag = ((self.transfer_frame_data_field_status & 16384) >> 14)
            return self._m_synch_flag if hasattr(self, '_m_synch_flag') else None

        @property
        def spacecraft_id(self):
            if hasattr(self, '_m_spacecraft_id'):
                return self._m_spacecraft_id if hasattr(self, '_m_spacecraft_id') else None

            self._m_spacecraft_id = (self.master_channel_id & 255)
            return self._m_spacecraft_id if hasattr(self, '_m_spacecraft_id') else None

        @property
        def first_header_pointer(self):
            if hasattr(self, '_m_first_header_pointer'):
                return self._m_first_header_pointer if hasattr(self, '_m_first_header_pointer') else None

            self._m_first_header_pointer = (self.transfer_frame_data_field_status & 2047)
            return self._m_first_header_pointer if hasattr(self, '_m_first_header_pointer') else None

        @property
        def master_channel_id(self):
            if hasattr(self, '_m_master_channel_id'):
                return self._m_master_channel_id if hasattr(self, '_m_master_channel_id') else None

            self._m_master_channel_id = ((self.channel_id & 65520) >> 4)
            return self._m_master_channel_id if hasattr(self, '_m_master_channel_id') else None

        @property
        def packet_order_flag(self):
            if hasattr(self, '_m_packet_order_flag'):
                return self._m_packet_order_flag if hasattr(self, '_m_packet_order_flag') else None

            self._m_packet_order_flag = ((self.transfer_frame_data_field_status & 8192) >> 13)
            return self._m_packet_order_flag if hasattr(self, '_m_packet_order_flag') else None

        @property
        def tf_secondary_header_flag(self):
            if hasattr(self, '_m_tf_secondary_header_flag'):
                return self._m_tf_secondary_header_flag if hasattr(self, '_m_tf_secondary_header_flag') else None

            self._m_tf_secondary_header_flag = ((self.transfer_frame_data_field_status & 32768) >> 15)
            return self._m_tf_secondary_header_flag if hasattr(self, '_m_tf_secondary_header_flag') else None

        @property
        def tf_version_number(self):
            if hasattr(self, '_m_tf_version_number'):
                return self._m_tf_version_number if hasattr(self, '_m_tf_version_number') else None

            self._m_tf_version_number = ((self.master_channel_id & 3072) >> 2)
            return self._m_tf_version_number if hasattr(self, '_m_tf_version_number') else None

        @property
        def ocf_flag(self):
            if hasattr(self, '_m_ocf_flag'):
                return self._m_ocf_flag if hasattr(self, '_m_ocf_flag') else None

            self._m_ocf_flag = (self.channel_id & 1)
            return self._m_ocf_flag if hasattr(self, '_m_ocf_flag') else None

        @property
        def virtual_channel_id(self):
            if hasattr(self, '_m_virtual_channel_id'):
                return self._m_virtual_channel_id if hasattr(self, '_m_virtual_channel_id') else None

            self._m_virtual_channel_id = ((self.channel_id & 14) >> 1)
            return self._m_virtual_channel_id if hasattr(self, '_m_virtual_channel_id') else None

        @property
        def segment_length_id(self):
            if hasattr(self, '_m_segment_length_id'):
                return self._m_segment_length_id if hasattr(self, '_m_segment_length_id') else None

            self._m_segment_length_id = ((self.transfer_frame_data_field_status & 6144) >> 12)
            return self._m_segment_length_id if hasattr(self, '_m_segment_length_id') else None


    class Clcw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cw_type = self._io.read_bits_int_be(1) != 0
            self.clcw_ver = self._io.read_bits_int_be(2)
            self.status_field = self._io.read_bits_int_be(3)
            self.cop = self._io.read_bits_int_be(2)
            self.vcid = self._io.read_bits_int_be(6)
            self.rsvd_a = self._io.read_bits_int_be(2)
            self.flag_norf = self._io.read_bits_int_be(1) != 0
            self.flag_nobitlock = self._io.read_bits_int_be(1) != 0
            self.flag_lockout = self._io.read_bits_int_be(1) != 0
            self.flag_wait = self._io.read_bits_int_be(1) != 0
            self.flag_retransmit = self._io.read_bits_int_be(1) != 0
            self.farm_b_counter = self._io.read_bits_int_be(2)
            self.rsvd_b = self._io.read_bits_int_be(1) != 0
            self.report_value = self._io.read_bits_int_be(8)


    class TmTfDataFieldT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.tm_tf_primary_header.virtual_channel_id
            if _on == 0:
                self._raw_payload = self._io.read_bytes(116)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qubik.VcidManagementT(_io__raw_payload, self, self._root)
            elif _on == 4:
                self._raw_payload = self._io.read_bytes(116)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qubik.VcidContactT(_io__raw_payload, self, self._root)
            elif _on == 1:
                self._raw_payload = self._io.read_bytes(116)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qubik.VcidTmT(_io__raw_payload, self, self._root)
            elif _on == 3:
                self._raw_payload = self._io.read_bytes(116)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qubik.VcidExperimentT(_io__raw_payload, self, self._root)
            elif _on == 2:
                self._raw_payload = self._io.read_bytes(116)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qubik.VcidExtTmT(_io__raw_payload, self, self._root)
            else:
                self.payload = self._io.read_bytes(116)


    class VcidContactT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes_full()


    class VcidManagementT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes_full()


    class TmTransferFrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_tm_tf_primary_header = self._io.read_bytes(6)
            _io__raw_tm_tf_primary_header = KaitaiStream(BytesIO(self._raw_tm_tf_primary_header))
            self.tm_tf_primary_header = Qubik.PrimaryHeaderT(_io__raw_tm_tf_primary_header, self, self._root)
            _on = self.tm_tf_primary_header.tf_secondary_header_flag
            if _on == 1:
                self.tf_secondary_header = self._io.read_u2be()
            self.tm_tf_data_field = Qubik.TmTfDataFieldT(self._io, self, self._root)
            self.tm_tf_trailer = self._io.read_bytes(6)
            self.unparsed = self._io.read_bytes_full()


    class VcidExtTmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes_full()



