# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cas9(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_identifier: ax25_frame.payload.ax25_info.packet_identifier
    :field sat_time_year: ax25_frame.payload.ax25_info.cas9_payload.sat_time.year
    :field sat_time_month: ax25_frame.payload.ax25_info.cas9_payload.sat_time.month
    :field sat_time_day: ax25_frame.payload.ax25_info.cas9_payload.sat_time.day
    :field sat_time_hour: ax25_frame.payload.ax25_info.cas9_payload.sat_time.hour
    :field sat_time_minute: ax25_frame.payload.ax25_info.cas9_payload.sat_time.minute
    :field sat_time_second: ax25_frame.payload.ax25_info.cas9_payload.sat_time.second
    :field reset_time_year: ax25_frame.payload.ax25_info.cas9_payload.reset_time.year
    :field reset_time_month: ax25_frame.payload.ax25_info.cas9_payload.reset_time.month
    :field reset_time_day: ax25_frame.payload.ax25_info.cas9_payload.reset_time.day
    :field reset_time_hour: ax25_frame.payload.ax25_info.cas9_payload.reset_time.hour
    :field reset_time_minute: ax25_frame.payload.ax25_info.cas9_payload.reset_time.minute
    :field reset_time_second: ax25_frame.payload.ax25_info.cas9_payload.reset_time.second
    :field total_reset_counter: ax25_frame.payload.ax25_info.cas9_payload.total_reset_counter
    :field tft_counter: ax25_frame.payload.ax25_info.cas9_payload.tft_counter
    :field rcfr_counter: ax25_frame.payload.ax25_info.cas9_payload.rcfr_counter
    :field rcce_counter: ax25_frame.payload.ax25_info.cas9_payload.rcce_counter
    :field rccf_counter: ax25_frame.payload.ax25_info.cas9_payload.rccf_counter
    :field wdg_switch_status: ax25_frame.payload.ax25_info.cas9_payload.wdg_switch_status
    :field cpu_io_aqu_wdg_reset_counter: ax25_frame.payload.ax25_info.cas9_payload.cpu_io_aqu_wdg_reset_counter
    :field adc_sw_wdg_reset_counter: ax25_frame.payload.ax25_info.cas9_payload.adc_sw_wdg_reset_counter
    :field tmp_meas_sw_wdg_reset_counter: ax25_frame.payload.ax25_info.cas9_payload.tmp_meas_sw_wdg_reset_counter
    :field rem_ctrl_sw_wdg_reset_counter: ax25_frame.payload.ax25_info.cas9_payload.rem_ctrl_sw_wdg_reset_counter
    :field working_status_1: ax25_frame.payload.ax25_info.cas9_payload.working_status_1
    :field working_status_2: ax25_frame.payload.ax25_info.cas9_payload.working_status_2
    :field working_status_3: ax25_frame.payload.ax25_info.cas9_payload.working_status_3
    :field pwr_supply_voltage: ax25_frame.payload.ax25_info.cas9_payload.pwr_supply_voltage_12v.w1w2
    :field vu_12v_power_supply_current: ax25_frame.payload.ax25_info.cas9_payload.vu_12v_power_supply_current
    :field vu_5v_power_supply_voltage: ax25_frame.payload.ax25_info.cas9_payload.vu_5v_power_supply_voltage.w1w2
    :field vu_3v8_power_supply_voltage: ax25_frame.payload.ax25_info.cas9_payload.vu_3v8_power_supply_voltage.w1w2
    :field ihu_3v3_voltage_1: ax25_frame.payload.ax25_info.cas9_payload.ihu_3v3_voltage_1.w1w2
    :field ihu_3v3_voltage_2: ax25_frame.payload.ax25_info.cas9_payload.ihu_3v3_voltage_2.w1w2
    :field ihu_3v8_current: ax25_frame.payload.ax25_info.cas9_payload.ihu_3v8_current
    :field uhf_transmitter_3v8_current: ax25_frame.payload.ax25_info.cas9_payload.uhf_transmitter_3v8_current
    :field vhf_receiver_3v8_current: ax25_frame.payload.ax25_info.cas9_payload.vhf_receiver_3v8_current
    :field vhf_agc_voltage: ax25_frame.payload.ax25_info.cas9_payload.vhf_agc_voltage.w1w2
    :field rf_transmit_power: ax25_frame.payload.ax25_info.cas9_payload.rf_transmit_power
    :field rf_reflected_power: ax25_frame.payload.ax25_info.cas9_payload.rf_reflected_power
    :field thermoelectric_generator_voltage_1: ax25_frame.payload.ax25_info.cas9_payload.thermoelectric_generator_voltage_1.w1w2
    :field thermoelectric_generator_voltage_2: ax25_frame.payload.ax25_info.cas9_payload.thermoelectric_generator_voltage_2.w1w2
    :field uhf_transmitter_pa_temperature: ax25_frame.payload.ax25_info.cas9_payload.uhf_transmitter_pa_temperature
    :field vhf_receiver_temperature: ax25_frame.payload.ax25_info.cas9_payload.vhf_receiver_temperature
    :field ihu_temperature: ax25_frame.payload.ax25_info.cas9_payload.ihu_temperature
    :field thermoelectric_generator_temperature_1: ax25_frame.payload.ax25_info.cas9_payload.thermoelectric_generator_temperature_1
    :field thermoelectric_generator_temperature_2: ax25_frame.payload.ax25_info.cas9_payload.thermoelectric_generator_temperature_2
    :field current_delay_telemetry_interval_hour: ax25_frame.payload.ax25_info.cas9_payload.current_delay_telemetry_interval.hour
    :field current_delay_telemetry_interval_minute: ax25_frame.payload.ax25_info.cas9_payload.current_delay_telemetry_interval.minute
    :field current_delay_telemetry_interval_second: ax25_frame.payload.ax25_info.cas9_payload.current_delay_telemetry_interval.second
    :field delay_telemetry_start_time_setting_year: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.year
    :field delay_telemetry_start_time_setting_month: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.month
    :field delay_telemetry_start_time_setting_day: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.day
    :field delay_telemetry_start_time_setting_hour: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.hour
    :field delay_telemetry_start_time_setting_minute: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.minute
    :field delay_telemetry_start_time_setting_second: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_start_time_setting.second
    :field delay_telemetry_interval_setting_hour: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_interval_setting.hour
    :field delay_telemetry_interval_setting_minute: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_interval_setting.minute
    :field delay_telemetry_interval_setting_second: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_interval_setting.second
    :field delay_telemetry_times_setting_delay_time: ax25_frame.payload.ax25_info.cas9_payload.delay_telemetry_times_setting.delay_time
    :field attitude_quaternion_q0: ax25_frame.payload.ax25_info.cas9_payload.attitude_quaternion_q0.q
    :field attitude_quaternion_q1: ax25_frame.payload.ax25_info.cas9_payload.attitude_quaternion_q1.q
    :field attitude_quaternion_q2: ax25_frame.payload.ax25_info.cas9_payload.attitude_quaternion_q2.q
    :field attitude_quaternion_q3: ax25_frame.payload.ax25_info.cas9_payload.attitude_quaternion_q3.q
    :field x_axis_angular_speed: ax25_frame.payload.ax25_info.cas9_payload.x_axis_angular_speed.w
    :field y_axis_angular_speed: ax25_frame.payload.ax25_info.cas9_payload.y_axis_angular_speed.w
    :field z_axis_angular_speed: ax25_frame.payload.ax25_info.cas9_payload.z_axis_angular_speed.w
    :field satellite_time_uptime: ax25_frame.payload.ax25_info.cas9_payload.satellite_time_seconds.sat_uptime
    :field satellite_time_milliseconds: ax25_frame.payload.ax25_info.cas9_payload.satellite_time_milliseconds
    :field primary_bus_voltage: ax25_frame.payload.ax25_info.cas9_payload.primary_bus_voltage.w1w2
    :field load_total_current: ax25_frame.payload.ax25_info.cas9_payload.load_total_current.w1w2
    :field solar_array_current: ax25_frame.payload.ax25_info.cas9_payload.solar_array_current.w1w2
    :field battery_charging_current: ax25_frame.payload.ax25_info.cas9_payload.battery_charging_current.w1w2
    :field battery_discharge_current: ax25_frame.payload.ax25_info.cas9_payload.battery_discharge_current.w1w2
    :field pos_5v3_supply_voltage: ax25_frame.payload.ax25_info.cas9_payload.pos_5v3_supply_voltage.w1w2
    :field attitude_control_mode: ax25_frame.payload.ax25_info.cas9_payload.attitude_control_mode
    :field satellite_longitude: ax25_frame.payload.ax25_info.cas9_payload.satellite_longitude
    :field satellite_latitude: ax25_frame.payload.ax25_info.cas9_payload.satellite_latitude
    :field rolling_angle_estimation: ax25_frame.payload.ax25_info.cas9_payload.rolling_angle_estimation
    :field pitch_angle_estimation: ax25_frame.payload.ax25_info.cas9_payload.pitch_angle_estimation
    :field yaw_angle_estimation: ax25_frame.payload.ax25_info.cas9_payload.yaw_angle_estimation
    :field uplink_remote_control_data_block_counter: ax25_frame.payload.ax25_info.cas9_payload.uplink_remote_control_data_block_counter
    :field x_band_transceiver_working_status: ax25_frame.payload.ax25_info.cas9_payload.x_band_transceiver_working_status
    :field x_band_transceiver_agc_voltage: ax25_frame.payload.ax25_info.cas9_payload.x_band_transceiver_agc_voltage.w1w2
    :field x_band_transceiver_transmit_power_level: ax25_frame.payload.ax25_info.cas9_payload.x_band_transceiver_transmit_power_level.w1w2
    :field x_band_transceiver_spi_interface_status: ax25_frame.payload.ax25_info.cas9_payload.x_band_transceiver_spi_interface_status
    :field article_1_year: ax25_frame.payload.ax25_info.cas9_payload.article_1.year
    :field article_1_month: ax25_frame.payload.ax25_info.cas9_payload.article_1.month
    :field article_1_day: ax25_frame.payload.ax25_info.cas9_payload.article_1.day
    :field article_1_hour: ax25_frame.payload.ax25_info.cas9_payload.article_1.hour
    :field article_1_minute: ax25_frame.payload.ax25_info.cas9_payload.article_1.minute
    :field article_1_second: ax25_frame.payload.ax25_info.cas9_payload.article_1.second
    :field article_1_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_1.cam_id
    :field article_1_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_1.photo_counter
    :field article_2_year: ax25_frame.payload.ax25_info.cas9_payload.article_2.year
    :field article_2_month: ax25_frame.payload.ax25_info.cas9_payload.article_2.month
    :field article_2_day: ax25_frame.payload.ax25_info.cas9_payload.article_2.day
    :field article_2_hour: ax25_frame.payload.ax25_info.cas9_payload.article_2.hour
    :field article_2_minute: ax25_frame.payload.ax25_info.cas9_payload.article_2.minute
    :field article_2_second: ax25_frame.payload.ax25_info.cas9_payload.article_2.second
    :field article_2_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_2.cam_id
    :field article_2_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_2.photo_counter
    :field article_3_year: ax25_frame.payload.ax25_info.cas9_payload.article_3.year
    :field article_3_month: ax25_frame.payload.ax25_info.cas9_payload.article_3.month
    :field article_3_day: ax25_frame.payload.ax25_info.cas9_payload.article_3.day
    :field article_3_hour: ax25_frame.payload.ax25_info.cas9_payload.article_3.hour
    :field article_3_minute: ax25_frame.payload.ax25_info.cas9_payload.article_3.minute
    :field article_3_second: ax25_frame.payload.ax25_info.cas9_payload.article_3.second
    :field article_3_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_3.cam_id
    :field article_3_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_3.photo_counter
    :field article_4_year: ax25_frame.payload.ax25_info.cas9_payload.article_4.year
    :field article_4_month: ax25_frame.payload.ax25_info.cas9_payload.article_4.month
    :field article_4_day: ax25_frame.payload.ax25_info.cas9_payload.article_4.day
    :field article_4_hour: ax25_frame.payload.ax25_info.cas9_payload.article_4.hour
    :field article_4_minute: ax25_frame.payload.ax25_info.cas9_payload.article_4.minute
    :field article_4_second: ax25_frame.payload.ax25_info.cas9_payload.article_4.second
    :field article_4_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_4.cam_id
    :field article_4_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_4.photo_counter
    :field article_5_year: ax25_frame.payload.ax25_info.cas9_payload.article_5.year
    :field article_5_month: ax25_frame.payload.ax25_info.cas9_payload.article_5.month
    :field article_5_day: ax25_frame.payload.ax25_info.cas9_payload.article_5.day
    :field article_5_hour: ax25_frame.payload.ax25_info.cas9_payload.article_5.hour
    :field article_5_minute: ax25_frame.payload.ax25_info.cas9_payload.article_5.minute
    :field article_5_second: ax25_frame.payload.ax25_info.cas9_payload.article_5.second
    :field article_5_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_5.cam_id
    :field article_5_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_5.photo_counter
    :field article_6_year: ax25_frame.payload.ax25_info.cas9_payload.article_6.year
    :field article_6_month: ax25_frame.payload.ax25_info.cas9_payload.article_6.month
    :field article_6_day: ax25_frame.payload.ax25_info.cas9_payload.article_6.day
    :field article_6_hour: ax25_frame.payload.ax25_info.cas9_payload.article_6.hour
    :field article_6_minute: ax25_frame.payload.ax25_info.cas9_payload.article_6.minute
    :field article_6_second: ax25_frame.payload.ax25_info.cas9_payload.article_6.second
    :field article_6_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_6.cam_id
    :field article_6_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_6.photo_counter
    :field article_7_year: ax25_frame.payload.ax25_info.cas9_payload.article_7.year
    :field article_7_month: ax25_frame.payload.ax25_info.cas9_payload.article_7.month
    :field article_7_day: ax25_frame.payload.ax25_info.cas9_payload.article_7.day
    :field article_7_hour: ax25_frame.payload.ax25_info.cas9_payload.article_7.hour
    :field article_7_minute: ax25_frame.payload.ax25_info.cas9_payload.article_7.minute
    :field article_7_second: ax25_frame.payload.ax25_info.cas9_payload.article_7.second
    :field article_7_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_7.cam_id
    :field article_7_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_7.photo_counter
    :field article_8_year: ax25_frame.payload.ax25_info.cas9_payload.article_8.year
    :field article_8_month: ax25_frame.payload.ax25_info.cas9_payload.article_8.month
    :field article_8_day: ax25_frame.payload.ax25_info.cas9_payload.article_8.day
    :field article_8_hour: ax25_frame.payload.ax25_info.cas9_payload.article_8.hour
    :field article_8_minute: ax25_frame.payload.ax25_info.cas9_payload.article_8.minute
    :field article_8_second: ax25_frame.payload.ax25_info.cas9_payload.article_8.second
    :field article_8_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_8.cam_id
    :field article_8_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_8.photo_counter
    :field article_9_year: ax25_frame.payload.ax25_info.cas9_payload.article_9.year
    :field article_9_month: ax25_frame.payload.ax25_info.cas9_payload.article_9.month
    :field article_9_day: ax25_frame.payload.ax25_info.cas9_payload.article_9.day
    :field article_9_hour: ax25_frame.payload.ax25_info.cas9_payload.article_9.hour
    :field article_9_minute: ax25_frame.payload.ax25_info.cas9_payload.article_9.minute
    :field article_9_second: ax25_frame.payload.ax25_info.cas9_payload.article_9.second
    :field article_9_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_9.cam_id
    :field article_9_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_9.photo_counter
    :field article_10_year: ax25_frame.payload.ax25_info.cas9_payload.article_10.year
    :field article_10_month: ax25_frame.payload.ax25_info.cas9_payload.article_10.month
    :field article_10_day: ax25_frame.payload.ax25_info.cas9_payload.article_10.day
    :field article_10_hour: ax25_frame.payload.ax25_info.cas9_payload.article_10.hour
    :field article_10_minute: ax25_frame.payload.ax25_info.cas9_payload.article_10.minute
    :field article_10_second: ax25_frame.payload.ax25_info.cas9_payload.article_10.second
    :field article_10_cam_id: ax25_frame.payload.ax25_info.cas9_payload.article_10.cam_id
    :field article_10_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.article_10.photo_counter
    :field photo_information_year: ax25_frame.payload.ax25_info.cas9_payload.photo_information.year
    :field photo_information_month: ax25_frame.payload.ax25_info.cas9_payload.photo_information.month
    :field photo_information_day: ax25_frame.payload.ax25_info.cas9_payload.photo_information.day
    :field photo_information_hour: ax25_frame.payload.ax25_info.cas9_payload.photo_information.hour
    :field photo_information_minute: ax25_frame.payload.ax25_info.cas9_payload.photo_information.minute
    :field photo_information_second: ax25_frame.payload.ax25_info.cas9_payload.photo_information.second
    :field photo_information_cam_id: ax25_frame.payload.ax25_info.cas9_payload.photo_information.cam_id
    :field photo_information_photo_counter: ax25_frame.payload.ax25_info.cas9_payload.photo_information.photo_counter
    :field photo_specs: ax25_frame.payload.ax25_info.cas9_payload.photo_specs
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Cas9.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Cas9.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Cas9.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Cas9.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Cas9.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Cas9.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Cas9.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Cas9.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Cas9.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Cas9.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Cas9.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Cas9.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Cas9.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CAS9  ") or (self.callsign == u"CQ    ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class AngularSpeedT(KaitaiStruct):
        """[X..Z]-axis angular speed
        W1W2:W_L W_H W=((W_H<<8)|W_L)/32768*2000(°/s)
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.w_l = self._io.read_u1()
            self.w_h = self._io.read_u1()

        @property
        def w(self):
            if hasattr(self, '_m_w'):
                return self._m_w if hasattr(self, '_m_w') else None

            self._m_w = ((((self.w_h << 8) | self.w_l) / 32768.0) * 2000.0)
            return self._m_w if hasattr(self, '_m_w') else None


    class SatIntervalT(KaitaiStruct):
        """W1-Hour: 00~23, representing 0:00~23:00
        W2-Minute: 00~59, representing 0 minute~59 minutes
        W3-second: 00~59, representing 0 second~59 seconds
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()


    class IntToDecimals1T(KaitaiStruct):
        """W1 is the integer part, W2 is the decimal part (1 decimal place)
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.w1 = self._io.read_u1()
            self.w2 = self._io.read_u1()

        @property
        def w1w2(self):
            if hasattr(self, '_m_w1w2'):
                return self._m_w1w2 if hasattr(self, '_m_w1w2') else None

            self._m_w1w2 = (((self.w1 * 10) + self.w2) / 10.0)
            return self._m_w1w2 if hasattr(self, '_m_w1w2') else None


    class Cas9TelemetryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.function_code = self._io.read_bytes(6)
            if not self.function_code == b"\x00\x01\x00\x01\x00\x7E":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x01\x00\x01\x00\x7E", self.function_code, self._io, u"/types/cas9_telemetry_t/seq/0")
            self.sat_time = Cas9.SatTimeT(self._io, self, self._root)
            self.reset_time = Cas9.SatTimeT(self._io, self, self._root)
            self.total_reset_counter = self._io.read_u1()
            self.tft_counter = self._io.read_u1()
            self.rcfr_counter = self._io.read_u1()
            self.rcce_counter = self._io.read_u1()
            self.rccf_counter = self._io.read_u1()
            self.wdg_switch_status = self._io.read_u1()
            self.cpu_io_aqu_wdg_reset_counter = self._io.read_u1()
            self.adc_sw_wdg_reset_counter = self._io.read_u1()
            self.tmp_meas_sw_wdg_reset_counter = self._io.read_u1()
            self.rem_ctrl_sw_wdg_reset_counter = self._io.read_u1()
            self.working_status_1 = self._io.read_u1()
            self.working_status_2 = self._io.read_u1()
            self.working_status_3 = self._io.read_u1()
            self.pwr_supply_voltage_12v = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.vu_12v_power_supply_current = self._io.read_u2be()
            self.vu_5v_power_supply_voltage = Cas9.IntToDecimals2T(self._io, self, self._root)
            self.vu_3v8_power_supply_voltage = Cas9.IntToDecimals2T(self._io, self, self._root)
            self.ihu_3v3_voltage_1 = Cas9.IntToDecimals2T(self._io, self, self._root)
            self.ihu_3v3_voltage_2 = Cas9.IntToDecimals2T(self._io, self, self._root)
            self.ihu_3v8_current = self._io.read_u2be()
            self.uhf_transmitter_3v8_current = self._io.read_u2be()
            self.vhf_receiver_3v8_current = self._io.read_u2be()
            self.vhf_agc_voltage = Cas9.IntToDecimals2T(self._io, self, self._root)
            self.rf_transmit_power = self._io.read_u2be()
            self.rf_reflected_power = self._io.read_u2be()
            self.thermoelectric_generator_voltage_1 = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.thermoelectric_generator_voltage_2 = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.uhf_transmitter_pa_temperature = self._io.read_s1()
            self.vhf_receiver_temperature = self._io.read_s1()
            self.ihu_temperature = self._io.read_s1()
            self.thermoelectric_generator_temperature_1 = self._io.read_s1()
            self.thermoelectric_generator_temperature_2 = self._io.read_s1()
            self.current_delay_telemetry_interval = Cas9.SatIntervalT(self._io, self, self._root)
            self.delay_telemetry_start_time_setting = Cas9.SatTimeT(self._io, self, self._root)
            self.delay_telemetry_interval_setting = Cas9.SatIntervalT(self._io, self, self._root)
            self.delay_telemetry_times_setting = Cas9.DelayTimesT(self._io, self, self._root)
            self.attitude_quaternion_q0 = Cas9.AttQuaternionT(self._io, self, self._root)
            self.attitude_quaternion_q1 = Cas9.AttQuaternionT(self._io, self, self._root)
            self.attitude_quaternion_q2 = Cas9.AttQuaternionT(self._io, self, self._root)
            self.attitude_quaternion_q3 = Cas9.AttQuaternionT(self._io, self, self._root)
            self.x_axis_angular_speed = Cas9.AngularSpeedT(self._io, self, self._root)
            self.y_axis_angular_speed = Cas9.AngularSpeedT(self._io, self, self._root)
            self.z_axis_angular_speed = Cas9.AngularSpeedT(self._io, self, self._root)
            self.satellite_time_seconds = Cas9.SatTimeSecondsT(self._io, self, self._root)
            self.satellite_time_milliseconds = self._io.read_u2be()
            self.primary_bus_voltage = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.load_total_current = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.solar_array_current = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.battery_charging_current = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.battery_discharge_current = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.pos_5v3_supply_voltage = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.attitude_control_mode = self._io.read_u1()
            self.satellite_longitude = self._io.read_s1()
            self.satellite_latitude = self._io.read_s1()
            self.rolling_angle_estimation = self._io.read_s1()
            self.pitch_angle_estimation = self._io.read_s1()
            self.yaw_angle_estimation = self._io.read_s1()
            self.uplink_remote_control_data_block_counter = self._io.read_u2be()
            self.x_band_transceiver_working_status = self._io.read_u1()
            self.x_band_transceiver_agc_voltage = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.x_band_transceiver_transmit_power_level = Cas9.IntToDecimals1T(self._io, self, self._root)
            self.x_band_transceiver_spi_interface_status = self._io.read_u1()


    class AttQuaternionT(KaitaiStruct):
        """Attitude quaternion q[0..3]
        q[0..3]=((Q_H<<8)|Q_L)/32768
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.q_l = self._io.read_u1()
            self.q_h = self._io.read_u1()

        @property
        def q(self):
            if hasattr(self, '_m_q'):
                return self._m_q if hasattr(self, '_m_q') else None

            self._m_q = (((self.q_h << 8) | self.q_l) / 32768.0)
            return self._m_q if hasattr(self, '_m_q') else None


    class PhotoStorageInfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.function_code = self._io.read_bytes(6)
            if not self.function_code == b"\x00\x01\x00\x01\x00\x57":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x01\x00\x01\x00\x57", self.function_code, self._io, u"/types/photo_storage_info_t/seq/0")
            self.article_1 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_2 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_3 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_4 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_5 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_6 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_7 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_8 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_9 = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.article_10 = Cas9.PhotoStorageInformationT(self._io, self, self._root)


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
            self.ax25_info = Cas9.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class SatTimeT(KaitaiStruct):
        """W1-Year: 00~99, representing 2000~2099
        W2-Month: 01~12, representing January to December
        W3-Day: 01~31, representing 1st~31st
        W4-Hour: 00~23, representing 0:00~23:00
        W5-minute: 00~59, representing 0 minutes~59 minutes
        W6-second: 00~59, representing 0 seconds~59 seconds
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()


    class PhotoDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.photo_information = Cas9.PhotoStorageInformationT(self._io, self, self._root)
            self.photo_specs = self._io.read_u1()
            self.photo_data = self._io.read_bytes_full()


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
            self.callsign_ror = Cas9.Callsign(_io__raw_callsign_ror, self, self._root)


    class IntToDecimals2T(KaitaiStruct):
        """W1 is the integer part, W2 is the decimal part (2 decimal place)
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.w1 = self._io.read_u1()
            self.w2 = self._io.read_u1()

        @property
        def w1w2(self):
            if hasattr(self, '_m_w1w2'):
                return self._m_w1w2 if hasattr(self, '_m_w1w2') else None

            self._m_w1w2 = (((self.w1 * 100) + self.w2) / 100.0)
            return self._m_w1w2 if hasattr(self, '_m_w1w2') else None


    class DelayTimesT(KaitaiStruct):
        """Delay telemetry times setting
        W1W2W3 is an integer Range: 0 ~ 16777215
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.delay_h = self._io.read_u1()
            self.delay_m = self._io.read_u1()
            self.delay_l = self._io.read_u1()

        @property
        def delay_time(self):
            if hasattr(self, '_m_delay_time'):
                return self._m_delay_time if hasattr(self, '_m_delay_time') else None

            self._m_delay_time = (((self.delay_h << 16) | (self.delay_m << 8)) | self.delay_l)
            return self._m_delay_time if hasattr(self, '_m_delay_time') else None


    class SatTimeSecondsT(KaitaiStruct):
        """Satellite time seconds
        W1 second highest byte
        W2 second high byte
        W3 second low byte
        W4 second lowest byte
        The four bytes are the accumulated value of the whole second of UTC since 0:00:00:00 UTC on January 1, 2009 (0:00 after the jumped second).
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sat_uptime = self._io.read_u4be()


    class PhotoStorageInformationT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()
            self.cam_id = self._io.read_bits_int_be(5)
            self.photo_counter = self._io.read_bits_int_be(11)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_identifier = self._io.read_u1()
            _on = self.packet_identifier
            if _on == 1:
                self._raw_cas9_payload = self._io.read_bytes_full()
                _io__raw_cas9_payload = KaitaiStream(BytesIO(self._raw_cas9_payload))
                self.cas9_payload = Cas9.Cas9TelemetryT(_io__raw_cas9_payload, self, self._root)
            elif _on == 2:
                self._raw_cas9_payload = self._io.read_bytes_full()
                _io__raw_cas9_payload = KaitaiStream(BytesIO(self._raw_cas9_payload))
                self.cas9_payload = Cas9.PhotoStorageInfoT(_io__raw_cas9_payload, self, self._root)
            elif _on == 3:
                self._raw_cas9_payload = self._io.read_bytes_full()
                _io__raw_cas9_payload = KaitaiStream(BytesIO(self._raw_cas9_payload))
                self.cas9_payload = Cas9.PhotoDataT(_io__raw_cas9_payload, self, self._root)
            else:
                self.cas9_payload = self._io.read_bytes_full()

        @property
        def payload_size(self):
            if hasattr(self, '_m_payload_size'):
                return self._m_payload_size if hasattr(self, '_m_payload_size') else None

            self._m_payload_size = self._io.size()
            return self._m_payload_size if hasattr(self, '_m_payload_size') else None


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


