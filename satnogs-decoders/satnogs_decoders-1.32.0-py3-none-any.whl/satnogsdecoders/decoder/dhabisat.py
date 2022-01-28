# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Dhabisat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field data_type: ax25_frame.payload.ax25_info.dhabisat_header.data_type
    :field time_stamp: ax25_frame.payload.ax25_info.dhabisat_header.time_stamp
    :field file_index: ax25_frame.payload.ax25_info.dhabisat_header.file_index
    :field interval: ax25_frame.payload.ax25_info.dhabisat_header.interval
    :field total_packets: ax25_frame.payload.ax25_info.dhabisat_header.total_packets
    :field current_packet: ax25_frame.payload.ax25_info.dhabisat_header.current_packet
    :field payload_ax25_info_beacon_type_callsign: ax25_frame.payload.ax25_info.beacon_type.callsign
    :field obc_mode: ax25_frame.payload.ax25_info.beacon_type.obc_mode
    :field obc_reset_count: ax25_frame.payload.ax25_info.beacon_type.obc_reset_count
    :field obc_timestamp: ax25_frame.payload.ax25_info.beacon_type.obc_timestamp
    :field obc_uptime: ax25_frame.payload.ax25_info.beacon_type.obc_uptime
    :field subsystem_safety_criteria: ax25_frame.payload.ax25_info.beacon_type.subsystem_safety_criteria
    :field telemetry_distribution_counter: ax25_frame.payload.ax25_info.beacon_type.telemetry_distribution_counter
    :field obc_temperature: ax25_frame.payload.ax25_info.beacon_type.obc_temperature
    :field camera_voltage: ax25_frame.payload.ax25_info.beacon_type.camera_voltage
    :field camera_current: ax25_frame.payload.ax25_info.beacon_type.camera_current
    :field battery_temperature: ax25_frame.payload.ax25_info.beacon_type.battery_temperature
    :field battery_voltage: ax25_frame.payload.ax25_info.beacon_type.battery_voltage
    :field adcs_5v_voltage: ax25_frame.payload.ax25_info.beacon_type.adcs_5v_voltage
    :field adcs_5v_current: ax25_frame.payload.ax25_info.beacon_type.adcs_5v_current
    :field adcs_5v_power: ax25_frame.payload.ax25_info.beacon_type.adcs_5v_power
    :field adcs_3v3_voltage: ax25_frame.payload.ax25_info.beacon_type.adcs_3v3_voltage
    :field adcs_3v3_current: ax25_frame.payload.ax25_info.beacon_type.adcs_3v3_current
    :field adcs_3v3_power: ax25_frame.payload.ax25_info.beacon_type.adcs_3v3_power
    :field eps_mode: ax25_frame.payload.ax25_info.beacon_type.eps_mode
    :field eps_reset_cause: ax25_frame.payload.ax25_info.beacon_type.eps_reset_cause
    :field eps_uptime: ax25_frame.payload.ax25_info.beacon_type.eps_uptime
    :field eps_error: ax25_frame.payload.ax25_info.beacon_type.eps_error
    :field eps_system_reset_counter_power_on: ax25_frame.payload.ax25_info.beacon_type.eps_system_reset_counter_power_on
    :field eps_system_reset_counter_watchdog: ax25_frame.payload.ax25_info.beacon_type.eps_system_reset_counter_watchdog
    :field eps_system_reset_counter_commanded: ax25_frame.payload.ax25_info.beacon_type.eps_system_reset_counter_commanded
    :field eps_system_reset_counter_controller: ax25_frame.payload.ax25_info.beacon_type.eps_system_reset_counter_controller
    :field eps_system_reset_counter_low_power: ax25_frame.payload.ax25_info.beacon_type.eps_system_reset_counter_low_power
    :field panel_xp_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_xp_temperature
    :field panel_xn_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_xn_temperature
    :field panel_yp_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_yp_temperature
    :field panel_yn_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_yn_temperature
    :field panel_zp_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_zp_temperature
    :field panel_zn_temperature: ax25_frame.payload.ax25_info.beacon_type.panel_zn_temperature
    :field tx_pa_temp: ax25_frame.payload.ax25_info.beacon_type.tx_pa_temp
    :field attitude_estimation_mode: ax25_frame.payload.ax25_info.beacon_type.attitude_estimation_mode
    :field attitude_control_mode: ax25_frame.payload.ax25_info.beacon_type.attitude_control_mode
    :field adcs_run_mode: ax25_frame.payload.ax25_info.beacon_type.adcs_run_mode
    :field asgp4_mode: ax25_frame.payload.ax25_info.beacon_type.asgp4_mode
    :field cubecontrol_signal_enabled: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_signal_enabled
    :field cubecontrol_motor_enabled: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_motor_enabled
    :field cubesense1_enabled: ax25_frame.payload.ax25_info.beacon_type.cubesense1_enabled
    :field cubesense2_enabled: ax25_frame.payload.ax25_info.beacon_type.cubesense2_enabled
    :field cubewheel1_enabled: ax25_frame.payload.ax25_info.beacon_type.cubewheel1_enabled
    :field cubewheel2_enabled: ax25_frame.payload.ax25_info.beacon_type.cubewheel2_enabled
    :field cubewheel3_enabled: ax25_frame.payload.ax25_info.beacon_type.cubewheel3_enabled
    :field cubestar_enabled: ax25_frame.payload.ax25_info.beacon_type.cubestar_enabled
    :field gps_receiver_enabled: ax25_frame.payload.ax25_info.beacon_type.gps_receiver_enabled
    :field gps_lna_power_enabled: ax25_frame.payload.ax25_info.beacon_type.gps_lna_power_enabled
    :field motor_driver_enabled: ax25_frame.payload.ax25_info.beacon_type.motor_driver_enabled
    :field sun_is_above_local_horizon: ax25_frame.payload.ax25_info.beacon_type.sun_is_above_local_horizon
    :field cubesense1_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubesense1_communications_error
    :field cubesense2_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubesense2_communications_error
    :field cubecontrol_signal_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_signal_communications_error
    :field cubecontrol_motor_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_motor_communications_error
    :field cubewheel1_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel1_communications_error
    :field cubewheel2_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel2_communications_error
    :field cubewheel3_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel3_communications_error
    :field cubestar_communications_error: ax25_frame.payload.ax25_info.beacon_type.cubestar_communications_error
    :field magnetometer_range_error: ax25_frame.payload.ax25_info.beacon_type.magnetometer_range_error
    :field cam1_sram_overcurrent_detected: ax25_frame.payload.ax25_info.beacon_type.cam1_sram_overcurrent_detected
    :field cam1_3v3_overcurrent_detected: ax25_frame.payload.ax25_info.beacon_type.cam1_3v3_overcurrent_detected
    :field cam1_sensor_busy_error: ax25_frame.payload.ax25_info.beacon_type.cam1_sensor_busy_error
    :field cam1_sensor_detection_error: ax25_frame.payload.ax25_info.beacon_type.cam1_sensor_detection_error
    :field sun_sensor_range_error: ax25_frame.payload.ax25_info.beacon_type.sun_sensor_range_error
    :field cam2_sram_overcurrent_detected: ax25_frame.payload.ax25_info.beacon_type.cam2_sram_overcurrent_detected
    :field cam2_3v3_overcurrent_detected: ax25_frame.payload.ax25_info.beacon_type.cam2_3v3_overcurrent_detected
    :field cam2_sensor_busy_error: ax25_frame.payload.ax25_info.beacon_type.cam2_sensor_busy_error
    :field cam2_sensor_detection_error: ax25_frame.payload.ax25_info.beacon_type.cam2_sensor_detection_error
    :field nadir_sensor_range_error: ax25_frame.payload.ax25_info.beacon_type.nadir_sensor_range_error
    :field rate_sensor_range_error: ax25_frame.payload.ax25_info.beacon_type.rate_sensor_range_error
    :field wheel_speed_range_error: ax25_frame.payload.ax25_info.beacon_type.wheel_speed_range_error
    :field coarse_sun_sensor_error: ax25_frame.payload.ax25_info.beacon_type.coarse_sun_sensor_error
    :field startracker_match_error: ax25_frame.payload.ax25_info.beacon_type.startracker_match_error
    :field startracker_overcurrent_detected: ax25_frame.payload.ax25_info.beacon_type.startracker_overcurrent_detected
    :field orbit_parameters_are_invalid: ax25_frame.payload.ax25_info.beacon_type.orbit_parameters_are_invalid
    :field configuration_is_invalid: ax25_frame.payload.ax25_info.beacon_type.configuration_is_invalid
    :field control_mode_change_is_not_allowed: ax25_frame.payload.ax25_info.beacon_type.control_mode_change_is_not_allowed
    :field estimator_change_is_not_allowed: ax25_frame.payload.ax25_info.beacon_type.estimator_change_is_not_allowed
    :field current_magnetometer_sampling_mode: ax25_frame.payload.ax25_info.beacon_type.current_magnetometer_sampling_mode
    :field modelled_and_measured_magnetic_field_differs_in_size: ax25_frame.payload.ax25_info.beacon_type.modelled_and_measured_magnetic_field_differs_in_size
    :field node_recovery_error: ax25_frame.payload.ax25_info.beacon_type.node_recovery_error
    :field cubesense1_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubesense1_runtime_error
    :field cubesense2_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubesense2_runtime_error
    :field cubecontrol_signal_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_signal_runtime_error
    :field cubecontrol_motor_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_motor_runtime_error
    :field cubewheel1_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel1_runtime_error
    :field cubewheel2_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel2_runtime_error
    :field cubewheel3_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubewheel3_runtime_error
    :field cubestar_runtime_error: ax25_frame.payload.ax25_info.beacon_type.cubestar_runtime_error
    :field magnetometer_error: ax25_frame.payload.ax25_info.beacon_type.magnetometer_error
    :field rate_sensor_failure: ax25_frame.payload.ax25_info.beacon_type.rate_sensor_failure
    :field padding_1: ax25_frame.payload.ax25_info.beacon_type.padding_1
    :field padding_2: ax25_frame.payload.ax25_info.beacon_type.padding_2
    :field padding_3: ax25_frame.payload.ax25_info.beacon_type.padding_3
    :field estimated_roll_angle: ax25_frame.payload.ax25_info.beacon_type.estimated_roll_angle
    :field estimated_pitch_angle: ax25_frame.payload.ax25_info.beacon_type.estimated_pitch_angle
    :field estimated_yaw_angle: ax25_frame.payload.ax25_info.beacon_type.estimated_yaw_angle
    :field estimated_q1: ax25_frame.payload.ax25_info.beacon_type.estimated_q1
    :field estimated_q2: ax25_frame.payload.ax25_info.beacon_type.estimated_q2
    :field estimated_q3: ax25_frame.payload.ax25_info.beacon_type.estimated_q3
    :field estimated_x_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_x_angular_rate
    :field estimated_y_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_y_angular_rate
    :field estimated_z_angular_rate: ax25_frame.payload.ax25_info.beacon_type.estimated_z_angular_rate
    :field x_position: ax25_frame.payload.ax25_info.beacon_type.x_position
    :field y_position: ax25_frame.payload.ax25_info.beacon_type.y_position
    :field z_position: ax25_frame.payload.ax25_info.beacon_type.z_position
    :field x_velocity: ax25_frame.payload.ax25_info.beacon_type.x_velocity
    :field y_velocity: ax25_frame.payload.ax25_info.beacon_type.y_velocity
    :field z_velocity: ax25_frame.payload.ax25_info.beacon_type.z_velocity
    :field latitude: ax25_frame.payload.ax25_info.beacon_type.latitude
    :field longitude: ax25_frame.payload.ax25_info.beacon_type.longitude
    :field altitude: ax25_frame.payload.ax25_info.beacon_type.altitude
    :field ecef_position_x: ax25_frame.payload.ax25_info.beacon_type.ecef_position_x
    :field ecef_position_y: ax25_frame.payload.ax25_info.beacon_type.ecef_position_y
    :field ecef_position_z: ax25_frame.payload.ax25_info.beacon_type.ecef_position_z
    :field cubesense1_3v3_current: ax25_frame.payload.ax25_info.beacon_type.cubesense1_3v3_current
    :field cubesense1_cam_sram_current: ax25_frame.payload.ax25_info.beacon_type.cubesense1_cam_sram_current
    :field cubesense2_3v3_current: ax25_frame.payload.ax25_info.beacon_type.cubesense2_3v3_current
    :field cubesense2_cam_sram_current: ax25_frame.payload.ax25_info.beacon_type.cubesense2_cam_sram_current
    :field cubecontrol_3v3_current: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_3v3_current
    :field cubecontrol_5v_current: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_5v_current
    :field cubecontrol_vbat_current: ax25_frame.payload.ax25_info.beacon_type.cubecontrol_vbat_current
    :field wheel1current: ax25_frame.payload.ax25_info.beacon_type.wheel1current
    :field wheel2current: ax25_frame.payload.ax25_info.beacon_type.wheel2current
    :field wheel3current: ax25_frame.payload.ax25_info.beacon_type.wheel3current
    :field cubestarcurrent: ax25_frame.payload.ax25_info.beacon_type.cubestarcurrent
    :field magnetorquercurrent: ax25_frame.payload.ax25_info.beacon_type.magnetorquercurrent
    :field cubestar_mcu_temperature: ax25_frame.payload.ax25_info.beacon_type.cubestar_mcu_temperature
    :field adcs_mcu_temperature: ax25_frame.payload.ax25_info.beacon_type.adcs_mcu_temperature
    :field magnetometer_temperature: ax25_frame.payload.ax25_info.beacon_type.magnetometer_temperature
    :field redundant_magnetometer_temperature: ax25_frame.payload.ax25_info.beacon_type.redundant_magnetometer_temperature
    :field xrate_sensor_temperature: ax25_frame.payload.ax25_info.beacon_type.xrate_sensor_temperature
    :field yrate_sensor_temperature: ax25_frame.payload.ax25_info.beacon_type.yrate_sensor_temperature
    :field zrate_sensor_temperature: ax25_frame.payload.ax25_info.beacon_type.zrate_sensor_temperature
    :field x_angular_rate: ax25_frame.payload.ax25_info.beacon_type.x_angular_rate
    :field y_angular_rate: ax25_frame.payload.ax25_info.beacon_type.y_angular_rate
    :field z_angular_rate: ax25_frame.payload.ax25_info.beacon_type.z_angular_rate
    :field x_wheelspeed: ax25_frame.payload.ax25_info.beacon_type.x_wheelspeed
    :field y_wheelspeed: ax25_frame.payload.ax25_info.beacon_type.y_wheelspeed
    :field z_wheelspeed: ax25_frame.payload.ax25_info.beacon_type.z_wheelspeed
    :field message: ax25_frame.payload.ax25_info.beacon_type.message
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    
    .. seealso::
       Source - https://gitlab.com/librespacefoundation/satnogs/satnogs-decoders/-/issues/57
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Dhabisat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Dhabisat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Dhabisat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Dhabisat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Dhabisat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Dhabisat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Dhabisat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Dhabisat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Dhabisat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Dhabisat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Dhabisat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Dhabisat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Dhabisat.Repeater(self._io, self, self._root)

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
            self.ax25_info = Dhabisat.DhabisatPayload(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"A68MY ") or (self.callsign == u"A68MX ") or (self.callsign == u"A68KU ") or (self.callsign == u"NOCALL")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class DhabisatPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dhabisat_header = Dhabisat.DhabisatHeaderT(self._io, self, self._root)
            _on = self._io.size()
            if _on == 187:
                self.beacon_type = Dhabisat.DhabisatBeacon(self._io, self, self._root)
            else:
                self.beacon_type = Dhabisat.DhabisatGenericPacket(self._io, self, self._root)


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


    class DhabisatGenericPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = (self._io.read_bytes_full()).decode(u"utf-8")


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Dhabisat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Dhabisat.SsidMask(self._io, self, self._root)


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
                _ = Dhabisat.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class DhabisatBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(5)).decode(u"utf-8")
            self.obc_mode = self._io.read_u1()
            self.obc_reset_count = self._io.read_u4le()
            self.obc_timestamp = self._io.read_u4le()
            self.obc_uptime = self._io.read_u4le()
            self.subsystem_safety_criteria = self._io.read_u1()
            self.telemetry_distribution_counter = self._io.read_u4le()
            self.obc_temperature = self._io.read_u1()
            self.camera_voltage = self._io.read_u1()
            self.camera_current = self._io.read_u2le()
            self.battery_temperature = self._io.read_s2le()
            self.battery_voltage = self._io.read_s2le()
            self.adcs_5v_voltage = self._io.read_u2le()
            self.adcs_5v_current = self._io.read_u2le()
            self.adcs_5v_power = self._io.read_u2le()
            self.adcs_3v3_voltage = self._io.read_u2le()
            self.adcs_3v3_current = self._io.read_u2le()
            self.adcs_3v3_power = self._io.read_u2le()
            self.eps_mode = self._io.read_u1()
            self.eps_reset_cause = self._io.read_u1()
            self.eps_uptime = self._io.read_u4le()
            self.eps_error = self._io.read_u2le()
            self.eps_system_reset_counter_power_on = self._io.read_u2le()
            self.eps_system_reset_counter_watchdog = self._io.read_u2le()
            self.eps_system_reset_counter_commanded = self._io.read_u2le()
            self.eps_system_reset_counter_controller = self._io.read_u2le()
            self.eps_system_reset_counter_low_power = self._io.read_u2le()
            self.panel_xp_temperature = self._io.read_u1()
            self.panel_xn_temperature = self._io.read_u1()
            self.panel_yp_temperature = self._io.read_u1()
            self.panel_yn_temperature = self._io.read_u1()
            self.panel_zp_temperature = self._io.read_u1()
            self.panel_zn_temperature = self._io.read_u1()
            self.tx_pa_temp = self._io.read_s2le()
            self.attitude_estimation_mode = self._io.read_bits_int_le(4)
            self.attitude_control_mode = self._io.read_bits_int_le(4)
            self.adcs_run_mode = self._io.read_bits_int_le(2)
            self.asgp4_mode = self._io.read_bits_int_le(2)
            self.cubecontrol_signal_enabled = self._io.read_bits_int_le(1) != 0
            self.cubecontrol_motor_enabled = self._io.read_bits_int_le(1) != 0
            self.cubesense1_enabled = self._io.read_bits_int_le(1) != 0
            self.cubesense2_enabled = self._io.read_bits_int_le(1) != 0
            self.cubewheel1_enabled = self._io.read_bits_int_le(1) != 0
            self.cubewheel2_enabled = self._io.read_bits_int_le(1) != 0
            self.cubewheel3_enabled = self._io.read_bits_int_le(1) != 0
            self.cubestar_enabled = self._io.read_bits_int_le(1) != 0
            self.gps_receiver_enabled = self._io.read_bits_int_le(1) != 0
            self.gps_lna_power_enabled = self._io.read_bits_int_le(1) != 0
            self.motor_driver_enabled = self._io.read_bits_int_le(1) != 0
            self.sun_is_above_local_horizon = self._io.read_bits_int_le(1) != 0
            self.cubesense1_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubesense2_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubecontrol_signal_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubecontrol_motor_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel1_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel2_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel3_communications_error = self._io.read_bits_int_le(1) != 0
            self.cubestar_communications_error = self._io.read_bits_int_le(1) != 0
            self.magnetometer_range_error = self._io.read_bits_int_le(1) != 0
            self.cam1_sram_overcurrent_detected = self._io.read_bits_int_le(1) != 0
            self.cam1_3v3_overcurrent_detected = self._io.read_bits_int_le(1) != 0
            self.cam1_sensor_busy_error = self._io.read_bits_int_le(1) != 0
            self.cam1_sensor_detection_error = self._io.read_bits_int_le(1) != 0
            self.sun_sensor_range_error = self._io.read_bits_int_le(1) != 0
            self.cam2_sram_overcurrent_detected = self._io.read_bits_int_le(1) != 0
            self.cam2_3v3_overcurrent_detected = self._io.read_bits_int_le(1) != 0
            self.cam2_sensor_busy_error = self._io.read_bits_int_le(1) != 0
            self.cam2_sensor_detection_error = self._io.read_bits_int_le(1) != 0
            self.nadir_sensor_range_error = self._io.read_bits_int_le(1) != 0
            self.rate_sensor_range_error = self._io.read_bits_int_le(1) != 0
            self.wheel_speed_range_error = self._io.read_bits_int_le(1) != 0
            self.coarse_sun_sensor_error = self._io.read_bits_int_le(1) != 0
            self.startracker_match_error = self._io.read_bits_int_le(1) != 0
            self.startracker_overcurrent_detected = self._io.read_bits_int_le(1) != 0
            self.orbit_parameters_are_invalid = self._io.read_bits_int_le(1) != 0
            self.configuration_is_invalid = self._io.read_bits_int_le(1) != 0
            self.control_mode_change_is_not_allowed = self._io.read_bits_int_le(1) != 0
            self.estimator_change_is_not_allowed = self._io.read_bits_int_le(1) != 0
            self.current_magnetometer_sampling_mode = self._io.read_bits_int_le(2)
            self.modelled_and_measured_magnetic_field_differs_in_size = self._io.read_bits_int_le(1) != 0
            self.node_recovery_error = self._io.read_bits_int_le(1) != 0
            self.cubesense1_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubesense2_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubecontrol_signal_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubecontrol_motor_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel1_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel2_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubewheel3_runtime_error = self._io.read_bits_int_le(1) != 0
            self.cubestar_runtime_error = self._io.read_bits_int_le(1) != 0
            self.magnetometer_error = self._io.read_bits_int_le(1) != 0
            self.rate_sensor_failure = self._io.read_bits_int_le(1) != 0
            self.padding_1 = self._io.read_bits_int_le(6)
            self._io.align_to_byte()
            self.padding_2 = self._io.read_u2le()
            self.padding_3 = self._io.read_u1()
            self.estimated_roll_angle = self._io.read_s2le()
            self.estimated_pitch_angle = self._io.read_s2le()
            self.estimated_yaw_angle = self._io.read_s2le()
            self.estimated_q1 = self._io.read_s2le()
            self.estimated_q2 = self._io.read_s2le()
            self.estimated_q3 = self._io.read_s2le()
            self.estimated_x_angular_rate = self._io.read_s2le()
            self.estimated_y_angular_rate = self._io.read_s2le()
            self.estimated_z_angular_rate = self._io.read_s2le()
            self.x_position = self._io.read_s2le()
            self.y_position = self._io.read_s2le()
            self.z_position = self._io.read_s2le()
            self.x_velocity = self._io.read_s2le()
            self.y_velocity = self._io.read_s2le()
            self.z_velocity = self._io.read_s2le()
            self.latitude = self._io.read_s2le()
            self.longitude = self._io.read_s2le()
            self.altitude = self._io.read_s2le()
            self.ecef_position_x = self._io.read_s2le()
            self.ecef_position_y = self._io.read_s2le()
            self.ecef_position_z = self._io.read_s2le()
            self.cubesense1_3v3_current = self._io.read_u2le()
            self.cubesense1_cam_sram_current = self._io.read_u2le()
            self.cubesense2_3v3_current = self._io.read_u2le()
            self.cubesense2_cam_sram_current = self._io.read_u2le()
            self.cubecontrol_3v3_current = self._io.read_u2le()
            self.cubecontrol_5v_current = self._io.read_u2le()
            self.cubecontrol_vbat_current = self._io.read_u2le()
            self.wheel1current = self._io.read_u2le()
            self.wheel2current = self._io.read_u2le()
            self.wheel3current = self._io.read_u2le()
            self.cubestarcurrent = self._io.read_u2le()
            self.magnetorquercurrent = self._io.read_u2le()
            self.cubestar_mcu_temperature = self._io.read_s2le()
            self.adcs_mcu_temperature = self._io.read_s2le()
            self.magnetometer_temperature = self._io.read_s2le()
            self.redundant_magnetometer_temperature = self._io.read_s2le()
            self.xrate_sensor_temperature = self._io.read_s2le()
            self.yrate_sensor_temperature = self._io.read_s2le()
            self.zrate_sensor_temperature = self._io.read_s2le()
            self.x_angular_rate = self._io.read_s2le()
            self.y_angular_rate = self._io.read_s2le()
            self.z_angular_rate = self._io.read_s2le()
            self.x_wheelspeed = self._io.read_s2le()
            self.y_wheelspeed = self._io.read_s2le()
            self.z_wheelspeed = self._io.read_s2le()


    class DhabisatHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_type = self._io.read_u1()
            self.time_stamp = self._io.read_u4le()
            self.file_index = self._io.read_u2le()
            self.interval = self._io.read_u2le()
            self.total_packets = self._io.read_u2le()
            self.current_packet = self._io.read_u2le()


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
            self.callsign_ror = Dhabisat.Callsign(_io__raw_callsign_ror, self, self._root)


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


