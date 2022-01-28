# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mitee1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field mitee_hdr_pyld_len: ax25_frame.payload.ax25_info.mitee_hdr.pyld_len
    :field mitee_hdr_pkt_no: ax25_frame.payload.ax25_info.mitee_hdr.pkt_no
    :field mitee_hdr_pkt_cnt: ax25_frame.payload.ax25_info.mitee_hdr.pkt_cnt
    :field mitee_hdr_grp_no: ax25_frame.payload.ax25_info.mitee_hdr.grp_no
    :field mitee_hdr_grp_size: ax25_frame.payload.ax25_info.mitee_hdr.grp_size
    :field mitee_hdr_status: ax25_frame.payload.ax25_info.mitee_hdr.status
    :field mitee_hdr_chksm: ax25_frame.payload.ax25_info.mitee_hdr.hdr_chksm
    :field mitee_stats_bcn_tx: ax25_frame.payload.ax25_info.comms.mitee_stats.bcn_tx
    :field mitee_stats_pkts_tx: ax25_frame.payload.ax25_info.comms.mitee_stats.pkts_tx
    :field mitee_stats_pkts_rx: ax25_frame.payload.ax25_info.comms.mitee_stats.pkts_rx
    :field mitee_stats_bytes_tx: ax25_frame.payload.ax25_info.comms.mitee_stats.bytes_tx
    :field mitee_stats_bytes_rx: ax25_frame.payload.ax25_info.comms.mitee_stats.bytes_rx
    :field mitee_stats_sync_errs: ax25_frame.payload.ax25_info.comms.mitee_stats.sync_errs
    :field mitee_stats_hdr_chksm_errs: ax25_frame.payload.ax25_info.comms.mitee_stats.hdr_chksm_errs
    :field mitee_stats_pyld_chksm_errs: ax25_frame.payload.ax25_info.comms.mitee_stats.pyld_chksm_errs
    :field mitee_stats_pyld_avail_errs: ax25_frame.payload.ax25_info.comms.mitee_stats.pyld_avail_errs
    :field mitee_stats_exec_cmds: ax25_frame.payload.ax25_info.comms.mitee_stats.exec_cmds
    :field radio_stats_pkts_tx: ax25_frame.payload.ax25_info.comms.radio_stats.pkts_tx
    :field radio_stats_pkts_rx: ax25_frame.payload.ax25_info.comms.radio_stats.pkts_rx
    :field radio_stats_bytes_tx: ax25_frame.payload.ax25_info.comms.radio_stats.bytes_tx
    :field radio_stats_bytes_rx: ax25_frame.payload.ax25_info.comms.radio_stats.bytes_rx
    :field radio_stats_hdr_chksm_errs: ax25_frame.payload.ax25_info.comms.radio_stats.hdr_chksm_errs
    :field radio_stats_pyld_chksm_errs: ax25_frame.payload.ax25_info.comms.radio_stats.pyld_chksm_errs
    :field radio_stats_pyld_len_errs: ax25_frame.payload.ax25_info.comms.radio_stats.pyld_len_errs
    :field radio_stats_uart_errs: ax25_frame.payload.ax25_info.comms.radio_stats.uart_errs
    :field radio_stats_fail_timeouts: ax25_frame.payload.ax25_info.comms.radio_stats.fail_timeouts
    :field sdep_stats_cmds_tx: ax25_frame.payload.ax25_info.comms.sdep_stats.cmds_tx
    :field sdep_stats_resps_rx: ax25_frame.payload.ax25_info.comms.sdep_stats.resps_rx
    :field sdep_stats_trx_tx: ax25_frame.payload.ax25_info.comms.sdep_stats.trx_tx
    :field sdep_stats_sdep_stats_bytes_tx: ax25_frame.payload.ax25_info.comms.sdep_stats.bytes_tx
    :field sdep_stats_sdep_stats_bytes_rx: ax25_frame.payload.ax25_info.comms.sdep_stats.bytes_rx
    :field sdep_stats_sdep_stats_fail_timeouts: ax25_frame.payload.ax25_info.comms.sdep_stats.fail_timeouts
    :field rst_stats_sat: ax25_frame.payload.ax25_info.comms.rst_stats.sat
    :field rst_stats_comms: ax25_frame.payload.ax25_info.comms.rst_stats.comms
    :field rst_stats_main: ax25_frame.payload.ax25_info.comms.rst_stats.main
    :field radio_cfg_interface_baud_rate: ax25_frame.payload.ax25_info.comms.radio_cfg.interface_baud_rate
    :field radio_cfg_tx_power_amp_level: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_power_amp_level
    :field radio_cfg_rx_rf_baud_rate: ax25_frame.payload.ax25_info.comms.radio_cfg.rx_rf_baud_rate
    :field radio_cfg_tx_rf_baud_rate: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_rf_baud_rate
    :field radio_cfg_rx_modulation: ax25_frame.payload.ax25_info.comms.radio_cfg.rx_modulation
    :field radio_cfg_tx_modulation: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_modulation
    :field radio_cfg_rx_freq: ax25_frame.payload.ax25_info.comms.radio_cfg.rx_freq
    :field radio_cfg_tx_freq: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_freq
    :field radio_cfg_src: ax25_frame.payload.ax25_info.comms.radio_cfg.src
    :field radio_cfg_dst: ax25_frame.payload.ax25_info.comms.radio_cfg.dst
    :field radio_cfg_tx_preamble: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_preamble
    :field radio_cfg_tx_postamble: ax25_frame.payload.ax25_info.comms.radio_cfg.tx_postamble
    :field radio_cfg_function_cfg1: ax25_frame.payload.ax25_info.comms.radio_cfg.function_cfg1
    :field radio_cfg_function_cfg2: ax25_frame.payload.ax25_info.comms.radio_cfg.function_cfg2
    :field radio_bcn_interval: ax25_frame.payload.ax25_info.comms.radio_bcn_interval
    :field radio_tlm_data_op_counter: ax25_frame.payload.ax25_info.comms.radio_tlm_data.op_counter
    :field radio_tlm_data_msp430_temp: ax25_frame.payload.ax25_info.comms.radio_tlm_data.msp430_temp
    :field radio_tlm_data_timecount1: ax25_frame.payload.ax25_info.comms.radio_tlm_data.timecount1
    :field radio_tlm_data_timecount2: ax25_frame.payload.ax25_info.comms.radio_tlm_data.timecount2
    :field radio_tlm_data_timecount3: ax25_frame.payload.ax25_info.comms.radio_tlm_data.timecount3
    :field radio_tlm_data_rssi: ax25_frame.payload.ax25_info.comms.radio_tlm_data.rssi
    :field radio_tlm_data_bytes_rx: ax25_frame.payload.ax25_info.comms.radio_tlm_data.bytes_rx
    :field radio_tlm_data_bytes_tx: ax25_frame.payload.ax25_info.comms.radio_tlm_data.bytes_tx
    :field radio_fw_rev_num: ax25_frame.payload.ax25_info.comms.radio_fw_rev_num
    :field mission_cnt: ax25_frame.payload.ax25_info.comms.mission_cnt
    :field ps_temp: ax25_frame.payload.ax25_info.comms.ps_temp
    :field second: ax25_frame.payload.ax25_info.cdh.datetime.second
    :field minute: ax25_frame.payload.ax25_info.cdh.datetime.minute
    :field hour: ax25_frame.payload.ax25_info.cdh.datetime.hour
    :field day_of_week: ax25_frame.payload.ax25_info.cdh.datetime.day_of_week
    :field day_of_month: ax25_frame.payload.ax25_info.cdh.datetime.day_of_month
    :field month: ax25_frame.payload.ax25_info.cdh.datetime.month
    :field year: ax25_frame.payload.ax25_info.cdh.datetime.year
    :field boot_count: ax25_frame.payload.ax25_info.cdh.boot_count
    :field error_count: ax25_frame.payload.ax25_info.cdh.error_count
    :field error_last: ax25_frame.payload.ax25_info.cdh.error_last
    :field ttc_state: ax25_frame.payload.ax25_info.cdh.ttc_state
    :field ttc_remaining: ax25_frame.payload.ax25_info.cdh.ttc_remaining
    :field ttc_queue_0: ax25_frame.payload.ax25_info.cdh.ttc_queue_0
    :field ttc_queue_1: ax25_frame.payload.ax25_info.cdh.ttc_queue_1
    :field ttc_queue_2: ax25_frame.payload.ax25_info.cdh.ttc_queue_2
    :field ttc_queue_3: ax25_frame.payload.ax25_info.cdh.ttc_queue_3
    :field ttc_queue_4: ax25_frame.payload.ax25_info.cdh.ttc_queue_4
    :field ttc_queue_5: ax25_frame.payload.ax25_info.cdh.ttc_queue_5
    :field ttc_queue_6: ax25_frame.payload.ax25_info.cdh.ttc_queue_6
    :field ttc_queue_7: ax25_frame.payload.ax25_info.cdh.ttc_queue_7
    :field bat_tmp: ax25_frame.payload.ax25_info.eps.bat_tmp
    :field reg_temp_5v: ax25_frame.payload.ax25_info.eps.reg_temp_5v
    :field volt_5v: ax25_frame.payload.ax25_info.eps.volt_5v
    :field volt_digital: ax25_frame.payload.ax25_info.eps.volt_digital
    :field volt_analog: ax25_frame.payload.ax25_info.eps.volt_analog
    :field batt_charge: ax25_frame.payload.ax25_info.eps.batt_charge
    :field batt_load: ax25_frame.payload.ax25_info.eps.batt_load
    :field curr_5v: ax25_frame.payload.ax25_info.eps.curr_5v
    :field curr_digital: ax25_frame.payload.ax25_info.eps.curr_digital
    :field curr_analog: ax25_frame.payload.ax25_info.eps.curr_analog
    :field volt_solar: ax25_frame.payload.ax25_info.eps.volt_solar
    :field volt_batt: ax25_frame.payload.ax25_info.eps.volt_batt
    :field batt_heater: ax25_frame.payload.ax25_info.eps.batt_heater
    :field bdot_on: ax25_frame.payload.ax25_info.adcs.bdot_on
    :field magtorq_x: ax25_frame.payload.ax25_info.adcs.magtorq.force_x
    :field magtorq_y: ax25_frame.payload.ax25_info.adcs.magtorq.force_y
    :field magtorq_z: ax25_frame.payload.ax25_info.adcs.magtorq.force_z
    :field gyro_x: ax25_frame.payload.ax25_info.adcs.imu.gyro_x
    :field gyro_y: ax25_frame.payload.ax25_info.adcs.imu.gyro_y
    :field gyro_z: ax25_frame.payload.ax25_info.adcs.imu.gyro_z
    :field accel_x: ax25_frame.payload.ax25_info.adcs.imu.accel_x
    :field accel_y: ax25_frame.payload.ax25_info.adcs.imu.accel_y
    :field accel_z: ax25_frame.payload.ax25_info.adcs.imu.accel_z
    :field imu_temp: ax25_frame.payload.ax25_info.adcs.imu.temp
    :field pd_top: ax25_frame.payload.ax25_info.adcs.photodiode.pd_top
    :field pd_left: ax25_frame.payload.ax25_info.adcs.photodiode.pd_left
    :field pd_bottom: ax25_frame.payload.ax25_info.adcs.photodiode.pd_bottom
    :field pd_right: ax25_frame.payload.ax25_info.adcs.photodiode.pd_right
    :field magtom_0_x: ax25_frame.payload.ax25_info.adcs.magtom_0.x
    :field magtom_0_y: ax25_frame.payload.ax25_info.adcs.magtom_0.y
    :field magtom_0_z: ax25_frame.payload.ax25_info.adcs.magtom_0.z
    :field magtom_1_x: ax25_frame.payload.ax25_info.adcs.magtom_1.x
    :field magtom_1_y: ax25_frame.payload.ax25_info.adcs.magtom_1.y
    :field magtom_1_z: ax25_frame.payload.ax25_info.adcs.magtom_1.z
    :field magtom_2_x: ax25_frame.payload.ax25_info.adcs.magtom_2.x
    :field magtom_2_y: ax25_frame.payload.ax25_info.adcs.magtom_2.y
    :field magtom_2_z: ax25_frame.payload.ax25_info.adcs.magtom_2.z
    :field pyld_chksm: ax25_frame.payload.ax25_info.pyld_chksm
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Mitee1.Ax25Frame(self._io, self, self._root)

    class MiteeHdr(KaitaiStruct):
        """Currently only considers beacon packets."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sync = self._io.read_bytes(2)
            if not self.sync == b"\x4D\x69":
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x69", self.sync, self._io, u"/types/mitee_hdr/seq/0")
            self.cmd_id = self._io.read_bytes(2)
            if not self.cmd_id == b"\xA0\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA0\x00", self.cmd_id, self._io, u"/types/mitee_hdr/seq/1")
            self.pyld_len = self._io.read_u1()
            self.pkt_no = self._io.read_u1()
            self.pkt_cnt = self._io.read_u1()
            self.grp_no = self._io.read_u1()
            self.grp_size = self._io.read_u1()
            self.status = self._io.read_u1()
            self.hdr_chksm = self._io.read_u2le()


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Mitee1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Mitee1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Mitee1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Mitee1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Mitee1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Mitee1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Mitee1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Mitee1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Mitee1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Mitee1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Mitee1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class AdcsMagtorq(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.force_x = self._io.read_s1()
            self.force_y = self._io.read_s1()
            self.force_z = self._io.read_s1()


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
            self.ax25_info = Mitee1.Ax25Info(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Adcs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bdot_on = self._io.read_u1()
            self.magtorq = Mitee1.AdcsMagtorq(self._io, self, self._root)
            self.imu = Mitee1.AdcsImu(self._io, self, self._root)
            self.photodiode = Mitee1.AdcsPd(self._io, self, self._root)
            self.magtom_0 = Mitee1.AdcsMagtom(self._io, self, self._root)
            self.magtom_1 = Mitee1.AdcsMagtom(self._io, self, self._root)
            self.magtom_2 = Mitee1.AdcsMagtom(self._io, self, self._root)


    class Comms(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mitee_stats = Mitee1.CommsMiteeStats(self._io, self, self._root)
            self.radio_stats = Mitee1.CommsRadioStats(self._io, self, self._root)
            self.sdep_stats = Mitee1.CommsSdepStats(self._io, self, self._root)
            self.rst_stats = Mitee1.CommsRstStats(self._io, self, self._root)
            self.radio_cfg = Mitee1.CommsRadioCfg(self._io, self, self._root)
            self.radio_bcn_interval = self._io.read_u1()
            self.radio_tlm_data = Mitee1.CommsRadioTlmData(self._io, self, self._root)
            self.radio_fw_rev_num = self._io.read_u4le()
            self.mission_cnt = self._io.read_u4le()
            self.ps_temp = self._io.read_u2le()


    class Cdh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.datetime = Mitee1.CdhDatetime(self._io, self, self._root)
            self.boot_count = self._io.read_u2le()
            self.error_count = self._io.read_u4le()
            self.error_last = self._io.read_u1()
            self.ttc_state = self._io.read_u1()
            self.ttc_remaining = self._io.read_u1()
            self.ttc_queue_0 = self._io.read_u1()
            self.ttc_queue_1 = self._io.read_u1()
            self.ttc_queue_2 = self._io.read_u1()
            self.ttc_queue_3 = self._io.read_u1()
            self.ttc_queue_4 = self._io.read_u1()
            self.ttc_queue_5 = self._io.read_u1()
            self.ttc_queue_6 = self._io.read_u1()
            self.ttc_queue_7 = self._io.read_u1()
            self.padding = self._io.read_bytes(1)


    class CommsRadioTlmData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.op_counter = self._io.read_u2le()
            self.msp430_temp = self._io.read_s2le()
            self.timecount1 = self._io.read_u1()
            self.timecount2 = self._io.read_u1()
            self.timecount3 = self._io.read_u1()
            self.rssi = self._io.read_u1()
            self.bytes_rx = self._io.read_u4le()
            self.bytes_tx = self._io.read_u4le()


    class CdhDatetime(KaitaiStruct):
        """Current date and time (0000-01-01 00:00:00 = mission start)."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.second = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.day_of_week = self._io.read_u1()
            self.day_of_month = self._io.read_u1()
            self.month = self._io.read_u1()
            self.year = self._io.read_u2le()


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


    class CommsSdepStats(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmds_tx = self._io.read_u4le()
            self.resps_rx = self._io.read_u4le()
            self.trx_tx = self._io.read_u4le()
            self.bytes_tx = self._io.read_u4le()
            self.bytes_rx = self._io.read_u4le()
            self.fail_timeouts = self._io.read_u2le()


    class CommsMiteeStats(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bcn_tx = self._io.read_u4le()
            self.pkts_tx = self._io.read_u4le()
            self.pkts_rx = self._io.read_u4le()
            self.bytes_tx = self._io.read_u4le()
            self.bytes_rx = self._io.read_u4le()
            self.sync_errs = self._io.read_u2le()
            self.hdr_chksm_errs = self._io.read_u2le()
            self.pyld_chksm_errs = self._io.read_u2le()
            self.pyld_avail_errs = self._io.read_u2le()
            self.exec_cmds = self._io.read_u2le()


    class CommsRadioCfg(KaitaiStruct):
        """Lithium2 radio config."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.interface_baud_rate = self._io.read_u1()
            self.tx_power_amp_level = self._io.read_u1()
            self.rx_rf_baud_rate = self._io.read_u1()
            self.tx_rf_baud_rate = self._io.read_u1()
            self.rx_modulation = self._io.read_u1()
            self.tx_modulation = self._io.read_u1()
            self.rx_freq = self._io.read_u4le()
            self.tx_freq = self._io.read_u4le()
            self.src = (self._io.read_bytes(6)).decode(u"ASCII")
            self.dst = (self._io.read_bytes(6)).decode(u"ASCII")
            self.tx_preamble = self._io.read_u2le()
            self.tx_postamble = self._io.read_u2le()
            self.function_cfg1 = self._io.read_u2le()
            self.function_cfg2 = self._io.read_u2le()


    class AdcsImu(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gyro_x = self._io.read_s2le()
            self.gyro_y = self._io.read_s2le()
            self.gyro_z = self._io.read_s2le()
            self.accel_x = self._io.read_s2le()
            self.accel_y = self._io.read_s2le()
            self.accel_z = self._io.read_s2le()
            self.temp = self._io.read_s2le()


    class Eps(KaitaiStruct):
        """EPS readings. 5V = 2048; 1V/A for current readings unless otherwise specified."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bat_tmp = self._io.read_s2le()
            self.reg_temp_5v = self._io.read_s2le()
            self.volt_5v = self._io.read_s2le()
            self.volt_digital = self._io.read_s2le()
            self.volt_analog = self._io.read_s2le()
            self.batt_charge = self._io.read_s2le()
            self.batt_load = self._io.read_s2le()
            self.curr_5v = self._io.read_s2le()
            self.curr_digital = self._io.read_s2le()
            self.curr_analog = self._io.read_s2le()
            self.volt_solar = self._io.read_s2le()
            self.volt_batt = self._io.read_s2le()
            self.batt_heater = self._io.read_u2le()


    class CommsRadioStats(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pkts_tx = self._io.read_u4le()
            self.pkts_rx = self._io.read_u4le()
            self.bytes_tx = self._io.read_u4le()
            self.bytes_rx = self._io.read_u4le()
            self.hdr_chksm_errs = self._io.read_u2le()
            self.pyld_chksm_errs = self._io.read_u2le()
            self.pyld_len_errs = self._io.read_u2le()
            self.uart_errs = self._io.read_u2le()
            self.fail_timeouts = self._io.read_u2le()


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
            self.callsign_ror = Mitee1.Callsign(_io__raw_callsign_ror, self, self._root)


    class AdcsMagtom(KaitaiStruct):
        """Magentometer axes (1 = 0.92 mGa)."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()


    class CommsRstStats(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sat = self._io.read_u2le()
            self.comms = self._io.read_u2le()
            self.main = self._io.read_u2le()


    class AdcsPd(KaitaiStruct):
        """Under-antenna photodiode raw values."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pd_top = self._io.read_u2le()
            self.pd_left = self._io.read_u2le()
            self.pd_bottom = self._io.read_u2le()
            self.pd_right = self._io.read_u2le()


    class Ax25Info(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mitee_hdr = Mitee1.MiteeHdr(self._io, self, self._root)
            self.comms = Mitee1.Comms(self._io, self, self._root)
            self.cdh = Mitee1.Cdh(self._io, self, self._root)
            self.eps = Mitee1.Eps(self._io, self, self._root)
            self.adcs = Mitee1.Adcs(self._io, self, self._root)
            self.pyld_chksm = self._io.read_u2le()



