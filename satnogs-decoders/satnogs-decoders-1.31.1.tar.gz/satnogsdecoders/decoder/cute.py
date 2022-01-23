# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cute(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field ccsds_version: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.ccsds_version
    :field packet_type: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_type
    :field secondary_header_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.secondary_header_flag
    :field is_stored_data: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.is_stored_data
    :field application_process_id: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.application_process_id
    :field grouping_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.grouping_flag
    :field sequence_count: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.sequence_count
    :field packet_length: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_length
    :field time_stamp_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.time_stamp_seconds
    :field sub_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.sub_seconds
    :field padding: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.padding
    :field soh_l0_wdt_2sec_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_2sec_cnt
    :field soh_l0_reset_armed: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.reset_armed
    :field soh_l0_wdt_stat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_stat
    :field soh_l0_wdt_en: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_en
    :field soh_l0_table_select: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.table_select
    :field soh_l0_boot_relay: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.boot_relay
    :field soh_l0_l0_acpt_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.l0_acpt_cnt
    :field soh_l0_l0_rjct_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.l0_rjct_cnt
    :field soh_l0_hw_sec_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.hw_sec_cnt
    :field soh_l0_time_tag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.time_tag
    :field soh_l0_pld_tlm_ack_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.pld_tlm_ack_cnt
    :field soh_l0_pld_cmd_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.pld_cmd_cnt
    :field soh_l0_pld_tlm_to_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.pld_tlm_to_cnt
    :field soh_l0_pld_tlm_nak_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.pld_tlm_nak_cnt
    :field soh_l0_spare_end: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.spare_end
    :field soh_command_tlm_cmd_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.cmd_status
    :field soh_command_tlm_realtime_cmd_accept_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.realtime_cmd_accept_count
    :field soh_command_tlm_realtime_cmd_reject_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.realtime_cmd_reject_count
    :field soh_command_tlm_stored_cmd_accept_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.stored_cmd_accept_count
    :field soh_command_tlm_stored_cmd_reject_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.stored_cmd_reject_count
    :field soh_command_tlm_macros_executing_pack1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack1
    :field soh_command_tlm_macros_executing_pack_bit8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit8
    :field soh_command_tlm_macros_executing_pack_bit7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit7
    :field soh_command_tlm_macros_executing_pack_bit6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit6
    :field soh_command_tlm_macros_executing_pack_bit5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit5
    :field soh_command_tlm_macros_executing_pack_bit4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit4
    :field soh_command_tlm_macros_executing_pack_bit3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit3
    :field soh_command_tlm_macros_executing_pack_bit2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit2
    :field soh_command_tlm_macros_executing_pack_bit1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit1
    :field soh_command_tlm_macros_executing_pack2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack2
    :field soh_command_tlm_macros_executing_pack_bit16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit16
    :field soh_command_tlm_macros_executing_pack_bit15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit15
    :field soh_command_tlm_macros_executing_pack_bit14: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit14
    :field soh_command_tlm_macros_executing_pack_bit13: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit13
    :field soh_command_tlm_macros_executing_pack_bit12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit12
    :field soh_command_tlm_macros_executing_pack_bit11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit11
    :field soh_command_tlm_macros_executing_pack_bit10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit10
    :field soh_command_tlm_macros_executing_pack_bit9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.macros_executing_pack_bit9
    :field soh_general_scrub_status_overall: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.scrub_status_overall
    :field soh_general_image_booted: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.image_booted
    :field soh_general_image_auto_failover: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.image_auto_failover
    :field soh_time_tai_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.tai_seconds
    :field soh_time_time_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.time_valid
    :field soh_refs_position_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci1
    :field soh_refs_position_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci2
    :field soh_refs_position_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci3
    :field soh_refs_velocity_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci1
    :field soh_refs_velocity_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci2
    :field soh_refs_velocity_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci3
    :field soh_refs_refs_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.refs_valid
    :field soh_att_det_q_body_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci1
    :field soh_att_det_q_body_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci2
    :field soh_att_det_q_body_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci3
    :field soh_att_det_q_body_wrt_eci4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci4
    :field soh_att_det_body_rate1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate1
    :field soh_att_det_body_rate1_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate1_dps
    :field soh_att_det_body_rate1_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate1_rpm
    :field soh_att_det_body_rate2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate2
    :field soh_att_det_body_rate2_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate2_dps
    :field soh_att_det_body_rate2_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate2_rpm
    :field soh_att_det_body_rate3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate3
    :field soh_att_det_body_rate3_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate3_dps
    :field soh_att_det_body_rate3_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.body_rate3_rpm
    :field soh_att_det_bad_att_timer: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.bad_att_timer
    :field soh_att_det_bad_rate_timer: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.bad_rate_timer
    :field soh_att_det_reinit_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.reinit_count
    :field soh_att_det_attitude_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.attitude_valid
    :field soh_att_det_meas_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.meas_att_valid
    :field soh_att_det_meas_rate_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.meas_rate_valid
    :field soh_att_det_tracker_used: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.tracker_used
    :field soh_att_cmd_hr_cycle_safe_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.hr_cycle_safe_mode
    :field soh_att_cmd_rotisserie_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.rotisserie_rate
    :field soh_att_cmd_rotisserie_rate_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.rotisserie_rate_dps
    :field soh_att_cmd_rotisserie_rate_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.rotisserie_rate_rpm
    :field soh_att_cmd_adcs_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.adcs_mode
    :field soh_att_cmd_safe_mode_reason: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.safe_mode_reason
    :field soh_att_cmd_recommend_sun_point: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.recommend_sun_point
    :field soh_rw_drive_filtered_speed_rpm1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm1
    :field soh_rw_drive_filtered_speed_rpm2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm2
    :field soh_rw_drive_filtered_speed_rpm3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm3
    :field soh_tracker_operating_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.operating_mode
    :field soh_tracker_star_id_step: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.star_id_step
    :field soh_tracker_att_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.att_status
    :field soh_tracker_num_attitude_stars: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.num_attitude_stars
    :field soh_att_ctrl_position_error1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.position_error1
    :field soh_att_ctrl_position_error2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.position_error2
    :field soh_att_ctrl_position_error3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.position_error3
    :field soh_att_ctrl_time_into_search: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.time_into_search
    :field soh_att_ctrl_wait_timer: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.wait_timer
    :field soh_att_ctrl_sun_point_angle_error: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.sun_point_angle_error
    :field soh_att_ctrl_sun_point_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.sun_point_state
    :field soh_momentum_momentum_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_body1
    :field soh_momentum_momentum_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_body2
    :field soh_momentum_momentum_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_body3
    :field soh_momentum_duty_cycle1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle1
    :field soh_momentum_duty_cycle2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle2
    :field soh_momentum_duty_cycle3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle3
    :field soh_momentum_torque_rod_mode1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode1
    :field soh_momentum_torque_rod_mode2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode2
    :field soh_momentum_torque_rod_mode3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode3
    :field soh_momentum_mag_source_used: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.mag_source_used
    :field soh_momentum_momentum_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_valid
    :field soh_css_sun_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body1
    :field soh_css_sun_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body2
    :field soh_css_sun_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body3
    :field soh_css_sun_vector_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_status
    :field soh_css_sun_sensor_used: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_sensor_used
    :field soh_mag_mag_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body1
    :field soh_mag_mag_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body2
    :field soh_mag_mag_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body3
    :field soh_mag_mag_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_valid
    :field soh_imu_new_packet_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.new_packet_count
    :field soh_imu_imu_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_vector_valid
    :field soh_clock_sync_hr_run_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_run_count
    :field soh_clock_sync_hr_exec_time_ms: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms
    :field soh_analogs_box1_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_analogs.box1_temp
    :field soh_analogs_bus_voltage: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_analogs.bus_voltage
    :field soh_analogs_battery_voltage: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_analogs.battery_voltage
    :field soh_analogs_battery_current: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_analogs.battery_current
    :field soh_tracker2_operating_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker2.operating_mode
    :field soh_tracker2_star_id_step: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker2.star_id_step
    :field soh_tracker2_att_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker2.att_status
    :field soh_tracker2_num_attitude_stars: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker2.num_attitude_stars
    :field soh_gps_gps_lock_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_lock_count
    :field soh_gps_gps_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_valid
    :field soh_gps_gps_enable: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_enable
    :field soh_event_check_latched_resp_fire_pack1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack1
    :field soh_event_check_latched_resp_fire_pack_bit8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit8
    :field soh_event_check_latched_resp_fire_pack_bit7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit7
    :field soh_event_check_latched_resp_fire_pack_bit6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit6
    :field soh_event_check_latched_resp_fire_pack_bit5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit5
    :field soh_event_check_latched_resp_fire_pack_bit4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit4
    :field soh_event_check_latched_resp_fire_pack_bit3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit3
    :field soh_event_check_latched_resp_fire_pack_bit2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit2
    :field soh_event_check_latched_resp_fire_pack_bit1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit1
    :field soh_event_check_latched_resp_fire_pack2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack2
    :field soh_event_check_latched_resp_fire_pack_bit16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit16
    :field soh_event_check_latched_resp_fire_pack_bit15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit15
    :field soh_event_check_latched_resp_fire_pack_bit14: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit14
    :field soh_event_check_latched_resp_fire_pack_bit13: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit13
    :field soh_event_check_latched_resp_fire_pack_bit12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit12
    :field soh_event_check_latched_resp_fire_pack_bit11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit11
    :field soh_event_check_latched_resp_fire_pack_bit10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit10
    :field soh_event_check_latched_resp_fire_pack_bit9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit9
    :field soh_radio_sd_minute_cur: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_minute_cur
    :field soh_radio_sd_percent_used_total: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_percent_used_total
    :field soh_radio_sd_ok: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_ok
    :field soh_radio_sd_fault_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_fault_count
    :field soh_radio_sdr_tx_tx_frames: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_tx_frames
    :field soh_radio_sdr_tx_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_temp
    :field soh_radio_sdr_tx_comm_error: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_comm_error
    :field soh_radio_sq_channel: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_channel
    :field soh_radio_sq_trap_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_trap_count
    :field soh_radio_sq_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_temp
    :field soh_tracker_ctrl_aid_status1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status1
    :field soh_tracker_ctrl_aid_status_bit8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit8
    :field soh_tracker_ctrl_aid_status_bit7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit7
    :field soh_tracker_ctrl_aid_status_bit6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit6
    :field soh_tracker_ctrl_aid_status_bit5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit5
    :field soh_tracker_ctrl_aid_status_bit4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit4
    :field soh_tracker_ctrl_aid_status_bit3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit3
    :field soh_tracker_ctrl_aid_status_bit2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit2
    :field soh_tracker_ctrl_aid_status_bit1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit1
    :field soh_tracker_ctrl_aid_status2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status2
    :field soh_tracker_ctrl_aid_status_bit16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit16
    :field soh_tracker_ctrl_aid_status_bit15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit15
    :field soh_tracker_ctrl_aid_status_bit14: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit14
    :field soh_tracker_ctrl_aid_status_bit13: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit13
    :field soh_tracker_ctrl_aid_status_bit12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit12
    :field soh_tracker_ctrl_aid_status_bit11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit11
    :field soh_tracker_ctrl_aid_status_bit10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit10
    :field soh_tracker_ctrl_aid_status_bit9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.aid_status_bit9
    :field soh_tracker_ctrl_star_id_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.star_id_status
    :field pld_pkt_ccsds_version: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.ccsds_version
    :field pld_pkt_packet_type: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.packet_type
    :field pld_pkt_secondary_header_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.secondary_header_flag
    :field pld_pkt_application_process_id: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.application_process_id
    :field pld_pkt_sequence_flags: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sequence_flags
    :field pld_pkt_sequence_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sequence_count
    :field pld_pkt_packet_length: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.packet_length
    :field pld_sw_stat_sh_coarse: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.sh_coarse
    :field pld_sw_stat_sh_fine: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.sh_fine
    :field pld_sw_stat_pld_sw_ver_maj: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.pld_sw_ver_maj
    :field pld_sw_stat_pld_sw_ver_min: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.pld_sw_ver_min
    :field pld_sw_stat_pld_sw_ver_patch: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.pld_sw_ver_patch
    :field pld_sw_stat_spare: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.spare
    :field pld_sw_stat_sd_state_card1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.sd_state_card1
    :field pld_sw_stat_sd_state_card0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.sd_state_card0
    :field pld_sw_stat_zynq_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_temp
    :field pld_sw_stat_zynq_vcc_int: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_int
    :field pld_sw_stat_zynq_vcc_aux: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_aux
    :field pld_sw_stat_zynq_vcc_bram: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_bram
    :field pld_sw_stat_zynq_vcc_pint: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_pint
    :field pld_sw_stat_zynq_vcc_paux: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_paux
    :field pld_sw_stat_zynq_vcc_pdr0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_vcc_pdr0
    :field pld_sw_stat_zynq_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.zynq_status
    :field pld_sw_stat_spare8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.spare8
    :field pld_sw_stat_roc_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.roc_temp
    :field pld_sw_stat_ccd_p5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_p5
    :field pld_sw_stat_ccd_p15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_p15
    :field pld_sw_stat_ccd_p32: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_p32
    :field pld_sw_stat_ccd_n5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_n5
    :field pld_sw_stat_spare16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.spare16
    :field pld_sw_stat_cmd_recv_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_recv_count
    :field pld_sw_stat_cmd_rjct_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_rjct_count
    :field pld_sw_stat_cmd_succ_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_succ_count
    :field pld_sw_stat_cmd_succ_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_succ_op
    :field pld_sw_stat_cmd_rjct_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_rjct_op
    :field pld_sw_stat_cmd_fail_code: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.cmd_fail_code
    :field pld_sw_stat_spare6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.spare6
    :field pld_sw_stat_arm_state_sc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.arm_state_sc
    :field pld_sw_stat_arm_state_dbg: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.arm_state_dbg
    :field pld_sw_stat_log_write_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.log_write_count
    :field pld_sw_stat_log_drop_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.log_drop_count
    :field pld_sw_stat_ccd_ena_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_ena_state
    :field pld_sw_stat_ccd_ctrl_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_ctrl_state
    :field pld_sw_stat_ccd_shutter: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.ccd_shutter
    :field pld_sw_stat_shutter_override: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.shutter_override
    :field pld_sw_stat_frame_id: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.frame_id
    :field pld_sw_stat_os_cpu_usage: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.os_cpu_usage
    :field pld_sw_stat_os_cpu_max: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.os_cpu_max
    :field pld_sw_stat_time_pps_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.time_pps_count
    :field pld_sw_stat_time_recv_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.time_recv_count
    :field pld_sw_stat_time_miss_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.time_miss_count
    :field pld_sw_stat_fsw_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.fsw_mode
    :field pld_sw_stat_tec_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_state
    :field pld_sw_stat_tec_slew_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_slew_rate
    :field pld_sw_stat_tec_setpoint: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_setpoint
    :field pld_sw_stat_tec_ccd_rtd: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_ccd_rtd
    :field pld_sw_stat_tec_sc_rtd5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_sc_rtd5
    :field pld_sw_stat_tec_sc_rtd4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_sc_rtd4
    :field pld_sw_stat_tec_sc_rtd3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_sc_rtd3
    :field pld_sw_stat_tec_sc_rtd2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_sc_rtd2
    :field pld_sw_stat_tec_sc_rtd1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_sc_rtd1
    :field pld_sw_stat_tec_shutter: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_shutter
    :field pld_sw_stat_tec_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_volt
    :field pld_sw_stat_tec_avg_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_avg_curr
    :field pld_sw_stat_tec_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.tec_curr
    :field pld_sw_stat_img_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.img_state
    :field pld_sw_stat_img_curr_proc_type: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.user_data_field.img_curr_proc_type
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Cute.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Cute.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Cute.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Cute.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Cute.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Cute.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Cute.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Cute.IFrame(self._io, self, self._root)


    class CuteBctSohT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.soh_l0 = Cute.SohL0T(self._io, self, self._root)
            self.soh_command_tlm = Cute.SohCommandTlmT(self._io, self, self._root)
            self.soh_general = Cute.SohGeneralT(self._io, self, self._root)
            self.soh_time = Cute.SohTimeT(self._io, self, self._root)
            self.soh_refs = Cute.SohRefsT(self._io, self, self._root)
            self.soh_att_det = Cute.SohAttDetT(self._io, self, self._root)
            self.soh_att_cmd = Cute.SohAttCmdT(self._io, self, self._root)
            self.soh_rw_drive = Cute.SohRwDriveT(self._io, self, self._root)
            self.soh_tracker = Cute.SohTrackerT(self._io, self, self._root)
            self.soh_att_ctrl = Cute.SohAttCtrlT(self._io, self, self._root)
            self.soh_momentum = Cute.SohMomentumT(self._io, self, self._root)
            self.soh_css = Cute.SohCssT(self._io, self, self._root)
            self.soh_mag = Cute.SohMagT(self._io, self, self._root)
            self.soh_imu = Cute.SohImuT(self._io, self, self._root)
            self.soh_clock_sync = Cute.SohClockSyncT(self._io, self, self._root)
            self.soh_analogs = Cute.SohAnalogsT(self._io, self, self._root)
            self.soh_tracker2 = Cute.SohTracker2T(self._io, self, self._root)
            self.soh_gps = Cute.SohGpsT(self._io, self, self._root)
            self.soh_event_check = Cute.SohEventCheckT(self._io, self, self._root)
            self.soh_radio = Cute.SohRadioT(self._io, self, self._root)
            self.soh_tracker_ctrl = Cute.SohTrackerCtrlT(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Cute.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Cute.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Cute.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Cute.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Cute.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CUTE  ") or (self.callsign == u"BCT   ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class SohClockSyncT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hr_run_count = self._io.read_u4be()
            self.hr_exec_time_ms = self._io.read_u1()


    class SohAttCmdT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hr_cycle_safe_mode = self._io.read_u4be()
            self.rotisserie_rate = self._io.read_s2be()
            self.adcs_mode = self._io.read_u1()
            self.safe_mode_reason = self._io.read_u1()
            self.recommend_sun_point = self._io.read_u1()


    class SohTrackerCtrlT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.aid_status1 = self._io.read_u1()
            self.aid_status2 = self._io.read_u1()
            self.star_id_status = self._io.read_u1()


    class SohTimeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tai_seconds = self._io.read_u4be()
            self.time_valid = self._io.read_u1()


    class SohGpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gps_lock_count = self._io.read_u2be()
            self.gps_valid = self._io.read_u1()
            self.gps_enable = self._io.read_u1()


    class SohRwDriveT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.filtered_speed_rpm1 = self._io.read_s2be()
            self.filtered_speed_rpm2 = self._io.read_s2be()
            self.filtered_speed_rpm3 = self._io.read_s2be()


    class CutePldSwStatT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sh_coarse = self._io.read_u4be()
            self.sh_fine = self._io.read_u2be()
            self.pld_sw_ver_maj = self._io.read_u1()
            self.pld_sw_ver_min = self._io.read_u1()
            self.pld_sw_ver_patch = self._io.read_u1()
            self.spare = self._io.read_bits_int_be(6)
            self.sd_state_card1 = self._io.read_bits_int_be(1) != 0
            self.sd_state_card0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.zynq_temp = self._io.read_u2be()
            self.zynq_vcc_int = self._io.read_u2be()
            self.zynq_vcc_aux = self._io.read_u2be()
            self.zynq_vcc_bram = self._io.read_u2be()
            self.zynq_vcc_pint = self._io.read_u2be()
            self.zynq_vcc_paux = self._io.read_u2be()
            self.zynq_vcc_pdr0 = self._io.read_u2be()
            self.zynq_status = self._io.read_u1()
            self.spare8 = self._io.read_u1()
            self.proc_temp = self._io.read_s2be()
            self.ccd_p5 = self._io.read_u2be()
            self.ccd_p15 = self._io.read_u2be()
            self.ccd_p32 = self._io.read_u2be()
            self.ccd_n5 = self._io.read_u2be()
            self.spare16 = self._io.read_u2be()
            self.cmd_recv_count = self._io.read_u2be()
            self.cmd_rjct_count = self._io.read_u2be()
            self.cmd_succ_count = self._io.read_u2be()
            self.cmd_succ_op = self._io.read_u2be()
            self.cmd_rjct_op = self._io.read_u2be()
            self.cmd_fail_code = self._io.read_u1()
            self.spare6 = self._io.read_bits_int_be(6)
            self.arm_state_sc = self._io.read_bits_int_be(1) != 0
            self.arm_state_dbg = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.log_write_count = self._io.read_u2be()
            self.log_drop_count = self._io.read_u2be()
            self.ccd_ena_state = self._io.read_u1()
            self.ccd_ctrl_state = self._io.read_u1()
            self.ccd_shutter = self._io.read_u1()
            self.shutter_override = self._io.read_u1()
            self.frame_id = self._io.read_u4be()
            self.os_cpu_usage = self._io.read_u2be()
            self.os_cpu_max = self._io.read_u2be()
            self.time_pps_count = self._io.read_u2be()
            self.time_recv_count = self._io.read_u2be()
            self.time_miss_count = self._io.read_u2be()
            self.fsw_mode = self._io.read_u1()
            self.tec_state = self._io.read_u1()
            self.tec_slew_rate = self._io.read_f4be()
            self.tec_setpoint = self._io.read_f4be()
            self.tec_ccd_rtd = self._io.read_u2be()
            self.tec_sc_rtd5 = self._io.read_u2be()
            self.tec_sc_rtd4 = self._io.read_u2be()
            self.tec_sc_rtd3 = self._io.read_u2be()
            self.tec_sc_rtd2 = self._io.read_u2be()
            self.tec_sc_rtd1 = self._io.read_u2be()
            self.tec_shutter = self._io.read_u2be()
            self.tec_volt = self._io.read_u2be()
            self.tec_avg_curr = self._io.read_u2be()
            self.tec_curr = self._io.read_u2be()
            self.img_state = self._io.read_u1()
            self.img_curr_proc_type = self._io.read_u1()


    class SohAnalogsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.box1_temp = self._io.read_s2be()
            self.bus_voltage = self._io.read_s2be()
            self.battery_voltage = self._io.read_u2be()
            self.battery_current = self._io.read_s2be()


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
            self.ax25_info = Cute.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class SohRadioT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sd_minute_cur = self._io.read_u4be()
            self.sd_percent_used_total = self._io.read_u1()
            self.sd_ok = self._io.read_u1()
            self.sd_fault_count = self._io.read_u1()
            self.sdr_tx_tx_frames = self._io.read_u4be()
            self.sdr_tx_temp = self._io.read_s1()
            self.sdr_tx_comm_error = self._io.read_u1()
            self.sq_channel = self._io.read_s1()
            self.sq_trap_count = self._io.read_u1()
            self.sq_temp = self._io.read_u1()


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


    class SohTrackerT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.operating_mode = self._io.read_u1()
            self.star_id_step = self._io.read_u1()
            self.att_status = self._io.read_u1()
            self.num_attitude_stars = self._io.read_u1()


    class SohImuT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.new_packet_count = self._io.read_u1()
            self.imu_vector_valid = self._io.read_u1()


    class DataSectionT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._parent.packet_primary_header.secondary_header_flag:
                self._raw_secondary_header = self._io.read_bytes(6)
                _io__raw_secondary_header = KaitaiStream(BytesIO(self._raw_secondary_header))
                self.secondary_header = Cute.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)

            _on = self._parent.packet_primary_header.application_process_id
            if _on == 86:
                self.user_data_field = Cute.CuteBctSohT(self._io, self, self._root)
            elif _on == 511:
                self.user_data_field = Cute.PldPacketPrimaryHeaderT(self._io, self, self._root)


    class SohMomentumT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.momentum_vector_body1 = self._io.read_s2be()
            self.momentum_vector_body2 = self._io.read_s2be()
            self.momentum_vector_body3 = self._io.read_s2be()
            self.duty_cycle1 = self._io.read_s1()
            self.duty_cycle2 = self._io.read_s1()
            self.duty_cycle3 = self._io.read_s1()
            self.torque_rod_mode1 = self._io.read_u1()
            self.torque_rod_mode2 = self._io.read_u1()
            self.torque_rod_mode3 = self._io.read_u1()
            self.mag_source_used = self._io.read_u1()
            self.momentum_vector_valid = self._io.read_u1()


    class SohCssT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sun_vector_body1 = self._io.read_s2be()
            self.sun_vector_body2 = self._io.read_s2be()
            self.sun_vector_body3 = self._io.read_s2be()
            self.sun_vector_status = self._io.read_u1()
            self.sun_sensor_used = self._io.read_u1()


    class PldPacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.application_process_id = self._io.read_bits_int_be(11)
            self.sequence_flags = self._io.read_bits_int_be(2)
            self.sequence_count = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_length = self._io.read_u2be()
            _on = self.application_process_id
            if _on == 1:
                self.user_data_field = Cute.CutePldSwStatT(self._io, self, self._root)


    class SecondaryHeaderT(KaitaiStruct):
        """The Secondary Header is a feature of the Space Packet which allows
        additional types of information that may be useful to the user
        application (e.g., a time code) to be included.
        See: 4.1.3.2 in CCSDS 133.0-B-1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_stamp_seconds = self._io.read_u4be()
            self.sub_seconds = self._io.read_u1()
            self.padding = self._io.read_u1()


    class SohEventCheckT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.latched_resp_fire_pack1 = self._io.read_u1()
            self.latched_resp_fire_pack2 = self._io.read_u1()


    class SohTracker2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.operating_mode = self._io.read_u1()
            self.star_id_step = self._io.read_u1()
            self.att_status = self._io.read_u1()
            self.num_attitude_stars = self._io.read_u1()


    class SohMagT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mag_vector_body1 = self._io.read_s2be()
            self.mag_vector_body2 = self._io.read_s2be()
            self.mag_vector_body3 = self._io.read_s2be()
            self.mag_vector_valid = self._io.read_u1()


    class PacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.is_stored_data = self._io.read_bits_int_be(1) != 0
            self.application_process_id = self._io.read_bits_int_be(10)
            self.grouping_flag = self._io.read_bits_int_be(2)
            self.sequence_count = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_length = self._io.read_u2be()


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
            self.callsign_ror = Cute.Callsign(_io__raw_callsign_ror, self, self._root)


    class SohGeneralT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.scrub_status_overall = self._io.read_s1()
            self.image_booted = self._io.read_u1()
            self.image_auto_failover = self._io.read_u1()


    class SohAttCtrlT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position_error1 = self._io.read_s4be()
            self.position_error2 = self._io.read_s4be()
            self.position_error3 = self._io.read_s4be()
            self.time_into_search = self._io.read_u2be()
            self.wait_timer = self._io.read_u2be()
            self.sun_point_angle_error = self._io.read_u2be()
            self.sun_point_state = self._io.read_u1()


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Cute.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Cute.DataSectionT(self._io, self, self._root)


    class SohL0T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wdt_2sec_cnt = self._io.read_bits_int_be(3)
            self.reset_armed = self._io.read_bits_int_be(1) != 0
            self.wdt_stat = self._io.read_bits_int_be(1) != 0
            self.wdt_en = self._io.read_bits_int_be(1) != 0
            self.table_select = self._io.read_bits_int_be(1) != 0
            self.boot_relay = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.l0_acpt_cnt = self._io.read_u1()
            self.l0_rjct_cnt = self._io.read_u1()
            self.hw_sec_cnt = self._io.read_u1()
            self.padding_0 = self._io.read_u8be()
            self.time_tag = self._io.read_u4be()
            self.padding_1 = self._io.read_u4be()
            self.pld_tlm_ack_cnt = self._io.read_u1()
            self.pld_cmd_cnt = self._io.read_u1()
            self.pld_tlm_to_cnt = self._io.read_u1()
            self.pld_tlm_nak_cnt = self._io.read_u1()
            self.spare_end = self._io.read_u8be()


    class SohRefsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position_wrt_eci1 = self._io.read_s4be()
            self.position_wrt_eci2 = self._io.read_s4be()
            self.position_wrt_eci3 = self._io.read_s4be()
            self.velocity_wrt_eci1 = self._io.read_s4be()
            self.velocity_wrt_eci2 = self._io.read_s4be()
            self.velocity_wrt_eci3 = self._io.read_s4be()
            self.refs_valid = self._io.read_u1()


    class SohAttDetT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.q_body_wrt_eci1 = self._io.read_s4be()
            self.q_body_wrt_eci2 = self._io.read_s4be()
            self.q_body_wrt_eci3 = self._io.read_s4be()
            self.q_body_wrt_eci4 = self._io.read_s4be()
            self.body_rate1 = self._io.read_s4be()
            self.body_rate2 = self._io.read_s4be()
            self.body_rate3 = self._io.read_s4be()
            self.bad_att_timer = self._io.read_u4be()
            self.bad_rate_timer = self._io.read_u4be()
            self.reinit_count = self._io.read_u4be()
            self.attitude_valid = self._io.read_u1()
            self.meas_att_valid = self._io.read_u1()
            self.meas_rate_valid = self._io.read_u1()
            self.tracker_used = self._io.read_u1()


    class SohCommandTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd_status = self._io.read_u1()
            self.realtime_cmd_accept_count = self._io.read_u1()
            self.realtime_cmd_reject_count = self._io.read_u1()
            self.stored_cmd_accept_count = self._io.read_u1()
            self.stored_cmd_reject_count = self._io.read_u1()
            self.macros_executing_pack1 = self._io.read_u1()
            self.macros_executing_pack2 = self._io.read_u1()


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Cute.CcsdsSpacePacketT(self._io, self, self._root)



