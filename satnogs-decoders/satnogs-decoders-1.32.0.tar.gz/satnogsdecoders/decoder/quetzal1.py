# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Quetzal1(KaitaiStruct):
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
    :field cubesat_identifier: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cubesat_identifier
    :field rtc_hh: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_hh
    :field rtc_mm: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_mm
    :field rtc_ss: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_ss
    :field rtc_dd: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_dd
    :field rtc_mo: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_mo
    :field rtc_yy: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.rtc_yy
    :field adm_status: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.adm_status
    :field eps_status: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.eps_status
    :field heater_status: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.heater_status
    :field adcs_status: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.adcs_status
    :field payload_status: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.payload_status
    :field adm_software_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.adm_software_reset_counter
    :field eps_software_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.eps_software_reset_counter
    :field adcs_software_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.adcs_software_reset_counter
    :field adcs_hardware_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.adcs_hardware_reset_counter
    :field comms_hardware_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.comms_hardware_reset_counter
    :field cdhs_reset_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.cdhs.cdhs_reset_counter
    :field tmp100_temp1: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.tmp100_temp1
    :field bq1_soc: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_soc
    :field bq1_bat_volt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_bat_volt
    :field bq1_avg_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_avg_cur
    :field bq1_remaining_capacity: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_remaining_capacity
    :field bq1_avg_power: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_avg_power
    :field bq1_state_of_health: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.bq1_state_of_health
    :field ina1_ch1_volt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina1_ch1_volt
    :field ina1_ch1_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina1_ch1_cur
    :field ina2_ch2_volt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina2_ch2_volt
    :field ina2_ch2_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina2_ch2_cur
    :field ina3_ch3_volt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina3_ch3_volt
    :field ina3_ch3_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.ina3_ch3_cur
    :field fpb_adcs_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.fpb_adcs_cur
    :field fpb_comms_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.fpb_comms_cur
    :field fpb_payload_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.fpb_payload_cur
    :field fpb_heater_cur: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.fpb_heater_cur
    :field fault_flags: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.fault_flags
    :field general_comm_flag: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.general_comm_flag
    :field general_trans_flag: ax25_frame.payload.ax25_info.csp_node.csp_node_port.eps.general_trans_flag
    :field bno055_temp: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.bno055_temp
    :field cs_adcs_temp_tmp100: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.cs_adcs_temp_tmp100
    :field general_trans_flags: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.general_trans_flags
    :field cs_orientation_gyro: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.cs_orientation_gyro
    :field cs_orientation_magneto: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.cs_orientation_magneto
    :field cs_orientation_adc1: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.cs_orientation_adc1
    :field cs_orientation_adc2: ax25_frame.payload.ax25_info.csp_node.csp_node_port.adcs.cs_orientation_adc2
    :field package_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.comm.package_counter
    :field operation_mode: ax25_frame.payload.ax25_info.csp_node.csp_node_port.payload.operation_mode
    :field camera_picture_counter: ax25_frame.payload.ax25_info.csp_node.csp_node_port.payload.camera_picture_counter
    :field cdhs_cycle_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.cdhs_cycle_time
    :field cdhs_wdt: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.cdhs_wdt
    :field adm_soc_limit: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_soc_limit
    :field adcs_soc_limit: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adcs_soc_limit
    :field comms_soc_limit: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.comms_soc_limit
    :field payload_soc_limit: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.payload_soc_limit
    :field heater_cycle_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.heater_cycle_time
    :field heater_emergency_on_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.heater_emergency_on_time
    :field heater_emergency_off_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.heater_emergency_off_time
    :field adm_cycle_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_cycle_time
    :field adm_burn_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_burn_time
    :field adm_max_cycles: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_max_cycles
    :field adm_wait_time_1: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_wait_time_1
    :field adm_wait_time_2: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_wait_time_2
    :field adm_enable: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.adm_enable
    :field comms_cycle_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.comms_cycle_time
    :field payload_cycle_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.payload_cycle_time
    :field payload_operation_mode: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.payload_operation_mode
    :field camera_resolution: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.camera_resolution
    :field camera_exposition: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.camera_exposition
    :field camera_picture_save_time: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.camera_picture_save_time
    :field payload_enable: ax25_frame.payload.ax25_info.csp_node.csp_node_port.ram_params.payload_enable
    :field uvg_msg: ax25_frame.payload.ax25_info.csp_node.csp_node_port.uvg_msg.uvg_msg
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
        self.ax25_frame = Quetzal1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Quetzal1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Quetzal1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Quetzal1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Quetzal1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Quetzal1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Quetzal1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Quetzal1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Quetzal1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Quetzal1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Quetzal1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Quetzal1.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Quetzal1.Repeater(self._io, self, self._root)

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
            self.ax25_info = Quetzal1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class UvgMsgT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.uvg_msg = (self._io.read_bytes(27)).decode(u"ASCII")


    class EpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tmp100_temp1 = self._io.read_u1()
            self.bq1_soc = self._io.read_u1()
            self.bq1_bat_volt = self._io.read_u1()
            self.bq1_avg_cur = self._io.read_u2be()
            self.bq1_remaining_capacity = self._io.read_u2be()
            self.bq1_avg_power = self._io.read_u2be()
            self.bq1_state_of_health = self._io.read_u1()
            self.ina1_ch1_volt = self._io.read_u1()
            self.ina1_ch1_cur = self._io.read_u2be()
            self.ina2_ch2_volt = self._io.read_u1()
            self.ina2_ch2_cur = self._io.read_u2be()
            self.ina3_ch3_volt = self._io.read_u1()
            self.ina3_ch3_cur = self._io.read_u2be()
            self.fpb_adcs_cur = self._io.read_u2be()
            self.fpb_comms_cur = self._io.read_u2be()
            self.fpb_payload_cur = self._io.read_u2be()
            self.fpb_heater_cur = self._io.read_u2be()
            self.fault_flags = self._io.read_u1()
            self.general_comm_flag = self._io.read_u1()
            self.general_trans_flag = self._io.read_u1()


    class CommT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.package_counter = self._io.read_u4be()


    class AdcsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cs_orientation_gyro_arr = [None] * (3)
            for i in range(3):
                self.cs_orientation_gyro_arr[i] = self._io.read_u1()

            self.cs_orientation_magneto_arr = [None] * (6)
            for i in range(6):
                self.cs_orientation_magneto_arr[i] = self._io.read_u1()

            self.cs_orientation_adc1_arr = [None] * (6)
            for i in range(6):
                self.cs_orientation_adc1_arr[i] = self._io.read_u1()

            self.cs_orientation_adc2_arr = [None] * (6)
            for i in range(6):
                self.cs_orientation_adc2_arr[i] = self._io.read_u1()

            self.bno055_temp = self._io.read_s1()
            self.cs_adcs_temp_tmp100 = self._io.read_s2be()
            self.general_trans_flags = self._io.read_u1()

        @property
        def cs_orientation_gyro(self):
            if hasattr(self, '_m_cs_orientation_gyro'):
                return self._m_cs_orientation_gyro if hasattr(self, '_m_cs_orientation_gyro') else None

            self._m_cs_orientation_gyro = (((self.cs_orientation_gyro_arr[0] << 16) | (self.cs_orientation_gyro_arr[1] << 8)) | self.cs_orientation_gyro_arr[2])
            return self._m_cs_orientation_gyro if hasattr(self, '_m_cs_orientation_gyro') else None

        @property
        def cs_orientation_magneto(self):
            if hasattr(self, '_m_cs_orientation_magneto'):
                return self._m_cs_orientation_magneto if hasattr(self, '_m_cs_orientation_magneto') else None

            self._m_cs_orientation_magneto = ((((((self.cs_orientation_magneto_arr[0] << 40) | (self.cs_orientation_magneto_arr[1] << 32)) | (self.cs_orientation_magneto_arr[2] << 24)) | (self.cs_orientation_magneto_arr[3] << 16)) | (self.cs_orientation_magneto_arr[4] << 8)) | self.cs_orientation_magneto_arr[5])
            return self._m_cs_orientation_magneto if hasattr(self, '_m_cs_orientation_magneto') else None

        @property
        def cs_orientation_adc1(self):
            if hasattr(self, '_m_cs_orientation_adc1'):
                return self._m_cs_orientation_adc1 if hasattr(self, '_m_cs_orientation_adc1') else None

            self._m_cs_orientation_adc1 = ((((((self.cs_orientation_adc1_arr[0] << 40) | (self.cs_orientation_adc1_arr[1] << 32)) | (self.cs_orientation_adc1_arr[2] << 24)) | (self.cs_orientation_adc1_arr[3] << 16)) | (self.cs_orientation_adc1_arr[4] << 8)) | self.cs_orientation_adc1_arr[5])
            return self._m_cs_orientation_adc1 if hasattr(self, '_m_cs_orientation_adc1') else None

        @property
        def cs_orientation_adc2(self):
            if hasattr(self, '_m_cs_orientation_adc2'):
                return self._m_cs_orientation_adc2 if hasattr(self, '_m_cs_orientation_adc2') else None

            self._m_cs_orientation_adc2 = ((((((self.cs_orientation_adc2_arr[0] << 40) | (self.cs_orientation_adc2_arr[1] << 32)) | (self.cs_orientation_adc2_arr[2] << 24)) | (self.cs_orientation_adc2_arr[3] << 16)) | (self.cs_orientation_adc2_arr[4] << 8)) | self.cs_orientation_adc2_arr[5])
            return self._m_cs_orientation_adc2 if hasattr(self, '_m_cs_orientation_adc2') else None


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cubesat_identifier_magic = self._io.read_bytes(8)
            if not self.cubesat_identifier_magic == b"\x51\x55\x45\x54\x5A\x41\x4C\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x51\x55\x45\x54\x5A\x41\x4C\x31", self.cubesat_identifier_magic, self._io, u"/types/beacon_t/seq/0")
            self.cdhs = Quetzal1.CdhsT(self._io, self, self._root)
            self.eps = Quetzal1.EpsT(self._io, self, self._root)
            self.adcs = Quetzal1.AdcsT(self._io, self, self._root)
            self.comm = Quetzal1.CommT(self._io, self, self._root)
            self.payload = Quetzal1.PayloadT(self._io, self, self._root)
            self.ram_params = Quetzal1.RamParamsT(self._io, self, self._root)
            self.uvg_msg = Quetzal1.UvgMsgT(self._io, self, self._root)

        @property
        def cubesat_identifier(self):
            if hasattr(self, '_m_cubesat_identifier'):
                return self._m_cubesat_identifier if hasattr(self, '_m_cubesat_identifier') else None

            _pos = self._io.pos()
            self._io.seek(4)
            self._m_cubesat_identifier = (self._io.read_bytes(8)).decode(u"ASCII")
            self._io.seek(_pos)
            return self._m_cubesat_identifier if hasattr(self, '_m_cubesat_identifier') else None


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
            self.ax25_info = Quetzal1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
            self.operation_mode = self._io.read_u1()
            self.camera_picture_counter = self._io.read_u2be()


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Quetzal1.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Quetzal1.SsidMask(self._io, self, self._root)


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
                _ = Quetzal1.Repeaters(self._io, self, self._root)
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
                self.csp_node_port = Quetzal1.Ax100ControlPortT(self._io, self, self._root)


    class CdhsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtc_hh = self._io.read_u1()
            self.rtc_mm = self._io.read_u1()
            self.rtc_ss = self._io.read_u1()
            self.rtc_dd = self._io.read_u1()
            self.rtc_mo = self._io.read_u1()
            self.rtc_yy = self._io.read_u1()
            self.adm_status = self._io.read_u1()
            self.eps_status = self._io.read_u1()
            self.heater_status = self._io.read_u1()
            self.adcs_status = self._io.read_u1()
            self.payload_status = self._io.read_u1()
            self.adm_software_reset_counter = self._io.read_u1()
            self.eps_software_reset_counter = self._io.read_u1()
            self.adcs_software_reset_counter = self._io.read_u1()
            self.adcs_hardware_reset_counter = self._io.read_u1()
            self.comms_hardware_reset_counter = self._io.read_u1()
            self.cdhs_reset_counter = self._io.read_u2be()


    class ObcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_node_port = Quetzal1.BeaconT(self._io, self, self._root)


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
            self.callsign_ror = Quetzal1.Callsign(_io__raw_callsign_ror, self, self._root)


    class RamParamsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cdhs_cycle_time = self._io.read_u1()
            self.cdhs_wdt = self._io.read_u1()
            self.adm_soc_limit = self._io.read_u1()
            self.adcs_soc_limit = self._io.read_u1()
            self.comms_soc_limit = self._io.read_u1()
            self.payload_soc_limit = self._io.read_u1()
            self.heater_cycle_time = self._io.read_u1()
            self.heater_emergency_on_time = self._io.read_u1()
            self.heater_emergency_off_time = self._io.read_u1()
            self.adm_cycle_time = self._io.read_u1()
            self.adm_burn_time = self._io.read_u1()
            self.adm_max_cycles = self._io.read_u1()
            self.adm_wait_time_1 = self._io.read_u1()
            self.adm_wait_time_2 = self._io.read_u1()
            self.adm_enable = self._io.read_u1()
            self.comms_cycle_time = self._io.read_u1()
            self.payload_cycle_time = self._io.read_u1()
            self.payload_operation_mode = self._io.read_u1()
            self.camera_resolution = self._io.read_u1()
            self.camera_exposition = self._io.read_u1()
            self.camera_picture_save_time = self._io.read_u1()
            self.payload_enable = self._io.read_u1()


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = Quetzal1.CspHeaderT(self._io, self, self._root)
            _on = self.csp_header.source
            if _on == 1:
                self.csp_node = Quetzal1.ObcT(self._io, self, self._root)
            elif _on == 5:
                self.csp_node = Quetzal1.Ax100T(self._io, self, self._root)



