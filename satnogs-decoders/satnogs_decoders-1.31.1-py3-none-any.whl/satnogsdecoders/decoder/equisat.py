# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Equisat(KaitaiStruct):
    """:field timestamp: equisat_frame.preamble.timestamp
    :field msg_op_states: equisat_frame.preamble.msg_op_states
    :field message_type: equisat_frame.preamble.message_type
    :field bytes_of_data: equisat_frame.preamble.bytes_of_data
    :field num_errors: equisat_frame.preamble.num_errors
    :field time_to_flash: equisat_frame.current_info.time_to_flash
    :field boot_count: equisat_frame.current_info.boot_count
    :field l1_ref: equisat_frame.current_info.l1_ref.int16
    :field l2_ref: equisat_frame.current_info.l2_ref.int16
    :field l1_sns: equisat_frame.current_info.l1_sns.int16
    :field l2_sns: equisat_frame.current_info.l2_sns.int16
    :field l1_temp: equisat_frame.current_info.l1_temp.int16
    :field l2_temp: equisat_frame.current_info.l2_temp.int16
    :field panel_ref: equisat_frame.current_info.panel_ref.int16
    :field l_ref: equisat_frame.current_info.l_ref.int16
    :field bat_digsigs_1: equisat_frame.current_info.bat_digsigs_1
    :field bat_digsigs_2: equisat_frame.current_info.bat_digsigs_2
    :field lf1ref: equisat_frame.current_info.lf1ref.int16
    :field lf2ref: equisat_frame.current_info.lf2ref.int16
    :field lf3ref: equisat_frame.current_info.lf3ref.int16
    :field lf4ref: equisat_frame.current_info.lf4ref.int16
    :field idle_batch_0_event_history: equisat_frame.data_section.idle_batch_0.event_history
    :field idle_batch_0_l1_ref: equisat_frame.data_section.idle_batch_0.l1_ref.int16
    :field idle_batch_0_l2_ref: equisat_frame.data_section.idle_batch_0.l2_ref.int16
    :field idle_batch_0_l1_sns: equisat_frame.data_section.idle_batch_0.l1_sns.int16
    :field idle_batch_0_l2_sns: equisat_frame.data_section.idle_batch_0.l2_sns.int16
    :field idle_batch_0_l1_temp: equisat_frame.data_section.idle_batch_0.l1_temp.int16
    :field idle_batch_0_l2_temp: equisat_frame.data_section.idle_batch_0.l2_temp.int16
    :field idle_batch_0_panel_ref: equisat_frame.data_section.idle_batch_0.panel_ref.int16
    :field idle_batch_0_l_ref: equisat_frame.data_section.idle_batch_0.l_ref.int16
    :field idle_batch_0_bat_digsigs_1: equisat_frame.data_section.idle_batch_0.bat_digsigs_1
    :field idle_batch_0_bat_digsigs_2: equisat_frame.data_section.idle_batch_0.bat_digsigs_2
    :field idle_batch_0_rad_temp: equisat_frame.data_section.idle_batch_0.rad_temp.int16
    :field idle_batch_0_imu_temp: equisat_frame.data_section.idle_batch_0.imu_temp.int16
    :field idle_batch_0_ir_flash_amb: equisat_frame.data_section.idle_batch_0.ir_flash_amb.int16
    :field idle_batch_0_ir_side1_amb: equisat_frame.data_section.idle_batch_0.ir_side1_amb.int16
    :field idle_batch_0_ir_side2_amb: equisat_frame.data_section.idle_batch_0.ir_side2_amb.int16
    :field idle_batch_0_ir_rbf_amb: equisat_frame.data_section.idle_batch_0.ir_rbf_amb.int16
    :field idle_batch_0_ir_access_amb: equisat_frame.data_section.idle_batch_0.ir_access_amb.int16
    :field idle_batch_0_ir_top1_amb: equisat_frame.data_section.idle_batch_0.ir_top1_amb.int16
    :field idle_batch_0_timestamp: equisat_frame.data_section.idle_batch_0.timestamp
    :field idle_batch_1_event_history: equisat_frame.data_section.idle_batch_1.event_history
    :field idle_batch_1_l1_ref: equisat_frame.data_section.idle_batch_1.l1_ref.int16
    :field idle_batch_1_l2_ref: equisat_frame.data_section.idle_batch_1.l2_ref.int16
    :field idle_batch_1_l1_sns: equisat_frame.data_section.idle_batch_1.l1_sns.int16
    :field idle_batch_1_l2_sns: equisat_frame.data_section.idle_batch_1.l2_sns.int16
    :field idle_batch_1_l1_temp: equisat_frame.data_section.idle_batch_1.l1_temp.int16
    :field idle_batch_1_l2_temp: equisat_frame.data_section.idle_batch_1.l2_temp.int16
    :field idle_batch_1_panel_ref: equisat_frame.data_section.idle_batch_1.panel_ref.int16
    :field idle_batch_1_l_ref: equisat_frame.data_section.idle_batch_1.l_ref.int16
    :field idle_batch_1_bat_digsigs_1: equisat_frame.data_section.idle_batch_1.bat_digsigs_1
    :field idle_batch_1_bat_digsigs_2: equisat_frame.data_section.idle_batch_1.bat_digsigs_2
    :field idle_batch_1_rad_temp: equisat_frame.data_section.idle_batch_1.rad_temp.int16
    :field idle_batch_1_imu_temp: equisat_frame.data_section.idle_batch_1.imu_temp.int16
    :field idle_batch_1_ir_flash_amb: equisat_frame.data_section.idle_batch_1.ir_flash_amb.int16
    :field idle_batch_1_ir_side1_amb: equisat_frame.data_section.idle_batch_1.ir_side1_amb.int16
    :field idle_batch_1_ir_side2_amb: equisat_frame.data_section.idle_batch_1.ir_side2_amb.int16
    :field idle_batch_1_ir_rbf_amb: equisat_frame.data_section.idle_batch_1.ir_rbf_amb.int16
    :field idle_batch_1_ir_access_amb: equisat_frame.data_section.idle_batch_1.ir_access_amb.int16
    :field idle_batch_1_ir_top1_amb: equisat_frame.data_section.idle_batch_1.ir_top1_amb.int16
    :field idle_batch_1_timestamp: equisat_frame.data_section.idle_batch_1.timestamp
    :field idle_batch_2_event_history: equisat_frame.data_section.idle_batch_2.event_history
    :field idle_batch_2_l1_ref: equisat_frame.data_section.idle_batch_2.l1_ref.int16
    :field idle_batch_2_l2_ref: equisat_frame.data_section.idle_batch_2.l2_ref.int16
    :field idle_batch_2_l1_sns: equisat_frame.data_section.idle_batch_2.l1_sns.int16
    :field idle_batch_2_l2_sns: equisat_frame.data_section.idle_batch_2.l2_sns.int16
    :field idle_batch_2_l1_temp: equisat_frame.data_section.idle_batch_2.l1_temp.int16
    :field idle_batch_2_l2_temp: equisat_frame.data_section.idle_batch_2.l2_temp.int16
    :field idle_batch_2_panel_ref: equisat_frame.data_section.idle_batch_2.panel_ref.int16
    :field idle_batch_2_l_ref: equisat_frame.data_section.idle_batch_2.l_ref.int16
    :field idle_batch_2_bat_digsigs_1: equisat_frame.data_section.idle_batch_2.bat_digsigs_1
    :field idle_batch_2_bat_digsigs_2: equisat_frame.data_section.idle_batch_2.bat_digsigs_2
    :field idle_batch_2_rad_temp: equisat_frame.data_section.idle_batch_2.rad_temp.int16
    :field idle_batch_2_imu_temp: equisat_frame.data_section.idle_batch_2.imu_temp.int16
    :field idle_batch_2_ir_flash_amb: equisat_frame.data_section.idle_batch_2.ir_flash_amb.int16
    :field idle_batch_2_ir_side1_amb: equisat_frame.data_section.idle_batch_2.ir_side1_amb.int16
    :field idle_batch_2_ir_side2_amb: equisat_frame.data_section.idle_batch_2.ir_side2_amb.int16
    :field idle_batch_2_ir_rbf_amb: equisat_frame.data_section.idle_batch_2.ir_rbf_amb.int16
    :field idle_batch_2_ir_access_amb: equisat_frame.data_section.idle_batch_2.ir_access_amb.int16
    :field idle_batch_2_ir_top1_amb: equisat_frame.data_section.idle_batch_2.ir_top1_amb.int16
    :field idle_batch_2_timestamp: equisat_frame.data_section.idle_batch_2.timestamp
    :field idle_batch_3_event_history: equisat_frame.data_section.idle_batch_3.event_history
    :field idle_batch_3_l1_ref: equisat_frame.data_section.idle_batch_3.l1_ref.int16
    :field idle_batch_3_l2_ref: equisat_frame.data_section.idle_batch_3.l2_ref.int16
    :field idle_batch_3_l1_sns: equisat_frame.data_section.idle_batch_3.l1_sns.int16
    :field idle_batch_3_l2_sns: equisat_frame.data_section.idle_batch_3.l2_sns.int16
    :field idle_batch_3_l1_temp: equisat_frame.data_section.idle_batch_3.l1_temp.int16
    :field idle_batch_3_l2_temp: equisat_frame.data_section.idle_batch_3.l2_temp.int16
    :field idle_batch_3_panel_ref: equisat_frame.data_section.idle_batch_3.panel_ref.int16
    :field idle_batch_3_l_ref: equisat_frame.data_section.idle_batch_3.l_ref.int16
    :field idle_batch_3_bat_digsigs_1: equisat_frame.data_section.idle_batch_3.bat_digsigs_1
    :field idle_batch_3_bat_digsigs_2: equisat_frame.data_section.idle_batch_3.bat_digsigs_2
    :field idle_batch_3_rad_temp: equisat_frame.data_section.idle_batch_3.rad_temp.int16
    :field idle_batch_3_imu_temp: equisat_frame.data_section.idle_batch_3.imu_temp.int16
    :field idle_batch_3_ir_flash_amb: equisat_frame.data_section.idle_batch_3.ir_flash_amb.int16
    :field idle_batch_3_ir_side1_amb: equisat_frame.data_section.idle_batch_3.ir_side1_amb.int16
    :field idle_batch_3_ir_side2_amb: equisat_frame.data_section.idle_batch_3.ir_side2_amb.int16
    :field idle_batch_3_ir_rbf_amb: equisat_frame.data_section.idle_batch_3.ir_rbf_amb.int16
    :field idle_batch_3_ir_access_amb: equisat_frame.data_section.idle_batch_3.ir_access_amb.int16
    :field idle_batch_3_ir_top1_amb: equisat_frame.data_section.idle_batch_3.ir_top1_amb.int16
    :field idle_batch_3_timestamp: equisat_frame.data_section.idle_batch_3.timestamp
    :field idle_batch_4_event_history: equisat_frame.data_section.idle_batch_4.event_history
    :field idle_batch_4_l1_ref: equisat_frame.data_section.idle_batch_4.l1_ref.int16
    :field idle_batch_4_l2_ref: equisat_frame.data_section.idle_batch_4.l2_ref.int16
    :field idle_batch_4_l1_sns: equisat_frame.data_section.idle_batch_4.l1_sns.int16
    :field idle_batch_4_l2_sns: equisat_frame.data_section.idle_batch_4.l2_sns.int16
    :field idle_batch_4_l1_temp: equisat_frame.data_section.idle_batch_4.l1_temp.int16
    :field idle_batch_4_l2_temp: equisat_frame.data_section.idle_batch_4.l2_temp.int16
    :field idle_batch_4_panel_ref: equisat_frame.data_section.idle_batch_4.panel_ref.int16
    :field idle_batch_4_l_ref: equisat_frame.data_section.idle_batch_4.l_ref.int16
    :field idle_batch_4_bat_digsigs_1: equisat_frame.data_section.idle_batch_4.bat_digsigs_1
    :field idle_batch_4_bat_digsigs_2: equisat_frame.data_section.idle_batch_4.bat_digsigs_2
    :field idle_batch_4_rad_temp: equisat_frame.data_section.idle_batch_4.rad_temp.int16
    :field idle_batch_4_imu_temp: equisat_frame.data_section.idle_batch_4.imu_temp.int16
    :field idle_batch_4_ir_flash_amb: equisat_frame.data_section.idle_batch_4.ir_flash_amb.int16
    :field idle_batch_4_ir_side1_amb: equisat_frame.data_section.idle_batch_4.ir_side1_amb.int16
    :field idle_batch_4_ir_side2_amb: equisat_frame.data_section.idle_batch_4.ir_side2_amb.int16
    :field idle_batch_4_ir_rbf_amb: equisat_frame.data_section.idle_batch_4.ir_rbf_amb.int16
    :field idle_batch_4_ir_access_amb: equisat_frame.data_section.idle_batch_4.ir_access_amb.int16
    :field idle_batch_4_ir_top1_amb: equisat_frame.data_section.idle_batch_4.ir_top1_amb.int16
    :field idle_batch_4_timestamp: equisat_frame.data_section.idle_batch_4.timestamp
    :field idle_batch_5_event_history: equisat_frame.data_section.idle_batch_5.event_history
    :field idle_batch_5_l1_ref: equisat_frame.data_section.idle_batch_5.l1_ref.int16
    :field idle_batch_5_l2_ref: equisat_frame.data_section.idle_batch_5.l2_ref.int16
    :field idle_batch_5_l1_sns: equisat_frame.data_section.idle_batch_5.l1_sns.int16
    :field idle_batch_5_l2_sns: equisat_frame.data_section.idle_batch_5.l2_sns.int16
    :field idle_batch_5_l1_temp: equisat_frame.data_section.idle_batch_5.l1_temp.int16
    :field idle_batch_5_l2_temp: equisat_frame.data_section.idle_batch_5.l2_temp.int16
    :field idle_batch_5_panel_ref: equisat_frame.data_section.idle_batch_5.panel_ref.int16
    :field idle_batch_5_l_ref: equisat_frame.data_section.idle_batch_5.l_ref.int16
    :field idle_batch_5_bat_digsigs_1: equisat_frame.data_section.idle_batch_5.bat_digsigs_1
    :field idle_batch_5_bat_digsigs_2: equisat_frame.data_section.idle_batch_5.bat_digsigs_2
    :field idle_batch_5_rad_temp: equisat_frame.data_section.idle_batch_5.rad_temp.int16
    :field idle_batch_5_imu_temp: equisat_frame.data_section.idle_batch_5.imu_temp.int16
    :field idle_batch_5_ir_flash_amb: equisat_frame.data_section.idle_batch_5.ir_flash_amb.int16
    :field idle_batch_5_ir_side1_amb: equisat_frame.data_section.idle_batch_5.ir_side1_amb.int16
    :field idle_batch_5_ir_side2_amb: equisat_frame.data_section.idle_batch_5.ir_side2_amb.int16
    :field idle_batch_5_ir_rbf_amb: equisat_frame.data_section.idle_batch_5.ir_rbf_amb.int16
    :field idle_batch_5_ir_access_amb: equisat_frame.data_section.idle_batch_5.ir_access_amb.int16
    :field idle_batch_5_ir_top1_amb: equisat_frame.data_section.idle_batch_5.ir_top1_amb.int16
    :field idle_batch_5_timestamp: equisat_frame.data_section.idle_batch_5.timestamp
    :field idle_batch_6_event_history: equisat_frame.data_section.idle_batch_6.event_history
    :field idle_batch_6_l1_ref: equisat_frame.data_section.idle_batch_6.l1_ref.int16
    :field idle_batch_6_l2_ref: equisat_frame.data_section.idle_batch_6.l2_ref.int16
    :field idle_batch_6_l1_sns: equisat_frame.data_section.idle_batch_6.l1_sns.int16
    :field idle_batch_6_l2_sns: equisat_frame.data_section.idle_batch_6.l2_sns.int16
    :field idle_batch_6_l1_temp: equisat_frame.data_section.idle_batch_6.l1_temp.int16
    :field idle_batch_6_l2_temp: equisat_frame.data_section.idle_batch_6.l2_temp.int16
    :field idle_batch_6_panel_ref: equisat_frame.data_section.idle_batch_6.panel_ref.int16
    :field idle_batch_6_l_ref: equisat_frame.data_section.idle_batch_6.l_ref.int16
    :field idle_batch_6_bat_digsigs_1: equisat_frame.data_section.idle_batch_6.bat_digsigs_1
    :field idle_batch_6_bat_digsigs_2: equisat_frame.data_section.idle_batch_6.bat_digsigs_2
    :field idle_batch_6_rad_temp: equisat_frame.data_section.idle_batch_6.rad_temp.int16
    :field idle_batch_6_imu_temp: equisat_frame.data_section.idle_batch_6.imu_temp.int16
    :field idle_batch_6_ir_flash_amb: equisat_frame.data_section.idle_batch_6.ir_flash_amb.int16
    :field idle_batch_6_ir_side1_amb: equisat_frame.data_section.idle_batch_6.ir_side1_amb.int16
    :field idle_batch_6_ir_side2_amb: equisat_frame.data_section.idle_batch_6.ir_side2_amb.int16
    :field idle_batch_6_ir_rbf_amb: equisat_frame.data_section.idle_batch_6.ir_rbf_amb.int16
    :field idle_batch_6_ir_access_amb: equisat_frame.data_section.idle_batch_6.ir_access_amb.int16
    :field idle_batch_6_ir_top1_amb: equisat_frame.data_section.idle_batch_6.ir_top1_amb.int16
    :field idle_batch_6_timestamp: equisat_frame.data_section.idle_batch_6.timestamp
    :field attitude_batch_0_ir_flash_obj: equisat_frame.data_section.attitude_batch_0.ir_flash_obj
    :field attitude_batch_0_ir_side1_obj: equisat_frame.data_section.attitude_batch_0.ir_side1_obj
    :field attitude_batch_0_ir_side2_obj: equisat_frame.data_section.attitude_batch_0.ir_side2_obj
    :field attitude_batch_0_ir_rbf_obj: equisat_frame.data_section.attitude_batch_0.ir_rbf_obj
    :field attitude_batch_0_ir_access_obj: equisat_frame.data_section.attitude_batch_0.ir_access_obj
    :field attitude_batch_0_ir_top1_obj: equisat_frame.data_section.attitude_batch_0.ir_top1_obj
    :field attitude_batch_0_pd_1: equisat_frame.data_section.attitude_batch_0.pd_1
    :field attitude_batch_0_pd_2: equisat_frame.data_section.attitude_batch_0.pd_2
    :field attitude_batch_0_accelerometer1_x: equisat_frame.data_section.attitude_batch_0.accelerometer1_x.int16
    :field attitude_batch_0_accelerometer1_z: equisat_frame.data_section.attitude_batch_0.accelerometer1_z.int16
    :field attitude_batch_0_accelerometer1_y: equisat_frame.data_section.attitude_batch_0.accelerometer1_y.int16
    :field attitude_batch_0_accelerometer2_x: equisat_frame.data_section.attitude_batch_0.accelerometer2_x.int16
    :field attitude_batch_0_accelerometer2_z: equisat_frame.data_section.attitude_batch_0.accelerometer2_z.int16
    :field attitude_batch_0_accelerometer2_y: equisat_frame.data_section.attitude_batch_0.accelerometer2_y.int16
    :field attitude_batch_0_gyroscope_x: equisat_frame.data_section.attitude_batch_0.gyroscope_x.int16
    :field attitude_batch_0_gyroscope_z: equisat_frame.data_section.attitude_batch_0.gyroscope_z.int16
    :field attitude_batch_0_gyroscope_y: equisat_frame.data_section.attitude_batch_0.gyroscope_y.int16
    :field attitude_batch_0_magnetometer1_x: equisat_frame.data_section.attitude_batch_0.magnetometer1_x.int16
    :field attitude_batch_0_magnetometer1_z: equisat_frame.data_section.attitude_batch_0.magnetometer1_z.int16
    :field attitude_batch_0_magnetometer1_y: equisat_frame.data_section.attitude_batch_0.magnetometer1_y.int16
    :field attitude_batch_0_magnetometer2_x: equisat_frame.data_section.attitude_batch_0.magnetometer2_x.int16
    :field attitude_batch_0_magnetometer2_z: equisat_frame.data_section.attitude_batch_0.magnetometer2_z.int16
    :field attitude_batch_0_magnetometer2_y: equisat_frame.data_section.attitude_batch_0.magnetometer2_y.int16
    :field attitude_batch_0_timestamp: equisat_frame.data_section.attitude_batch_0.timestamp
    :field attitude_batch_0_pd_flash: equisat_frame.data_section.attitude_batch_0.pd_flash
    :field attitude_batch_0_pd_side1: equisat_frame.data_section.attitude_batch_0.pd_side1
    :field attitude_batch_0_pd_side2: equisat_frame.data_section.attitude_batch_0.pd_side2
    :field attitude_batch_0_pd_access: equisat_frame.data_section.attitude_batch_0.pd_access
    :field attitude_batch_0_pd_top1: equisat_frame.data_section.attitude_batch_0.pd_top1
    :field attitude_batch_0_pd_top2: equisat_frame.data_section.attitude_batch_0.pd_top2
    :field attitude_batch_1_ir_flash_obj: equisat_frame.data_section.attitude_batch_1.ir_flash_obj
    :field attitude_batch_1_ir_side1_obj: equisat_frame.data_section.attitude_batch_1.ir_side1_obj
    :field attitude_batch_1_ir_side2_obj: equisat_frame.data_section.attitude_batch_1.ir_side2_obj
    :field attitude_batch_1_ir_rbf_obj: equisat_frame.data_section.attitude_batch_1.ir_rbf_obj
    :field attitude_batch_1_ir_access_obj: equisat_frame.data_section.attitude_batch_1.ir_access_obj
    :field attitude_batch_1_ir_top1_obj: equisat_frame.data_section.attitude_batch_1.ir_top1_obj
    :field attitude_batch_1_pd_1: equisat_frame.data_section.attitude_batch_1.pd_1
    :field attitude_batch_1_pd_2: equisat_frame.data_section.attitude_batch_1.pd_2
    :field attitude_batch_1_accelerometer1_x: equisat_frame.data_section.attitude_batch_1.accelerometer1_x.int16
    :field attitude_batch_1_accelerometer1_z: equisat_frame.data_section.attitude_batch_1.accelerometer1_z.int16
    :field attitude_batch_1_accelerometer1_y: equisat_frame.data_section.attitude_batch_1.accelerometer1_y.int16
    :field attitude_batch_1_accelerometer2_x: equisat_frame.data_section.attitude_batch_1.accelerometer2_x.int16
    :field attitude_batch_1_accelerometer2_z: equisat_frame.data_section.attitude_batch_1.accelerometer2_z.int16
    :field attitude_batch_1_accelerometer2_y: equisat_frame.data_section.attitude_batch_1.accelerometer2_y.int16
    :field attitude_batch_1_gyroscope_x: equisat_frame.data_section.attitude_batch_1.gyroscope_x.int16
    :field attitude_batch_1_gyroscope_z: equisat_frame.data_section.attitude_batch_1.gyroscope_z.int16
    :field attitude_batch_1_gyroscope_y: equisat_frame.data_section.attitude_batch_1.gyroscope_y.int16
    :field attitude_batch_1_magnetometer1_x: equisat_frame.data_section.attitude_batch_1.magnetometer1_x.int16
    :field attitude_batch_1_magnetometer1_z: equisat_frame.data_section.attitude_batch_1.magnetometer1_z.int16
    :field attitude_batch_1_magnetometer1_y: equisat_frame.data_section.attitude_batch_1.magnetometer1_y.int16
    :field attitude_batch_1_magnetometer2_x: equisat_frame.data_section.attitude_batch_1.magnetometer2_x.int16
    :field attitude_batch_1_magnetometer2_z: equisat_frame.data_section.attitude_batch_1.magnetometer2_z.int16
    :field attitude_batch_1_magnetometer2_y: equisat_frame.data_section.attitude_batch_1.magnetometer2_y.int16
    :field attitude_batch_1_timestamp: equisat_frame.data_section.attitude_batch_1.timestamp
    :field attitude_batch_1_pd_flash: equisat_frame.data_section.attitude_batch_1.pd_flash
    :field attitude_batch_1_pd_side1: equisat_frame.data_section.attitude_batch_1.pd_side1
    :field attitude_batch_1_pd_side2: equisat_frame.data_section.attitude_batch_1.pd_side2
    :field attitude_batch_1_pd_access: equisat_frame.data_section.attitude_batch_1.pd_access
    :field attitude_batch_1_pd_top1: equisat_frame.data_section.attitude_batch_1.pd_top1
    :field attitude_batch_1_pd_top2: equisat_frame.data_section.attitude_batch_1.pd_top2
    :field attitude_batch_2_ir_flash_obj: equisat_frame.data_section.attitude_batch_2.ir_flash_obj
    :field attitude_batch_2_ir_side1_obj: equisat_frame.data_section.attitude_batch_2.ir_side1_obj
    :field attitude_batch_2_ir_side2_obj: equisat_frame.data_section.attitude_batch_2.ir_side2_obj
    :field attitude_batch_2_ir_rbf_obj: equisat_frame.data_section.attitude_batch_2.ir_rbf_obj
    :field attitude_batch_2_ir_access_obj: equisat_frame.data_section.attitude_batch_2.ir_access_obj
    :field attitude_batch_2_ir_top1_obj: equisat_frame.data_section.attitude_batch_2.ir_top1_obj
    :field attitude_batch_2_pd_1: equisat_frame.data_section.attitude_batch_2.pd_1
    :field attitude_batch_2_pd_2: equisat_frame.data_section.attitude_batch_2.pd_2
    :field attitude_batch_2_accelerometer1_x: equisat_frame.data_section.attitude_batch_2.accelerometer1_x.int16
    :field attitude_batch_2_accelerometer1_z: equisat_frame.data_section.attitude_batch_2.accelerometer1_z.int16
    :field attitude_batch_2_accelerometer1_y: equisat_frame.data_section.attitude_batch_2.accelerometer1_y.int16
    :field attitude_batch_2_accelerometer2_x: equisat_frame.data_section.attitude_batch_2.accelerometer2_x.int16
    :field attitude_batch_2_accelerometer2_z: equisat_frame.data_section.attitude_batch_2.accelerometer2_z.int16
    :field attitude_batch_2_accelerometer2_y: equisat_frame.data_section.attitude_batch_2.accelerometer2_y.int16
    :field attitude_batch_2_gyroscope_x: equisat_frame.data_section.attitude_batch_2.gyroscope_x.int16
    :field attitude_batch_2_gyroscope_z: equisat_frame.data_section.attitude_batch_2.gyroscope_z.int16
    :field attitude_batch_2_gyroscope_y: equisat_frame.data_section.attitude_batch_2.gyroscope_y.int16
    :field attitude_batch_2_magnetometer1_x: equisat_frame.data_section.attitude_batch_2.magnetometer1_x.int16
    :field attitude_batch_2_magnetometer1_z: equisat_frame.data_section.attitude_batch_2.magnetometer1_z.int16
    :field attitude_batch_2_magnetometer1_y: equisat_frame.data_section.attitude_batch_2.magnetometer1_y.int16
    :field attitude_batch_2_magnetometer2_x: equisat_frame.data_section.attitude_batch_2.magnetometer2_x.int16
    :field attitude_batch_2_magnetometer2_z: equisat_frame.data_section.attitude_batch_2.magnetometer2_z.int16
    :field attitude_batch_2_magnetometer2_y: equisat_frame.data_section.attitude_batch_2.magnetometer2_y.int16
    :field attitude_batch_2_timestamp: equisat_frame.data_section.attitude_batch_2.timestamp
    :field attitude_batch_2_pd_flash: equisat_frame.data_section.attitude_batch_2.pd_flash
    :field attitude_batch_2_pd_side1: equisat_frame.data_section.attitude_batch_2.pd_side1
    :field attitude_batch_2_pd_side2: equisat_frame.data_section.attitude_batch_2.pd_side2
    :field attitude_batch_2_pd_access: equisat_frame.data_section.attitude_batch_2.pd_access
    :field attitude_batch_2_pd_top1: equisat_frame.data_section.attitude_batch_2.pd_top1
    :field attitude_batch_2_pd_top2: equisat_frame.data_section.attitude_batch_2.pd_top2
    :field attitude_batch_3_ir_flash_obj: equisat_frame.data_section.attitude_batch_3.ir_flash_obj
    :field attitude_batch_3_ir_side1_obj: equisat_frame.data_section.attitude_batch_3.ir_side1_obj
    :field attitude_batch_3_ir_side2_obj: equisat_frame.data_section.attitude_batch_3.ir_side2_obj
    :field attitude_batch_3_ir_rbf_obj: equisat_frame.data_section.attitude_batch_3.ir_rbf_obj
    :field attitude_batch_3_ir_access_obj: equisat_frame.data_section.attitude_batch_3.ir_access_obj
    :field attitude_batch_3_ir_top1_obj: equisat_frame.data_section.attitude_batch_3.ir_top1_obj
    :field attitude_batch_3_pd_1: equisat_frame.data_section.attitude_batch_3.pd_1
    :field attitude_batch_3_pd_2: equisat_frame.data_section.attitude_batch_3.pd_2
    :field attitude_batch_3_accelerometer1_x: equisat_frame.data_section.attitude_batch_3.accelerometer1_x.int16
    :field attitude_batch_3_accelerometer1_z: equisat_frame.data_section.attitude_batch_3.accelerometer1_z.int16
    :field attitude_batch_3_accelerometer1_y: equisat_frame.data_section.attitude_batch_3.accelerometer1_y.int16
    :field attitude_batch_3_accelerometer2_x: equisat_frame.data_section.attitude_batch_3.accelerometer2_x.int16
    :field attitude_batch_3_accelerometer2_z: equisat_frame.data_section.attitude_batch_3.accelerometer2_z.int16
    :field attitude_batch_3_accelerometer2_y: equisat_frame.data_section.attitude_batch_3.accelerometer2_y.int16
    :field attitude_batch_3_gyroscope_x: equisat_frame.data_section.attitude_batch_3.gyroscope_x.int16
    :field attitude_batch_3_gyroscope_z: equisat_frame.data_section.attitude_batch_3.gyroscope_z.int16
    :field attitude_batch_3_gyroscope_y: equisat_frame.data_section.attitude_batch_3.gyroscope_y.int16
    :field attitude_batch_3_magnetometer1_x: equisat_frame.data_section.attitude_batch_3.magnetometer1_x.int16
    :field attitude_batch_3_magnetometer1_z: equisat_frame.data_section.attitude_batch_3.magnetometer1_z.int16
    :field attitude_batch_3_magnetometer1_y: equisat_frame.data_section.attitude_batch_3.magnetometer1_y.int16
    :field attitude_batch_3_magnetometer2_x: equisat_frame.data_section.attitude_batch_3.magnetometer2_x.int16
    :field attitude_batch_3_magnetometer2_z: equisat_frame.data_section.attitude_batch_3.magnetometer2_z.int16
    :field attitude_batch_3_magnetometer2_y: equisat_frame.data_section.attitude_batch_3.magnetometer2_y.int16
    :field attitude_batch_3_timestamp: equisat_frame.data_section.attitude_batch_3.timestamp
    :field attitude_batch_3_pd_flash: equisat_frame.data_section.attitude_batch_3.pd_flash
    :field attitude_batch_3_pd_side1: equisat_frame.data_section.attitude_batch_3.pd_side1
    :field attitude_batch_3_pd_side2: equisat_frame.data_section.attitude_batch_3.pd_side2
    :field attitude_batch_3_pd_access: equisat_frame.data_section.attitude_batch_3.pd_access
    :field attitude_batch_3_pd_top1: equisat_frame.data_section.attitude_batch_3.pd_top1
    :field attitude_batch_3_pd_top2: equisat_frame.data_section.attitude_batch_3.pd_top2
    :field attitude_batch_4_ir_flash_obj: equisat_frame.data_section.attitude_batch_4.ir_flash_obj
    :field attitude_batch_4_ir_side1_obj: equisat_frame.data_section.attitude_batch_4.ir_side1_obj
    :field attitude_batch_4_ir_side2_obj: equisat_frame.data_section.attitude_batch_4.ir_side2_obj
    :field attitude_batch_4_ir_rbf_obj: equisat_frame.data_section.attitude_batch_4.ir_rbf_obj
    :field attitude_batch_4_ir_access_obj: equisat_frame.data_section.attitude_batch_4.ir_access_obj
    :field attitude_batch_4_ir_top1_obj: equisat_frame.data_section.attitude_batch_4.ir_top1_obj
    :field attitude_batch_4_pd_1: equisat_frame.data_section.attitude_batch_4.pd_1
    :field attitude_batch_4_pd_2: equisat_frame.data_section.attitude_batch_4.pd_2
    :field attitude_batch_4_accelerometer1_x: equisat_frame.data_section.attitude_batch_4.accelerometer1_x.int16
    :field attitude_batch_4_accelerometer1_z: equisat_frame.data_section.attitude_batch_4.accelerometer1_z.int16
    :field attitude_batch_4_accelerometer1_y: equisat_frame.data_section.attitude_batch_4.accelerometer1_y.int16
    :field attitude_batch_4_accelerometer2_x: equisat_frame.data_section.attitude_batch_4.accelerometer2_x.int16
    :field attitude_batch_4_accelerometer2_z: equisat_frame.data_section.attitude_batch_4.accelerometer2_z.int16
    :field attitude_batch_4_accelerometer2_y: equisat_frame.data_section.attitude_batch_4.accelerometer2_y.int16
    :field attitude_batch_4_gyroscope_x: equisat_frame.data_section.attitude_batch_4.gyroscope_x.int16
    :field attitude_batch_4_gyroscope_z: equisat_frame.data_section.attitude_batch_4.gyroscope_z.int16
    :field attitude_batch_4_gyroscope_y: equisat_frame.data_section.attitude_batch_4.gyroscope_y.int16
    :field attitude_batch_4_magnetometer1_x: equisat_frame.data_section.attitude_batch_4.magnetometer1_x.int16
    :field attitude_batch_4_magnetometer1_z: equisat_frame.data_section.attitude_batch_4.magnetometer1_z.int16
    :field attitude_batch_4_magnetometer1_y: equisat_frame.data_section.attitude_batch_4.magnetometer1_y.int16
    :field attitude_batch_4_magnetometer2_x: equisat_frame.data_section.attitude_batch_4.magnetometer2_x.int16
    :field attitude_batch_4_magnetometer2_z: equisat_frame.data_section.attitude_batch_4.magnetometer2_z.int16
    :field attitude_batch_4_magnetometer2_y: equisat_frame.data_section.attitude_batch_4.magnetometer2_y.int16
    :field attitude_batch_4_timestamp: equisat_frame.data_section.attitude_batch_4.timestamp
    :field attitude_batch_4_pd_flash: equisat_frame.data_section.attitude_batch_4.pd_flash
    :field attitude_batch_4_pd_side1: equisat_frame.data_section.attitude_batch_4.pd_side1
    :field attitude_batch_4_pd_side2: equisat_frame.data_section.attitude_batch_4.pd_side2
    :field attitude_batch_4_pd_access: equisat_frame.data_section.attitude_batch_4.pd_access
    :field attitude_batch_4_pd_top1: equisat_frame.data_section.attitude_batch_4.pd_top1
    :field attitude_batch_4_pd_top2: equisat_frame.data_section.attitude_batch_4.pd_top2
    :field flash_burst_data_led1_temp_0: equisat_frame.data_section.led1_temp_0.int16
    :field flash_burst_data_led1_temp_1: equisat_frame.data_section.led1_temp_1.int16
    :field flash_burst_data_led1_temp_2: equisat_frame.data_section.led1_temp_2.int16
    :field flash_burst_data_led1_temp_3: equisat_frame.data_section.led1_temp_3.int16
    :field flash_burst_data_led1_temp_4: equisat_frame.data_section.led1_temp_4.int16
    :field flash_burst_data_led1_temp_5: equisat_frame.data_section.led1_temp_5.int16
    :field flash_burst_data_led1_temp_6: equisat_frame.data_section.led1_temp_6.int16
    :field flash_burst_data_led2_temp_0: equisat_frame.data_section.led2_temp_0.int16
    :field flash_burst_data_led2_temp_1: equisat_frame.data_section.led2_temp_1.int16
    :field flash_burst_data_led2_temp_2: equisat_frame.data_section.led2_temp_2.int16
    :field flash_burst_data_led2_temp_3: equisat_frame.data_section.led2_temp_3.int16
    :field flash_burst_data_led2_temp_4: equisat_frame.data_section.led2_temp_4.int16
    :field flash_burst_data_led2_temp_5: equisat_frame.data_section.led2_temp_5.int16
    :field flash_burst_data_led2_temp_6: equisat_frame.data_section.led2_temp_6.int16
    :field flash_burst_data_led3_temp_0: equisat_frame.data_section.led3_temp_0.int16
    :field flash_burst_data_led3_temp_1: equisat_frame.data_section.led3_temp_1.int16
    :field flash_burst_data_led3_temp_2: equisat_frame.data_section.led3_temp_2.int16
    :field flash_burst_data_led3_temp_3: equisat_frame.data_section.led3_temp_3.int16
    :field flash_burst_data_led3_temp_4: equisat_frame.data_section.led3_temp_4.int16
    :field flash_burst_data_led3_temp_5: equisat_frame.data_section.led3_temp_5.int16
    :field flash_burst_data_led3_temp_6: equisat_frame.data_section.led3_temp_6.int16
    :field flash_burst_data_led4_temp_0: equisat_frame.data_section.led4_temp_0.int16
    :field flash_burst_data_led4_temp_1: equisat_frame.data_section.led4_temp_1.int16
    :field flash_burst_data_led4_temp_2: equisat_frame.data_section.led4_temp_2.int16
    :field flash_burst_data_led4_temp_3: equisat_frame.data_section.led4_temp_3.int16
    :field flash_burst_data_led4_temp_4: equisat_frame.data_section.led4_temp_4.int16
    :field flash_burst_data_led4_temp_5: equisat_frame.data_section.led4_temp_5.int16
    :field flash_burst_data_led4_temp_6: equisat_frame.data_section.led4_temp_6.int16
    :field flash_burst_data_lf1_temp_0: equisat_frame.data_section.lf1_temp_0.int16
    :field flash_burst_data_lf1_temp_1: equisat_frame.data_section.lf1_temp_1.int16
    :field flash_burst_data_lf1_temp_2: equisat_frame.data_section.lf1_temp_2.int16
    :field flash_burst_data_lf1_temp_3: equisat_frame.data_section.lf1_temp_3.int16
    :field flash_burst_data_lf1_temp_4: equisat_frame.data_section.lf1_temp_4.int16
    :field flash_burst_data_lf1_temp_5: equisat_frame.data_section.lf1_temp_5.int16
    :field flash_burst_data_lf1_temp_6: equisat_frame.data_section.lf1_temp_6.int16
    :field flash_burst_data_lf3_temp_0: equisat_frame.data_section.lf3_temp_0.int16
    :field flash_burst_data_lf3_temp_1: equisat_frame.data_section.lf3_temp_1.int16
    :field flash_burst_data_lf3_temp_2: equisat_frame.data_section.lf3_temp_2.int16
    :field flash_burst_data_lf3_temp_3: equisat_frame.data_section.lf3_temp_3.int16
    :field flash_burst_data_lf3_temp_4: equisat_frame.data_section.lf3_temp_4.int16
    :field flash_burst_data_lf3_temp_5: equisat_frame.data_section.lf3_temp_5.int16
    :field flash_burst_data_lf3_temp_6: equisat_frame.data_section.lf3_temp_6.int16
    :field flash_burst_data_lfb1_sns_0: equisat_frame.data_section.lfb1_sns_0.int16
    :field flash_burst_data_lfb1_sns_1: equisat_frame.data_section.lfb1_sns_1.int16
    :field flash_burst_data_lfb1_sns_2: equisat_frame.data_section.lfb1_sns_2.int16
    :field flash_burst_data_lfb1_sns_3: equisat_frame.data_section.lfb1_sns_3.int16
    :field flash_burst_data_lfb1_sns_4: equisat_frame.data_section.lfb1_sns_4.int16
    :field flash_burst_data_lfb1_sns_5: equisat_frame.data_section.lfb1_sns_5.int16
    :field flash_burst_data_lfb1_sns_6: equisat_frame.data_section.lfb1_sns_6.int16
    :field flash_burst_data_lfb1_osns_0: equisat_frame.data_section.lfb1_osns_0.int16
    :field flash_burst_data_lfb1_osns_1: equisat_frame.data_section.lfb1_osns_1.int16
    :field flash_burst_data_lfb1_osns_2: equisat_frame.data_section.lfb1_osns_2.int16
    :field flash_burst_data_lfb1_osns_3: equisat_frame.data_section.lfb1_osns_3.int16
    :field flash_burst_data_lfb1_osns_4: equisat_frame.data_section.lfb1_osns_4.int16
    :field flash_burst_data_lfb1_osns_5: equisat_frame.data_section.lfb1_osns_5.int16
    :field flash_burst_data_lfb1_osns_6: equisat_frame.data_section.lfb1_osns_6.int16
    :field flash_burst_data_lfb2_sns_0: equisat_frame.data_section.lfb2_sns_0.int16
    :field flash_burst_data_lfb2_sns_1: equisat_frame.data_section.lfb2_sns_1.int16
    :field flash_burst_data_lfb2_sns_2: equisat_frame.data_section.lfb2_sns_2.int16
    :field flash_burst_data_lfb2_sns_3: equisat_frame.data_section.lfb2_sns_3.int16
    :field flash_burst_data_lfb2_sns_4: equisat_frame.data_section.lfb2_sns_4.int16
    :field flash_burst_data_lfb2_sns_5: equisat_frame.data_section.lfb2_sns_5.int16
    :field flash_burst_data_lfb2_sns_6: equisat_frame.data_section.lfb2_sns_6.int16
    :field flash_burst_data_lfb2_osns_0: equisat_frame.data_section.lfb2_osns_0.int16
    :field flash_burst_data_lfb2_osns_1: equisat_frame.data_section.lfb2_osns_1.int16
    :field flash_burst_data_lfb2_osns_2: equisat_frame.data_section.lfb2_osns_2.int16
    :field flash_burst_data_lfb2_osns_3: equisat_frame.data_section.lfb2_osns_3.int16
    :field flash_burst_data_lfb2_osns_4: equisat_frame.data_section.lfb2_osns_4.int16
    :field flash_burst_data_lfb2_osns_5: equisat_frame.data_section.lfb2_osns_5.int16
    :field flash_burst_data_lfb2_osns_6: equisat_frame.data_section.lfb2_osns_6.int16
    :field flash_burst_data_lf1_ref_0: equisat_frame.data_section.lf1_ref_0.int16
    :field flash_burst_data_lf1_ref_1: equisat_frame.data_section.lf1_ref_1.int16
    :field flash_burst_data_lf1_ref_2: equisat_frame.data_section.lf1_ref_2.int16
    :field flash_burst_data_lf1_ref_3: equisat_frame.data_section.lf1_ref_3.int16
    :field flash_burst_data_lf1_ref_4: equisat_frame.data_section.lf1_ref_4.int16
    :field flash_burst_data_lf1_ref_5: equisat_frame.data_section.lf1_ref_5.int16
    :field flash_burst_data_lf1_ref_6: equisat_frame.data_section.lf1_ref_6.int16
    :field flash_burst_data_lf2_ref_0: equisat_frame.data_section.lf2_ref_0.int16
    :field flash_burst_data_lf2_ref_1: equisat_frame.data_section.lf2_ref_1.int16
    :field flash_burst_data_lf2_ref_2: equisat_frame.data_section.lf2_ref_2.int16
    :field flash_burst_data_lf2_ref_3: equisat_frame.data_section.lf2_ref_3.int16
    :field flash_burst_data_lf2_ref_4: equisat_frame.data_section.lf2_ref_4.int16
    :field flash_burst_data_lf2_ref_5: equisat_frame.data_section.lf2_ref_5.int16
    :field flash_burst_data_lf2_ref_6: equisat_frame.data_section.lf2_ref_6.int16
    :field flash_burst_data_lf3_ref_0: equisat_frame.data_section.lf3_ref_0.int16
    :field flash_burst_data_lf3_ref_1: equisat_frame.data_section.lf3_ref_1.int16
    :field flash_burst_data_lf3_ref_2: equisat_frame.data_section.lf3_ref_2.int16
    :field flash_burst_data_lf3_ref_3: equisat_frame.data_section.lf3_ref_3.int16
    :field flash_burst_data_lf3_ref_4: equisat_frame.data_section.lf3_ref_4.int16
    :field flash_burst_data_lf3_ref_5: equisat_frame.data_section.lf3_ref_5.int16
    :field flash_burst_data_lf3_ref_6: equisat_frame.data_section.lf3_ref_6.int16
    :field flash_burst_data_lf4_ref_0: equisat_frame.data_section.lf4_ref_0.int16
    :field flash_burst_data_lf4_ref_1: equisat_frame.data_section.lf4_ref_1.int16
    :field flash_burst_data_lf4_ref_2: equisat_frame.data_section.lf4_ref_2.int16
    :field flash_burst_data_lf4_ref_3: equisat_frame.data_section.lf4_ref_3.int16
    :field flash_burst_data_lf4_ref_4: equisat_frame.data_section.lf4_ref_4.int16
    :field flash_burst_data_lf4_ref_5: equisat_frame.data_section.lf4_ref_5.int16
    :field flash_burst_data_lf4_ref_6: equisat_frame.data_section.lf4_ref_6.int16
    :field flash_burst_data_led1_sns_0: equisat_frame.data_section.led1_sns_0.int16
    :field flash_burst_data_led1_sns_1: equisat_frame.data_section.led1_sns_1.int16
    :field flash_burst_data_led1_sns_2: equisat_frame.data_section.led1_sns_2.int16
    :field flash_burst_data_led1_sns_3: equisat_frame.data_section.led1_sns_3.int16
    :field flash_burst_data_led1_sns_4: equisat_frame.data_section.led1_sns_4.int16
    :field flash_burst_data_led1_sns_5: equisat_frame.data_section.led1_sns_5.int16
    :field flash_burst_data_led1_sns_6: equisat_frame.data_section.led1_sns_6.int16
    :field flash_burst_data_led2_sns_0: equisat_frame.data_section.led2_sns_0.int16
    :field flash_burst_data_led2_sns_1: equisat_frame.data_section.led2_sns_1.int16
    :field flash_burst_data_led2_sns_2: equisat_frame.data_section.led2_sns_2.int16
    :field flash_burst_data_led2_sns_3: equisat_frame.data_section.led2_sns_3.int16
    :field flash_burst_data_led2_sns_4: equisat_frame.data_section.led2_sns_4.int16
    :field flash_burst_data_led2_sns_5: equisat_frame.data_section.led2_sns_5.int16
    :field flash_burst_data_led2_sns_6: equisat_frame.data_section.led2_sns_6.int16
    :field flash_burst_data_led3_sns_0: equisat_frame.data_section.led3_sns_0.int16
    :field flash_burst_data_led3_sns_1: equisat_frame.data_section.led3_sns_1.int16
    :field flash_burst_data_led3_sns_2: equisat_frame.data_section.led3_sns_2.int16
    :field flash_burst_data_led3_sns_3: equisat_frame.data_section.led3_sns_3.int16
    :field flash_burst_data_led3_sns_4: equisat_frame.data_section.led3_sns_4.int16
    :field flash_burst_data_led3_sns_5: equisat_frame.data_section.led3_sns_5.int16
    :field flash_burst_data_led3_sns_6: equisat_frame.data_section.led3_sns_6.int16
    :field flash_burst_data_led4_sns_0: equisat_frame.data_section.led4_sns_0.int16
    :field flash_burst_data_led4_sns_1: equisat_frame.data_section.led4_sns_1.int16
    :field flash_burst_data_led4_sns_2: equisat_frame.data_section.led4_sns_2.int16
    :field flash_burst_data_led4_sns_3: equisat_frame.data_section.led4_sns_3.int16
    :field flash_burst_data_led4_sns_4: equisat_frame.data_section.led4_sns_4.int16
    :field flash_burst_data_led4_sns_5: equisat_frame.data_section.led4_sns_5.int16
    :field flash_burst_data_led4_sns_6: equisat_frame.data_section.led4_sns_6.int16
    :field flash_burst_data_gyroscope_x_0: equisat_frame.data_section.gyroscope_x_0.int16
    :field flash_burst_data_gyroscope_x_1: equisat_frame.data_section.gyroscope_x_1.int16
    :field flash_burst_data_gyroscope_x_2: equisat_frame.data_section.gyroscope_x_2.int16
    :field flash_burst_data_gyroscope_x_3: equisat_frame.data_section.gyroscope_x_3.int16
    :field flash_burst_data_gyroscope_x_4: equisat_frame.data_section.gyroscope_x_4.int16
    :field flash_burst_data_gyroscope_x_5: equisat_frame.data_section.gyroscope_x_5.int16
    :field flash_burst_data_gyroscope_x_6: equisat_frame.data_section.gyroscope_x_6.int16
    :field flash_burst_data_gyroscope_z_0: equisat_frame.data_section.gyroscope_z_0.int16
    :field flash_burst_data_gyroscope_z_1: equisat_frame.data_section.gyroscope_z_1.int16
    :field flash_burst_data_gyroscope_z_2: equisat_frame.data_section.gyroscope_z_2.int16
    :field flash_burst_data_gyroscope_z_3: equisat_frame.data_section.gyroscope_z_3.int16
    :field flash_burst_data_gyroscope_z_4: equisat_frame.data_section.gyroscope_z_4.int16
    :field flash_burst_data_gyroscope_z_5: equisat_frame.data_section.gyroscope_z_5.int16
    :field flash_burst_data_gyroscope_z_6: equisat_frame.data_section.gyroscope_z_6.int16
    :field flash_burst_data_gyroscope_y_0: equisat_frame.data_section.gyroscope_y_0.int16
    :field flash_burst_data_gyroscope_y_1: equisat_frame.data_section.gyroscope_y_1.int16
    :field flash_burst_data_gyroscope_y_2: equisat_frame.data_section.gyroscope_y_2.int16
    :field flash_burst_data_gyroscope_y_3: equisat_frame.data_section.gyroscope_y_3.int16
    :field flash_burst_data_gyroscope_y_4: equisat_frame.data_section.gyroscope_y_4.int16
    :field flash_burst_data_gyroscope_y_5: equisat_frame.data_section.gyroscope_y_5.int16
    :field flash_burst_data_gyroscope_y_6: equisat_frame.data_section.gyroscope_y_6.int16
    :field flash_cmp_batch_0_led1_temp: equisat_frame.data_section.flash_cmp_batch_0.led1_temp.int16
    :field flash_cmp_batch_0_led2_temp: equisat_frame.data_section.flash_cmp_batch_0.led2_temp.int16
    :field flash_cmp_batch_0_led3_temp: equisat_frame.data_section.flash_cmp_batch_0.led3_temp.int16
    :field flash_cmp_batch_0_led4_temp: equisat_frame.data_section.flash_cmp_batch_0.led4_temp.int16
    :field flash_cmp_batch_0_lf1_temp: equisat_frame.data_section.flash_cmp_batch_0.lf1_temp.int16
    :field flash_cmp_batch_0_lf3_temp: equisat_frame.data_section.flash_cmp_batch_0.lf3_temp.int16
    :field flash_cmp_batch_0_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_0.lfb1_sns.int16
    :field flash_cmp_batch_0_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_0.lfb1_osns.int16
    :field flash_cmp_batch_0_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_0.lfb2_sns.int16
    :field flash_cmp_batch_0_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_0.lfb2_osns.int16
    :field flash_cmp_batch_0_lf1_ref: equisat_frame.data_section.flash_cmp_batch_0.lf1_ref.int16
    :field flash_cmp_batch_0_lf2_ref: equisat_frame.data_section.flash_cmp_batch_0.lf2_ref.int16
    :field flash_cmp_batch_0_lf3_ref: equisat_frame.data_section.flash_cmp_batch_0.lf3_ref.int16
    :field flash_cmp_batch_0_lf4_ref: equisat_frame.data_section.flash_cmp_batch_0.lf4_ref.int16
    :field flash_cmp_batch_0_led1_sns: equisat_frame.data_section.flash_cmp_batch_0.led1_sns.int16
    :field flash_cmp_batch_0_led2_sns: equisat_frame.data_section.flash_cmp_batch_0.led2_sns.int16
    :field flash_cmp_batch_0_led3_sns: equisat_frame.data_section.flash_cmp_batch_0.led3_sns.int16
    :field flash_cmp_batch_0_led4_sns: equisat_frame.data_section.flash_cmp_batch_0.led4_sns.int16
    :field flash_cmp_batch_0_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_0.magnetometer_x.int16
    :field flash_cmp_batch_0_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_0.magnetometer_z.int16
    :field flash_cmp_batch_0_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_0.magnetometer_y.int16
    :field flash_cmp_batch_0_timestamp: equisat_frame.data_section.flash_cmp_batch_0.timestamp
    :field flash_cmp_batch_1_led1_temp: equisat_frame.data_section.flash_cmp_batch_1.led1_temp.int16
    :field flash_cmp_batch_1_led2_temp: equisat_frame.data_section.flash_cmp_batch_1.led2_temp.int16
    :field flash_cmp_batch_1_led3_temp: equisat_frame.data_section.flash_cmp_batch_1.led3_temp.int16
    :field flash_cmp_batch_1_led4_temp: equisat_frame.data_section.flash_cmp_batch_1.led4_temp.int16
    :field flash_cmp_batch_1_lf1_temp: equisat_frame.data_section.flash_cmp_batch_1.lf1_temp.int16
    :field flash_cmp_batch_1_lf3_temp: equisat_frame.data_section.flash_cmp_batch_1.lf3_temp.int16
    :field flash_cmp_batch_1_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_1.lfb1_sns.int16
    :field flash_cmp_batch_1_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_1.lfb1_osns.int16
    :field flash_cmp_batch_1_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_1.lfb2_sns.int16
    :field flash_cmp_batch_1_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_1.lfb2_osns.int16
    :field flash_cmp_batch_1_lf1_ref: equisat_frame.data_section.flash_cmp_batch_1.lf1_ref.int16
    :field flash_cmp_batch_1_lf2_ref: equisat_frame.data_section.flash_cmp_batch_1.lf2_ref.int16
    :field flash_cmp_batch_1_lf3_ref: equisat_frame.data_section.flash_cmp_batch_1.lf3_ref.int16
    :field flash_cmp_batch_1_lf4_ref: equisat_frame.data_section.flash_cmp_batch_1.lf4_ref.int16
    :field flash_cmp_batch_1_led1_sns: equisat_frame.data_section.flash_cmp_batch_1.led1_sns.int16
    :field flash_cmp_batch_1_led2_sns: equisat_frame.data_section.flash_cmp_batch_1.led2_sns.int16
    :field flash_cmp_batch_1_led3_sns: equisat_frame.data_section.flash_cmp_batch_1.led3_sns.int16
    :field flash_cmp_batch_1_led4_sns: equisat_frame.data_section.flash_cmp_batch_1.led4_sns.int16
    :field flash_cmp_batch_1_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_1.magnetometer_x.int16
    :field flash_cmp_batch_1_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_1.magnetometer_z.int16
    :field flash_cmp_batch_1_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_1.magnetometer_y.int16
    :field flash_cmp_batch_1_timestamp: equisat_frame.data_section.flash_cmp_batch_1.timestamp
    :field flash_cmp_batch_2_led1_temp: equisat_frame.data_section.flash_cmp_batch_2.led1_temp.int16
    :field flash_cmp_batch_2_led2_temp: equisat_frame.data_section.flash_cmp_batch_2.led2_temp.int16
    :field flash_cmp_batch_2_led3_temp: equisat_frame.data_section.flash_cmp_batch_2.led3_temp.int16
    :field flash_cmp_batch_2_led4_temp: equisat_frame.data_section.flash_cmp_batch_2.led4_temp.int16
    :field flash_cmp_batch_2_lf1_temp: equisat_frame.data_section.flash_cmp_batch_2.lf1_temp.int16
    :field flash_cmp_batch_2_lf3_temp: equisat_frame.data_section.flash_cmp_batch_2.lf3_temp.int16
    :field flash_cmp_batch_2_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_2.lfb1_sns.int16
    :field flash_cmp_batch_2_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_2.lfb1_osns.int16
    :field flash_cmp_batch_2_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_2.lfb2_sns.int16
    :field flash_cmp_batch_2_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_2.lfb2_osns.int16
    :field flash_cmp_batch_2_lf1_ref: equisat_frame.data_section.flash_cmp_batch_2.lf1_ref.int16
    :field flash_cmp_batch_2_lf2_ref: equisat_frame.data_section.flash_cmp_batch_2.lf2_ref.int16
    :field flash_cmp_batch_2_lf3_ref: equisat_frame.data_section.flash_cmp_batch_2.lf3_ref.int16
    :field flash_cmp_batch_2_lf4_ref: equisat_frame.data_section.flash_cmp_batch_2.lf4_ref.int16
    :field flash_cmp_batch_2_led1_sns: equisat_frame.data_section.flash_cmp_batch_2.led1_sns.int16
    :field flash_cmp_batch_2_led2_sns: equisat_frame.data_section.flash_cmp_batch_2.led2_sns.int16
    :field flash_cmp_batch_2_led3_sns: equisat_frame.data_section.flash_cmp_batch_2.led3_sns.int16
    :field flash_cmp_batch_2_led4_sns: equisat_frame.data_section.flash_cmp_batch_2.led4_sns.int16
    :field flash_cmp_batch_2_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_2.magnetometer_x.int16
    :field flash_cmp_batch_2_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_2.magnetometer_z.int16
    :field flash_cmp_batch_2_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_2.magnetometer_y.int16
    :field flash_cmp_batch_2_timestamp: equisat_frame.data_section.flash_cmp_batch_2.timestamp
    :field flash_cmp_batch_3_led1_temp: equisat_frame.data_section.flash_cmp_batch_3.led1_temp.int16
    :field flash_cmp_batch_3_led2_temp: equisat_frame.data_section.flash_cmp_batch_3.led2_temp.int16
    :field flash_cmp_batch_3_led3_temp: equisat_frame.data_section.flash_cmp_batch_3.led3_temp.int16
    :field flash_cmp_batch_3_led4_temp: equisat_frame.data_section.flash_cmp_batch_3.led4_temp.int16
    :field flash_cmp_batch_3_lf1_temp: equisat_frame.data_section.flash_cmp_batch_3.lf1_temp.int16
    :field flash_cmp_batch_3_lf3_temp: equisat_frame.data_section.flash_cmp_batch_3.lf3_temp.int16
    :field flash_cmp_batch_3_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_3.lfb1_sns.int16
    :field flash_cmp_batch_3_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_3.lfb1_osns.int16
    :field flash_cmp_batch_3_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_3.lfb2_sns.int16
    :field flash_cmp_batch_3_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_3.lfb2_osns.int16
    :field flash_cmp_batch_3_lf1_ref: equisat_frame.data_section.flash_cmp_batch_3.lf1_ref.int16
    :field flash_cmp_batch_3_lf2_ref: equisat_frame.data_section.flash_cmp_batch_3.lf2_ref.int16
    :field flash_cmp_batch_3_lf3_ref: equisat_frame.data_section.flash_cmp_batch_3.lf3_ref.int16
    :field flash_cmp_batch_3_lf4_ref: equisat_frame.data_section.flash_cmp_batch_3.lf4_ref.int16
    :field flash_cmp_batch_3_led1_sns: equisat_frame.data_section.flash_cmp_batch_3.led1_sns.int16
    :field flash_cmp_batch_3_led2_sns: equisat_frame.data_section.flash_cmp_batch_3.led2_sns.int16
    :field flash_cmp_batch_3_led3_sns: equisat_frame.data_section.flash_cmp_batch_3.led3_sns.int16
    :field flash_cmp_batch_3_led4_sns: equisat_frame.data_section.flash_cmp_batch_3.led4_sns.int16
    :field flash_cmp_batch_3_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_3.magnetometer_x.int16
    :field flash_cmp_batch_3_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_3.magnetometer_z.int16
    :field flash_cmp_batch_3_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_3.magnetometer_y.int16
    :field flash_cmp_batch_3_timestamp: equisat_frame.data_section.flash_cmp_batch_3.timestamp
    :field flash_cmp_batch_4_led1_temp: equisat_frame.data_section.flash_cmp_batch_4.led1_temp.int16
    :field flash_cmp_batch_4_led2_temp: equisat_frame.data_section.flash_cmp_batch_4.led2_temp.int16
    :field flash_cmp_batch_4_led3_temp: equisat_frame.data_section.flash_cmp_batch_4.led3_temp.int16
    :field flash_cmp_batch_4_led4_temp: equisat_frame.data_section.flash_cmp_batch_4.led4_temp.int16
    :field flash_cmp_batch_4_lf1_temp: equisat_frame.data_section.flash_cmp_batch_4.lf1_temp.int16
    :field flash_cmp_batch_4_lf3_temp: equisat_frame.data_section.flash_cmp_batch_4.lf3_temp.int16
    :field flash_cmp_batch_4_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_4.lfb1_sns.int16
    :field flash_cmp_batch_4_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_4.lfb1_osns.int16
    :field flash_cmp_batch_4_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_4.lfb2_sns.int16
    :field flash_cmp_batch_4_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_4.lfb2_osns.int16
    :field flash_cmp_batch_4_lf1_ref: equisat_frame.data_section.flash_cmp_batch_4.lf1_ref.int16
    :field flash_cmp_batch_4_lf2_ref: equisat_frame.data_section.flash_cmp_batch_4.lf2_ref.int16
    :field flash_cmp_batch_4_lf3_ref: equisat_frame.data_section.flash_cmp_batch_4.lf3_ref.int16
    :field flash_cmp_batch_4_lf4_ref: equisat_frame.data_section.flash_cmp_batch_4.lf4_ref.int16
    :field flash_cmp_batch_4_led1_sns: equisat_frame.data_section.flash_cmp_batch_4.led1_sns.int16
    :field flash_cmp_batch_4_led2_sns: equisat_frame.data_section.flash_cmp_batch_4.led2_sns.int16
    :field flash_cmp_batch_4_led3_sns: equisat_frame.data_section.flash_cmp_batch_4.led3_sns.int16
    :field flash_cmp_batch_4_led4_sns: equisat_frame.data_section.flash_cmp_batch_4.led4_sns.int16
    :field flash_cmp_batch_4_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_4.magnetometer_x.int16
    :field flash_cmp_batch_4_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_4.magnetometer_z.int16
    :field flash_cmp_batch_4_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_4.magnetometer_y.int16
    :field flash_cmp_batch_4_timestamp: equisat_frame.data_section.flash_cmp_batch_4.timestamp
    :field flash_cmp_batch_5_led1_temp: equisat_frame.data_section.flash_cmp_batch_5.led1_temp.int16
    :field flash_cmp_batch_5_led2_temp: equisat_frame.data_section.flash_cmp_batch_5.led2_temp.int16
    :field flash_cmp_batch_5_led3_temp: equisat_frame.data_section.flash_cmp_batch_5.led3_temp.int16
    :field flash_cmp_batch_5_led4_temp: equisat_frame.data_section.flash_cmp_batch_5.led4_temp.int16
    :field flash_cmp_batch_5_lf1_temp: equisat_frame.data_section.flash_cmp_batch_5.lf1_temp.int16
    :field flash_cmp_batch_5_lf3_temp: equisat_frame.data_section.flash_cmp_batch_5.lf3_temp.int16
    :field flash_cmp_batch_5_lfb1_sns: equisat_frame.data_section.flash_cmp_batch_5.lfb1_sns.int16
    :field flash_cmp_batch_5_lfb1_osns: equisat_frame.data_section.flash_cmp_batch_5.lfb1_osns.int16
    :field flash_cmp_batch_5_lfb2_sns: equisat_frame.data_section.flash_cmp_batch_5.lfb2_sns.int16
    :field flash_cmp_batch_5_lfb2_osns: equisat_frame.data_section.flash_cmp_batch_5.lfb2_osns.int16
    :field flash_cmp_batch_5_lf1_ref: equisat_frame.data_section.flash_cmp_batch_5.lf1_ref.int16
    :field flash_cmp_batch_5_lf2_ref: equisat_frame.data_section.flash_cmp_batch_5.lf2_ref.int16
    :field flash_cmp_batch_5_lf3_ref: equisat_frame.data_section.flash_cmp_batch_5.lf3_ref.int16
    :field flash_cmp_batch_5_lf4_ref: equisat_frame.data_section.flash_cmp_batch_5.lf4_ref.int16
    :field flash_cmp_batch_5_led1_sns: equisat_frame.data_section.flash_cmp_batch_5.led1_sns.int16
    :field flash_cmp_batch_5_led2_sns: equisat_frame.data_section.flash_cmp_batch_5.led2_sns.int16
    :field flash_cmp_batch_5_led3_sns: equisat_frame.data_section.flash_cmp_batch_5.led3_sns.int16
    :field flash_cmp_batch_5_led4_sns: equisat_frame.data_section.flash_cmp_batch_5.led4_sns.int16
    :field flash_cmp_batch_5_magnetometer_x: equisat_frame.data_section.flash_cmp_batch_5.magnetometer_x.int16
    :field flash_cmp_batch_5_magnetometer_z: equisat_frame.data_section.flash_cmp_batch_5.magnetometer_z.int16
    :field flash_cmp_batch_5_magnetometer_y: equisat_frame.data_section.flash_cmp_batch_5.magnetometer_y.int16
    :field flash_cmp_batch_5_timestamp: equisat_frame.data_section.flash_cmp_batch_5.timestamp
    :field lowpower_batch_0_event_history: equisat_frame.data_section.lowpower_batch_0.event_history
    :field lowpower_batch_0_l1_ref: equisat_frame.data_section.lowpower_batch_0.l1_ref.int16
    :field lowpower_batch_0_l2_ref: equisat_frame.data_section.lowpower_batch_0.l2_ref.int16
    :field lowpower_batch_0_l1_sns: equisat_frame.data_section.lowpower_batch_0.l1_sns.int16
    :field lowpower_batch_0_l2_sns: equisat_frame.data_section.lowpower_batch_0.l2_sns.int16
    :field lowpower_batch_0_l1_temp: equisat_frame.data_section.lowpower_batch_0.l1_temp.int16
    :field lowpower_batch_0_l2_temp: equisat_frame.data_section.lowpower_batch_0.l2_temp.int16
    :field lowpower_batch_0_panel_ref: equisat_frame.data_section.lowpower_batch_0.panel_ref.int16
    :field lowpower_batch_0_l_ref: equisat_frame.data_section.lowpower_batch_0.l_ref.int16
    :field lowpower_batch_0_bat_digsigs_1: equisat_frame.data_section.lowpower_batch_0.bat_digsigs_1
    :field lowpower_batch_0_bat_digsigs_2: equisat_frame.data_section.lowpower_batch_0.bat_digsigs_2
    :field lowpower_batch_0_ir_flash_obj: equisat_frame.data_section.lowpower_batch_0.ir_flash_obj
    :field lowpower_batch_0_ir_side1_obj: equisat_frame.data_section.lowpower_batch_0.ir_side1_obj
    :field lowpower_batch_0_ir_side2_obj: equisat_frame.data_section.lowpower_batch_0.ir_side2_obj
    :field lowpower_batch_0_ir_rbf_obj: equisat_frame.data_section.lowpower_batch_0.ir_rbf_obj
    :field lowpower_batch_0_ir_access_obj: equisat_frame.data_section.lowpower_batch_0.ir_access_obj
    :field lowpower_batch_0_ir_top1_obj: equisat_frame.data_section.lowpower_batch_0.ir_top1_obj
    :field lowpower_batch_0_gyroscope_x: equisat_frame.data_section.lowpower_batch_0.gyroscope_x.int16
    :field lowpower_batch_0_gyroscope_z: equisat_frame.data_section.lowpower_batch_0.gyroscope_z.int16
    :field lowpower_batch_0_gyroscope_y: equisat_frame.data_section.lowpower_batch_0.gyroscope_y.int16
    :field lowpower_batch_1_event_history: equisat_frame.data_section.lowpower_batch_1.event_history
    :field lowpower_batch_1_l1_ref: equisat_frame.data_section.lowpower_batch_1.l1_ref.int16
    :field lowpower_batch_1_l2_ref: equisat_frame.data_section.lowpower_batch_1.l2_ref.int16
    :field lowpower_batch_1_l1_sns: equisat_frame.data_section.lowpower_batch_1.l1_sns.int16
    :field lowpower_batch_1_l2_sns: equisat_frame.data_section.lowpower_batch_1.l2_sns.int16
    :field lowpower_batch_1_l1_temp: equisat_frame.data_section.lowpower_batch_1.l1_temp.int16
    :field lowpower_batch_1_l2_temp: equisat_frame.data_section.lowpower_batch_1.l2_temp.int16
    :field lowpower_batch_1_panel_ref: equisat_frame.data_section.lowpower_batch_1.panel_ref.int16
    :field lowpower_batch_1_l_ref: equisat_frame.data_section.lowpower_batch_1.l_ref.int16
    :field lowpower_batch_1_bat_digsigs_1: equisat_frame.data_section.lowpower_batch_1.bat_digsigs_1
    :field lowpower_batch_1_bat_digsigs_2: equisat_frame.data_section.lowpower_batch_1.bat_digsigs_2
    :field lowpower_batch_1_ir_flash_obj: equisat_frame.data_section.lowpower_batch_1.ir_flash_obj
    :field lowpower_batch_1_ir_side1_obj: equisat_frame.data_section.lowpower_batch_1.ir_side1_obj
    :field lowpower_batch_1_ir_side2_obj: equisat_frame.data_section.lowpower_batch_1.ir_side2_obj
    :field lowpower_batch_1_ir_rbf_obj: equisat_frame.data_section.lowpower_batch_1.ir_rbf_obj
    :field lowpower_batch_1_ir_access_obj: equisat_frame.data_section.lowpower_batch_1.ir_access_obj
    :field lowpower_batch_1_ir_top1_obj: equisat_frame.data_section.lowpower_batch_1.ir_top1_obj
    :field lowpower_batch_1_gyroscope_x: equisat_frame.data_section.lowpower_batch_1.gyroscope_x.int16
    :field lowpower_batch_1_gyroscope_z: equisat_frame.data_section.lowpower_batch_1.gyroscope_z.int16
    :field lowpower_batch_1_gyroscope_y: equisat_frame.data_section.lowpower_batch_1.gyroscope_y.int16
    :field lowpower_batch_2_event_history: equisat_frame.data_section.lowpower_batch_2.event_history
    :field lowpower_batch_2_l1_ref: equisat_frame.data_section.lowpower_batch_2.l1_ref.int16
    :field lowpower_batch_2_l2_ref: equisat_frame.data_section.lowpower_batch_2.l2_ref.int16
    :field lowpower_batch_2_l1_sns: equisat_frame.data_section.lowpower_batch_2.l1_sns.int16
    :field lowpower_batch_2_l2_sns: equisat_frame.data_section.lowpower_batch_2.l2_sns.int16
    :field lowpower_batch_2_l1_temp: equisat_frame.data_section.lowpower_batch_2.l1_temp.int16
    :field lowpower_batch_2_l2_temp: equisat_frame.data_section.lowpower_batch_2.l2_temp.int16
    :field lowpower_batch_2_panel_ref: equisat_frame.data_section.lowpower_batch_2.panel_ref.int16
    :field lowpower_batch_2_l_ref: equisat_frame.data_section.lowpower_batch_2.l_ref.int16
    :field lowpower_batch_2_bat_digsigs_1: equisat_frame.data_section.lowpower_batch_2.bat_digsigs_1
    :field lowpower_batch_2_bat_digsigs_2: equisat_frame.data_section.lowpower_batch_2.bat_digsigs_2
    :field lowpower_batch_2_ir_flash_obj: equisat_frame.data_section.lowpower_batch_2.ir_flash_obj
    :field lowpower_batch_2_ir_side1_obj: equisat_frame.data_section.lowpower_batch_2.ir_side1_obj
    :field lowpower_batch_2_ir_side2_obj: equisat_frame.data_section.lowpower_batch_2.ir_side2_obj
    :field lowpower_batch_2_ir_rbf_obj: equisat_frame.data_section.lowpower_batch_2.ir_rbf_obj
    :field lowpower_batch_2_ir_access_obj: equisat_frame.data_section.lowpower_batch_2.ir_access_obj
    :field lowpower_batch_2_ir_top1_obj: equisat_frame.data_section.lowpower_batch_2.ir_top1_obj
    :field lowpower_batch_2_gyroscope_x: equisat_frame.data_section.lowpower_batch_2.gyroscope_x.int16
    :field lowpower_batch_2_gyroscope_z: equisat_frame.data_section.lowpower_batch_2.gyroscope_z.int16
    :field lowpower_batch_2_gyroscope_y: equisat_frame.data_section.lowpower_batch_2.gyroscope_y.int16
    :field lowpower_batch_3_event_history: equisat_frame.data_section.lowpower_batch_3.event_history
    :field lowpower_batch_3_l1_ref: equisat_frame.data_section.lowpower_batch_3.l1_ref.int16
    :field lowpower_batch_3_l2_ref: equisat_frame.data_section.lowpower_batch_3.l2_ref.int16
    :field lowpower_batch_3_l1_sns: equisat_frame.data_section.lowpower_batch_3.l1_sns.int16
    :field lowpower_batch_3_l2_sns: equisat_frame.data_section.lowpower_batch_3.l2_sns.int16
    :field lowpower_batch_3_l1_temp: equisat_frame.data_section.lowpower_batch_3.l1_temp.int16
    :field lowpower_batch_3_l2_temp: equisat_frame.data_section.lowpower_batch_3.l2_temp.int16
    :field lowpower_batch_3_panel_ref: equisat_frame.data_section.lowpower_batch_3.panel_ref.int16
    :field lowpower_batch_3_l_ref: equisat_frame.data_section.lowpower_batch_3.l_ref.int16
    :field lowpower_batch_3_bat_digsigs_1: equisat_frame.data_section.lowpower_batch_3.bat_digsigs_1
    :field lowpower_batch_3_bat_digsigs_2: equisat_frame.data_section.lowpower_batch_3.bat_digsigs_2
    :field lowpower_batch_3_ir_flash_obj: equisat_frame.data_section.lowpower_batch_3.ir_flash_obj
    :field lowpower_batch_3_ir_side1_obj: equisat_frame.data_section.lowpower_batch_3.ir_side1_obj
    :field lowpower_batch_3_ir_side2_obj: equisat_frame.data_section.lowpower_batch_3.ir_side2_obj
    :field lowpower_batch_3_ir_rbf_obj: equisat_frame.data_section.lowpower_batch_3.ir_rbf_obj
    :field lowpower_batch_3_ir_access_obj: equisat_frame.data_section.lowpower_batch_3.ir_access_obj
    :field lowpower_batch_3_ir_top1_obj: equisat_frame.data_section.lowpower_batch_3.ir_top1_obj
    :field lowpower_batch_3_gyroscope_x: equisat_frame.data_section.lowpower_batch_3.gyroscope_x.int16
    :field lowpower_batch_3_gyroscope_z: equisat_frame.data_section.lowpower_batch_3.gyroscope_z.int16
    :field lowpower_batch_3_gyroscope_y: equisat_frame.data_section.lowpower_batch_3.gyroscope_y.int16
    :field lowpower_batch_4_event_history: equisat_frame.data_section.lowpower_batch_4.event_history
    :field lowpower_batch_4_l1_ref: equisat_frame.data_section.lowpower_batch_4.l1_ref.int16
    :field lowpower_batch_4_l2_ref: equisat_frame.data_section.lowpower_batch_4.l2_ref.int16
    :field lowpower_batch_4_l1_sns: equisat_frame.data_section.lowpower_batch_4.l1_sns.int16
    :field lowpower_batch_4_l2_sns: equisat_frame.data_section.lowpower_batch_4.l2_sns.int16
    :field lowpower_batch_4_l1_temp: equisat_frame.data_section.lowpower_batch_4.l1_temp.int16
    :field lowpower_batch_4_l2_temp: equisat_frame.data_section.lowpower_batch_4.l2_temp.int16
    :field lowpower_batch_4_panel_ref: equisat_frame.data_section.lowpower_batch_4.panel_ref.int16
    :field lowpower_batch_4_l_ref: equisat_frame.data_section.lowpower_batch_4.l_ref.int16
    :field lowpower_batch_4_bat_digsigs_1: equisat_frame.data_section.lowpower_batch_4.bat_digsigs_1
    :field lowpower_batch_4_bat_digsigs_2: equisat_frame.data_section.lowpower_batch_4.bat_digsigs_2
    :field lowpower_batch_4_ir_flash_obj: equisat_frame.data_section.lowpower_batch_4.ir_flash_obj
    :field lowpower_batch_4_ir_side1_obj: equisat_frame.data_section.lowpower_batch_4.ir_side1_obj
    :field lowpower_batch_4_ir_side2_obj: equisat_frame.data_section.lowpower_batch_4.ir_side2_obj
    :field lowpower_batch_4_ir_rbf_obj: equisat_frame.data_section.lowpower_batch_4.ir_rbf_obj
    :field lowpower_batch_4_ir_access_obj: equisat_frame.data_section.lowpower_batch_4.ir_access_obj
    :field lowpower_batch_4_ir_top1_obj: equisat_frame.data_section.lowpower_batch_4.ir_top1_obj
    :field lowpower_batch_4_gyroscope_x: equisat_frame.data_section.lowpower_batch_4.gyroscope_x.int16
    :field lowpower_batch_4_gyroscope_z: equisat_frame.data_section.lowpower_batch_4.gyroscope_z.int16
    :field lowpower_batch_4_gyroscope_y: equisat_frame.data_section.lowpower_batch_4.gyroscope_y.int16
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.equisat_frame = Equisat.EquisatFrameT(self._io, self, self._root)

    class CompressedMagnetometerT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 11 - 2800)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedImuTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 1 - 20374)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedGyroscopeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 1 - 32750)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CurrentInfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_to_flash = self._io.read_u1()
            self.boot_count = self._io.read_u1()
            self.l1_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l2_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l1_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l2_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l1_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.l2_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.panel_ref = Equisat.CompressedPanelrefT(self._io, self, self._root)
            self.l_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.bat_digsigs_1 = self._io.read_u1()
            self.bat_digsigs_2 = self._io.read_u1()
            self.lf1ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.lf2ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.lf3ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.lf4ref = Equisat.CompressedLRefT(self._io, self, self._root)


    class CompressedLedSnsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 650 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class EquisatFrameT(KaitaiStruct):

        class SatState(Enum):
            initial = 0
            antenna_deploy = 1
            hello_world = 2
            idle_no_flash = 3
            idle_flash = 4
            low_power = 5

        class MessageType(Enum):
            idle = 0
            attitude = 1
            flash_burst = 2
            flash_cmp = 3
            low_power = 4
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_preamble = self._io.read_bytes(13)
            _io__raw_preamble = KaitaiStream(BytesIO(self._raw_preamble))
            self.preamble = Equisat.PreambleT(_io__raw_preamble, self, self._root)
            self._raw_current_info = self._io.read_bytes(16)
            _io__raw_current_info = KaitaiStream(BytesIO(self._raw_current_info))
            self.current_info = Equisat.CurrentInfoT(_io__raw_current_info, self, self._root)
            _on = self.preamble.message_type
            if _on == 0:
                self.data_section = Equisat.IdleDataT(self._io, self, self._root)
            elif _on == 4:
                self.data_section = Equisat.LowpowerDataT(self._io, self, self._root)
            elif _on == 1:
                self.data_section = Equisat.AttitudeDataT(self._io, self, self._root)
            elif _on == 3:
                self.data_section = Equisat.FlashCmpDataT(self._io, self, self._root)
            elif _on == 2:
                self.data_section = Equisat.FlashBurstDataT(self._io, self, self._root)
            self.unparsed = self._io.read_bytes_full()


    class LowpowerDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lowpower_batch_0 = Equisat.LowpowerBatchT(self._io, self, self._root)
            self.lowpower_batch_1 = Equisat.LowpowerBatchT(self._io, self, self._root)
            self.lowpower_batch_2 = Equisat.LowpowerBatchT(self._io, self, self._root)
            self.lowpower_batch_3 = Equisat.LowpowerBatchT(self._io, self, self._root)
            self.lowpower_batch_4 = Equisat.LowpowerBatchT(self._io, self, self._root)


    class CompressedLfbSnsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 45 - -960)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class FlashCmpDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flash_cmp_batch_0 = Equisat.FlashCmpBatchT(self._io, self, self._root)
            self.flash_cmp_batch_1 = Equisat.FlashCmpBatchT(self._io, self, self._root)
            self.flash_cmp_batch_2 = Equisat.FlashCmpBatchT(self._io, self, self._root)
            self.flash_cmp_batch_3 = Equisat.FlashCmpBatchT(self._io, self, self._root)
            self.flash_cmp_batch_4 = Equisat.FlashCmpBatchT(self._io, self, self._root)
            self.flash_cmp_batch_5 = Equisat.FlashCmpBatchT(self._io, self, self._root)


    class CallsignStrT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_string = (self._io.read_bytes_full()).decode(u"utf-8")


    class IdleDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idle_batch_0 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_1 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_2 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_3 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_4 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_5 = Equisat.IdleBatchT(self._io, self, self._root)
            self.idle_batch_6 = Equisat.IdleBatchT(self._io, self, self._root)


    class AttitudeBatchT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ir_flash_obj = self._io.read_u2le()
            self.ir_side1_obj = self._io.read_u2le()
            self.ir_side2_obj = self._io.read_u2le()
            self.ir_rbf_obj = self._io.read_u2le()
            self.ir_access_obj = self._io.read_u2le()
            self.ir_top1_obj = self._io.read_u2le()
            self.pd_1 = self._io.read_u1()
            self.pd_2 = self._io.read_u1()
            self.accelerometer1_x = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.accelerometer1_z = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.accelerometer1_y = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.accelerometer2_x = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.accelerometer2_z = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.accelerometer2_y = Equisat.CompressedAccelerometerT(self._io, self, self._root)
            self.gyroscope_x = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.magnetometer1_x = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer1_z = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer1_y = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer2_x = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer2_z = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer2_y = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.timestamp = self._io.read_u4le()

        @property
        def pd_flash(self):
            if hasattr(self, '_m_pd_flash'):
                return self._m_pd_flash if hasattr(self, '_m_pd_flash') else None

            self._m_pd_flash = ((self.pd_1 >> 6) & 3)
            return self._m_pd_flash if hasattr(self, '_m_pd_flash') else None

        @property
        def pd_access(self):
            if hasattr(self, '_m_pd_access'):
                return self._m_pd_access if hasattr(self, '_m_pd_access') else None

            self._m_pd_access = ((self.pd_1 >> 0) & 3)
            return self._m_pd_access if hasattr(self, '_m_pd_access') else None

        @property
        def pd_top2(self):
            if hasattr(self, '_m_pd_top2'):
                return self._m_pd_top2 if hasattr(self, '_m_pd_top2') else None

            self._m_pd_top2 = ((self.pd_2 >> 4) & 3)
            return self._m_pd_top2 if hasattr(self, '_m_pd_top2') else None

        @property
        def pd_top1(self):
            if hasattr(self, '_m_pd_top1'):
                return self._m_pd_top1 if hasattr(self, '_m_pd_top1') else None

            self._m_pd_top1 = ((self.pd_2 >> 6) & 3)
            return self._m_pd_top1 if hasattr(self, '_m_pd_top1') else None

        @property
        def pd_side2(self):
            if hasattr(self, '_m_pd_side2'):
                return self._m_pd_side2 if hasattr(self, '_m_pd_side2') else None

            self._m_pd_side2 = ((self.pd_1 >> 2) & 3)
            return self._m_pd_side2 if hasattr(self, '_m_pd_side2') else None

        @property
        def pd_side1(self):
            if hasattr(self, '_m_pd_side1'):
                return self._m_pd_side1 if hasattr(self, '_m_pd_side1') else None

            self._m_pd_side1 = ((self.pd_1 >> 4) & 3)
            return self._m_pd_side1 if hasattr(self, '_m_pd_side1') else None


    class CompressedLfbOsnsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 72 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class FlashBurstDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.led1_temp_0 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_1 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_2 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_3 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_4 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_5 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led1_temp_6 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_0 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_1 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_2 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_3 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_4 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_5 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp_6 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_0 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_1 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_2 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_3 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_4 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_5 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp_6 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_0 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_1 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_2 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_3 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_4 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_5 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp_6 = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.lf1_temp_0 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_1 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_2 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_3 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_4 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_5 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf1_temp_6 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_0 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_1 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_2 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_3 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_4 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_5 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp_6 = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lfb1_sns_0 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_1 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_2 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_3 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_4 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_5 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_sns_6 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_osns_0 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_1 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_2 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_3 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_4 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_5 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb1_osns_6 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_sns_0 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_1 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_2 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_3 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_4 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_5 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_sns_6 = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_osns_0 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_1 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_2 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_3 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_4 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_5 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_osns_6 = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lf1_ref_0 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_1 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_2 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_3 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_4 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_5 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf1_ref_6 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_0 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_1 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_2 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_3 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_4 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_5 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref_6 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_0 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_1 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_2 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_3 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_4 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_5 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref_6 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_0 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_1 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_2 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_3 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_4 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_5 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref_6 = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.led1_sns_0 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_1 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_2 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_3 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_4 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_5 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led1_sns_6 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_0 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_1 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_2 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_3 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_4 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_5 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns_6 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_0 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_1 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_2 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_3 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_4 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_5 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns_6 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_0 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_1 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_2 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_3 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_4 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_5 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns_6 = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.gyroscope_x_0 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_1 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_2 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_3 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_4 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_5 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_x_6 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_0 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_1 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_2 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_3 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_4 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_5 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z_6 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_0 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_1 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_2 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_3 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_4 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_5 = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y_6 = Equisat.CompressedGyroscopeT(self._io, self, self._root)


    class CompressedPanelrefT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 6 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class PreambleT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.source = self._io.read_bytes(6)
            if not self.source == b"\x57\x4C\x39\x58\x5A\x45":
                raise kaitaistruct.ValidationNotEqualError(b"\x57\x4C\x39\x58\x5A\x45", self.source, self._io, u"/types/preamble_t/seq/0")
            self.timestamp = self._io.read_u4le()
            self.msg_op_states = self._io.read_u1()
            self.bytes_of_data = self._io.read_u1()
            self.num_errors = self._io.read_u1()

        @property
        def satellite_state(self):
            if hasattr(self, '_m_satellite_state'):
                return self._m_satellite_state if hasattr(self, '_m_satellite_state') else None

            self._m_satellite_state = ((self.msg_op_states >> 3) & 7)
            return self._m_satellite_state if hasattr(self, '_m_satellite_state') else None

        @property
        def flash_killed(self):
            if hasattr(self, '_m_flash_killed'):
                return self._m_flash_killed if hasattr(self, '_m_flash_killed') else None

            self._m_flash_killed = (self.msg_op_states & (1 << 6)) // (1 << 6)
            return self._m_flash_killed if hasattr(self, '_m_flash_killed') else None

        @property
        def message_type(self):
            if hasattr(self, '_m_message_type'):
                return self._m_message_type if hasattr(self, '_m_message_type') else None

            self._m_message_type = (self.msg_op_states & 7)
            return self._m_message_type if hasattr(self, '_m_message_type') else None

        @property
        def mram_killed(self):
            if hasattr(self, '_m_mram_killed'):
                return self._m_mram_killed if hasattr(self, '_m_mram_killed') else None

            self._m_mram_killed = (self.msg_op_states & (1 << 7)) // (1 << 7)
            return self._m_mram_killed if hasattr(self, '_m_mram_killed') else None

        @property
        def callsign(self):
            if hasattr(self, '_m_callsign'):
                return self._m_callsign if hasattr(self, '_m_callsign') else None

            self._m_callsign = self.source
            return self._m_callsign if hasattr(self, '_m_callsign') else None


    class LowpowerBatchT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.event_history = self._io.read_u1()
            self.l1_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l2_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l1_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l2_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l1_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.l2_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.panel_ref = Equisat.CompressedPanelrefT(self._io, self, self._root)
            self.l_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.bat_digsigs_1 = self._io.read_u1()
            self.bat_digsigs_2 = self._io.read_u1()
            self.ir_flash_obj = self._io.read_u2le()
            self.ir_side1_obj = self._io.read_u2le()
            self.ir_side2_obj = self._io.read_u2le()
            self.ir_rbf_obj = self._io.read_u2le()
            self.ir_access_obj = self._io.read_u2le()
            self.ir_top1_obj = self._io.read_u2le()
            self.gyroscope_x = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_z = Equisat.CompressedGyroscopeT(self._io, self, self._root)
            self.gyroscope_y = Equisat.CompressedGyroscopeT(self._io, self, self._root)


    class CompressedAccelerometerT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 1 - 32768)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class IdleBatchT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.event_history = self._io.read_u1()
            self.l1_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l2_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.l1_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l2_sns = Equisat.CompressedLSnsT(self._io, self, self._root)
            self.l1_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.l2_temp = Equisat.CompressedLTempT(self._io, self, self._root)
            self.panel_ref = Equisat.CompressedPanelrefT(self._io, self, self._root)
            self.l_ref = Equisat.CompressedLRefT(self._io, self, self._root)
            self.bat_digsigs_1 = self._io.read_u1()
            self.bat_digsigs_2 = self._io.read_u1()
            self.rad_temp = Equisat.CompressedRadTempT(self._io, self, self._root)
            self.imu_temp = Equisat.CompressedImuTempT(self._io, self, self._root)
            self.ir_flash_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.ir_side1_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.ir_side2_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.ir_rbf_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.ir_access_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.ir_top1_amb = Equisat.CompressedIrAmbT(self._io, self, self._root)
            self.timestamp = self._io.read_u4le()


    class CompressedLSnsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 20 - 150)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedLTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 32 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedRadTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 16 - 2000)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedLedTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 32 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedLRefT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 14 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedLfVoltT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 14 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class CompressedLfTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 32 - 0)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class FlashCmpBatchT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.led1_temp = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led2_temp = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led3_temp = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.led4_temp = Equisat.CompressedLedTempT(self._io, self, self._root)
            self.lf1_temp = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lf3_temp = Equisat.CompressedLfTempT(self._io, self, self._root)
            self.lfb1_sns = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb1_osns = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lfb2_sns = Equisat.CompressedLfbSnsT(self._io, self, self._root)
            self.lfb2_osns = Equisat.CompressedLfbOsnsT(self._io, self, self._root)
            self.lf1_ref = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf2_ref = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf3_ref = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.lf4_ref = Equisat.CompressedLfVoltT(self._io, self, self._root)
            self.led1_sns = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led2_sns = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led3_sns = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.led4_sns = Equisat.CompressedLedSnsT(self._io, self, self._root)
            self.magnetometer_x = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer_z = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.magnetometer_y = Equisat.CompressedMagnetometerT(self._io, self, self._root)
            self.timestamp = self._io.read_u4le()


    class CompressedIrAmbT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cint16 = self._io.read_s1()

        @property
        def int16(self):
            if hasattr(self, '_m_int16'):
                return self._m_int16 if hasattr(self, '_m_int16') else None

            self._m_int16 = ((self.cint16 << 8) // 7 - -11657)
            return self._m_int16 if hasattr(self, '_m_int16') else None


    class AttitudeDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.attitude_batch_0 = Equisat.AttitudeBatchT(self._io, self, self._root)
            self.attitude_batch_1 = Equisat.AttitudeBatchT(self._io, self, self._root)
            self.attitude_batch_2 = Equisat.AttitudeBatchT(self._io, self, self._root)
            self.attitude_batch_3 = Equisat.AttitudeBatchT(self._io, self, self._root)
            self.attitude_batch_4 = Equisat.AttitudeBatchT(self._io, self, self._root)


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


