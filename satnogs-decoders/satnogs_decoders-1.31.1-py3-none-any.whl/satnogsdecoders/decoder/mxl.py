# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mxl(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field primary_id: ax25_frame.payload.ax25_info.rap_header.primary_id
    :field secondary_id: ax25_frame.payload.ax25_info.rap_header.secondary_id
    :field flags: ax25_frame.payload.ax25_info.rap_header.flags
    :field packet_length: ax25_frame.payload.ax25_info.rap_header.packet_length
    :field header_checksum: ax25_frame.payload.ax25_info.rap_header.header_checksum
    :field spacecraft: ax25_frame.payload.ax25_info.rap_header.spacecraft
    :field operation_mode: ax25_frame.payload.ax25_info.payload.tbex_beacon.operation_mode
    :field rtc_unix_time: ax25_frame.payload.ax25_info.payload.tbex_beacon.rtc_unix_time
    :field numresets: ax25_frame.payload.ax25_info.payload.tbex_beacon.numresets
    :field avgnumactivetasks1: ax25_frame.payload.ax25_info.payload.tbex_beacon.avgnumactivetasks1
    :field avgnumactivetasks5: ax25_frame.payload.ax25_info.payload.tbex_beacon.avgnumactivetasks5
    :field avgnumactivetasks15: ax25_frame.payload.ax25_info.payload.tbex_beacon.avgnumactivetasks15
    :field totnumprocesses: ax25_frame.payload.ax25_info.payload.tbex_beacon.totnumprocesses
    :field usedmemminuscache: ax25_frame.payload.ax25_info.payload.tbex_beacon.usedmemminuscache
    :field freemempluscache: ax25_frame.payload.ax25_info.payload.tbex_beacon.freemempluscache
    :field sd_usage: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_usage
    :field datamnt_usage: ax25_frame.payload.ax25_info.payload.tbex_beacon.datamnt_usage
    :field stamp_gpio_states: ax25_frame.payload.ax25_info.payload.tbex_beacon.stamp_gpio_states
    :field ioe_states: ax25_frame.payload.ax25_info.payload.tbex_beacon.ioe_states
    :field lithium_op_count: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_op_count
    :field lithium_msp430_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_msp430_temp
    :field lithium_rssi: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_rssi
    :field lithium_rx: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_rx
    :field lithium_tx: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_tx
    :field fcpu_processor_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_processor_temp
    :field lithium_pa_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.lithium_pa_temp
    :field li_3v3_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.li_3v3_voltage
    :field fcpu_3v3_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_3v3_current
    :field li_3v3_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.li_3v3_current
    :field fcpu_3v3_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_3v3_voltage
    :field li_vbatt_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.li_vbatt_voltage
    :field li_vbatt_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.li_vbatt_current
    :field sd_imon_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_imon_1
    :field sd_imon_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_imon_2
    :field sd_imon_3: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_imon_3
    :field sd_imon_4: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_imon_4
    :field battery_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.battery_voltage
    :field battery_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.battery_current
    :field battery_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.battery_temperature
    :field battery_bus_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.battery_bus_voltage
    :field battery_bus_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.battery_bus_current
    :field bus_voltage_5v: ax25_frame.payload.ax25_info.payload.tbex_beacon.bus_voltage_5v
    :field bus_current_5v: ax25_frame.payload.ax25_info.payload.tbex_beacon.bus_current_5v
    :field input_current_5v: ax25_frame.payload.ax25_info.payload.tbex_beacon.input_current_5v
    :field bus_voltage_3_3v: ax25_frame.payload.ax25_info.payload.tbex_beacon.bus_voltage_3_3v
    :field bus_current_3_3v: ax25_frame.payload.ax25_info.payload.tbex_beacon.bus_current_3_3v
    :field input_current_3_3v: ax25_frame.payload.ax25_info.payload.tbex_beacon.input_current_3_3v
    :field output_regulator_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.output_regulator_temperature
    :field eps_5v_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.eps_5v_voltage
    :field eps_5v_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.eps_5v_current
    :field eps_3_3_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.eps_3_3_voltage
    :field eps_3_3v_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.eps_3_3v_current
    :field channel_1_panel_voltage_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_panel_voltage_a
    :field channel_1_panel_voltage_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_panel_voltage_b
    :field channel_1_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_panel_current_a
    :field channel_1_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_panel_current_b
    :field channel_1_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_output_current
    :field channel_1_output_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_output_voltage
    :field channel_1_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_board_temperature
    :field channel_1_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_1_module_temperature
    :field channel_2_panel_voltage_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_panel_voltage_a
    :field channel_2_panel_voltage_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_panel_voltage_b
    :field channel_2_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_panel_current_a
    :field channel_2_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_panel_current_b
    :field channel_2_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_output_current
    :field channel_2_output_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_output_voltage
    :field channel_2_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_board_temperature
    :field channel_2_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_2_module_temperature
    :field channel_3_panel_voltage_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_panel_voltage_a
    :field channel_3_panel_voltage_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_panel_voltage_b
    :field channel_3_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_panel_current_a
    :field channel_3_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_panel_current_b
    :field channel_3_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_output_current
    :field channel_3_output_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_output_voltage
    :field channel_3_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_board_temperature
    :field channel_3_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_3_module_temperature
    :field channel_4_panel_voltage_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_panel_voltage_a
    :field channel_4_panel_voltage_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_panel_voltage_b
    :field channel_4_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_panel_current_a
    :field channel_4_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_panel_current_b
    :field channel_4_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_output_current
    :field channel_4_output_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_output_voltage
    :field channel_4_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_board_temperature
    :field channel_4_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_4_module_temperature
    :field channel_5_module_input_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_module_input_voltage
    :field channel_5_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_panel_current_a
    :field channel_5_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_panel_current_b
    :field channel_5_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_output_current
    :field channel_5_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_board_temperature
    :field channel_5_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_5_module_temperature
    :field channel_6_module_input_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_module_input_voltage
    :field channel_6_panel_current_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_panel_current_a
    :field channel_6_panel_current_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_panel_current_b
    :field channel_6_output_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_output_current
    :field channel_6_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_board_temperature
    :field channel_6_module_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.channel_6_module_temperature
    :field adcs_5v_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_5v_voltage
    :field adcs_5v_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_5v_current
    :field adcs_3v3_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_3v3_voltage
    :field adcs_3v3_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_3v3_current
    :field adcs_vbatt_curent: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_vbatt_curent
    :field adcs_vbatt_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_vbatt_voltage
    :field adcs_temp_0: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_temp_0
    :field adcs_temp_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.adcs_temp_1
    :field eimu_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.eimu_current
    :field adc_curr: ax25_frame.payload.ax25_info.payload.tbex_beacon.adc_curr
    :field sd_v: ax25_frame.payload.ax25_info.payload.tbex_beacon.sd_v
    :field fcpu_var_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_1
    :field fcpu_var_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_2
    :field fcpu_var_3: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_3
    :field fcpu_var_4: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_4
    :field fcpu_var_5: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_5
    :field fcpu_var_6: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_6
    :field tbex_payload_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.tbex_payload_current
    :field tbex_payload_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.tbex_payload_voltage
    :field pim_3v3_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.pim_3v3_current
    :field pim_3v3_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.pim_3v3_voltage
    :field pim_vbatt_monitor: ax25_frame.payload.ax25_info.payload.tbex_beacon.pim_vbatt_monitor
    :field pim_bus_3v3_voltag: ax25_frame.payload.ax25_info.payload.tbex_beacon.pim_bus_3v3_voltag
    :field rtc_unix_time_beacon_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.rtc_unix_time_beacon_2
    :field numresets_beacon_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.numresets_beacon_2
    :field stamp_gpio_states_abbreviated: ax25_frame.payload.ax25_info.payload.tbex_beacon.stamp_gpio_states_abbreviated
    :field fcpu_var_7: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_7
    :field fcpu_var_8: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_8
    :field fcpu_var_9: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_9
    :field fcpu_var_10: ax25_frame.payload.ax25_info.payload.tbex_beacon.fcpu_var_10
    :field command_received_from_fcpu: ax25_frame.payload.ax25_info.payload.tbex_beacon.command_received_from_fcpu
    :field nx_wing_magnetometer_x: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_wing_magnetometer_x
    :field nx_wing_magnetometer_y: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_wing_magnetometer_y
    :field nx_wing_magnetometer_z: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_wing_magnetometer_z
    :field px_wing_magnetometer_x: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_wing_magnetometer_x
    :field px_wing_magnetometer_y: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_wing_magnetometer_y
    :field px_wing_magnetometer_z: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_wing_magnetometer_z
    :field py_body_magnetometer_x: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_magnetometer_x
    :field py_body_magnetometer_y: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_magnetometer_y
    :field py_body_magnetometer_z: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_magnetometer_z
    :field ny_body_magnetometer_x: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_magnetometer_x
    :field ny_body_magnetometer_y: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_magnetometer_y
    :field ny_body_magnetometer_z: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_magnetometer_z
    :field py_body_cell_voltage_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_cell_voltage_1
    :field py_body_cell_voltage_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_cell_voltage_2
    :field py_body_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_panel_circuitry_current
    :field py_body_internal_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_internal_temp
    :field py_body_external_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_external_temp
    :field ny_body_cell_voltage_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_cell_voltage_1
    :field ny_body_cell_voltage_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_cell_voltage_2
    :field ny_body_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_panel_circuitry_current
    :field ny_body_internal_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_internal_temp
    :field ny_body_external_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_external_temp
    :field nx_body_cell_voltage_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_cell_voltage_1
    :field nx_body_cell_voltage_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_cell_voltage_2
    :field nx_body_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_panel_circuitry_current
    :field nx_body_internal_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_internal_temp
    :field nx_body_external_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_external_temp
    :field px_body_cell_voltage_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_cell_voltage_1
    :field px_body_cell_voltage_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_cell_voltage_2
    :field px_body_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_panel_circuitry_current
    :field px_body_internal_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_internal_temp
    :field px_body_external_temp: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_external_temp
    :field nx_deployable_temp_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_deployable_temp_1
    :field nx_deployable_temp_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_deployable_temp_2
    :field nx_deployable_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_deployable_panel_circuitry_current
    :field px_deployable_temp_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_deployable_temp_1
    :field px_deployable_temp_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_deployable_temp_2
    :field px_deployable_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_deployable_panel_circuitry_current
    :field py_deployable_temp_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_deployable_temp_1
    :field py_deployable_temp_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_deployable_temp_2
    :field py_deployable_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_deployable_panel_circuitry_current
    :field ny_deployable_temp_1: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_deployable_temp_1
    :field ny_deployable_temp_2: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_deployable_temp_2
    :field ny_deployable_panel_circuitry_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_deployable_panel_circuitry_current
    :field nx_wing_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_wing_photodiode_a
    :field nx_wing_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_wing_photodiode_b
    :field px_wing_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_wing_photodiode_a
    :field px_wing_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_wing_photodiode_b
    :field py_body_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_photodiode_a
    :field py_body_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_body_photodiode_b
    :field ny_body_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_photodiode_a
    :field ny_body_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_body_photodiode_b
    :field py_wing_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_wing_photodiode_a
    :field py_wing_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.py_wing_photodiode_b
    :field ny_wing_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_wing_photodiode_a
    :field ny_wing_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.ny_wing_photodiode_b
    :field nx_body_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_photodiode_a
    :field nx_body_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.nx_body_photodiode_b
    :field px_body_photodiode_a: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_photodiode_a
    :field px_body_photodiode_b: ax25_frame.payload.ax25_info.payload.tbex_beacon.px_body_photodiode_b
    :field gyro_4_x: ax25_frame.payload.ax25_info.payload.tbex_beacon.gyro_4_x
    :field gyro_4_y: ax25_frame.payload.ax25_info.payload.tbex_beacon.gyro_4_y
    :field gyro_4_z: ax25_frame.payload.ax25_info.payload.tbex_beacon.gyro_4_z
    :field eimu_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.eimu_temperature
    :field wheel_x_speed: ax25_frame.payload.ax25_info.payload.tbex_beacon.wheel_x_speed
    :field wheel_y_speed: ax25_frame.payload.ax25_info.payload.tbex_beacon.wheel_y_speed
    :field wheel_z_speed: ax25_frame.payload.ax25_info.payload.tbex_beacon.wheel_z_speed
    :field tcb_temp_0: ax25_frame.payload.ax25_info.payload.tbex_beacon.tcb_temp_0
    :field tcb_3v3_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.tcb_3v3_current
    :field tcb_vbatt_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.tcb_vbatt_current
    :field input_current: ax25_frame.payload.ax25_info.payload.tbex_beacon.input_current
    :field input_voltage: ax25_frame.payload.ax25_info.payload.tbex_beacon.input_voltage
    :field voltage_5_5: ax25_frame.payload.ax25_info.payload.tbex_beacon.voltage_5_5
    :field voltage_3_0: ax25_frame.payload.ax25_info.payload.tbex_beacon.voltage_3_0
    :field voltage_3_3: ax25_frame.payload.ax25_info.payload.tbex_beacon.voltage_3_3
    :field rf_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.rf_board_temperature
    :field control_board_temperature: ax25_frame.payload.ax25_info.payload.tbex_beacon.control_board_temperature
    :field vhf_channel_forward_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.vhf_channel_forward_power
    :field uhf_channel_forward_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.uhf_channel_forward_power
    :field l_band_channel_forward_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.l_band_channel_forward_power
    :field vhf_channel_reverse_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.vhf_channel_reverse_power
    :field uhf_channel_reverse_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.uhf_channel_reverse_power
    :field l_band_channel_reverse_power: ax25_frame.payload.ax25_info.payload.tbex_beacon.l_band_channel_reverse_power
    :field pll_config_mask: ax25_frame.payload.ax25_info.payload.tbex_beacon.pll_config_mask
    :field ppu_reset_count: ax25_frame.payload.ax25_info.payload.tbex_beacon.ppu_reset_count
    :field status_mask: ax25_frame.payload.ax25_info.payload.tbex_beacon.status_mask
    :field error_mask: ax25_frame.payload.ax25_info.payload.tbex_beacon.error_mask
    :field rtc_unix_time: ax25_frame.payload.ax25_info.payload.grifex_beacon.rtc_unix_time
    :field numresets: ax25_frame.payload.ax25_info.payload.grifex_beacon.numresets
    :field avgnumactivetasks1: ax25_frame.payload.ax25_info.payload.grifex_beacon.avgnumactivetasks1
    :field avgnumactivetasks5: ax25_frame.payload.ax25_info.payload.grifex_beacon.avgnumactivetasks5
    :field avgnumactivetasks15: ax25_frame.payload.ax25_info.payload.grifex_beacon.avgnumactivetasks15
    :field curnumrunnabletasks: ax25_frame.payload.ax25_info.payload.grifex_beacon.curnumrunnabletasks
    :field totnumprocesses: ax25_frame.payload.ax25_info.payload.grifex_beacon.totnumprocesses
    :field lastprocesspid: ax25_frame.payload.ax25_info.payload.grifex_beacon.lastprocesspid
    :field totmem: ax25_frame.payload.ax25_info.payload.grifex_beacon.totmem
    :field freemem: ax25_frame.payload.ax25_info.payload.grifex_beacon.freemem
    :field adcs_enable_status: ax25_frame.payload.ax25_info.payload.grifex_beacon.adcs_enable_status
    :field sd_usage: ax25_frame.payload.ax25_info.payload.grifex_beacon.sd_usage
    :field datamnt_usage: ax25_frame.payload.ax25_info.payload.grifex_beacon.datamnt_usage
    :field lithium_op_count: ax25_frame.payload.ax25_info.payload.grifex_beacon.lithium_op_count
    :field lithium_msp430_temp: ax25_frame.payload.ax25_info.payload.grifex_beacon.lithium_msp430_temp
    :field lithium_rssi: ax25_frame.payload.ax25_info.payload.grifex_beacon.lithium_rssi
    :field lithium_rx: ax25_frame.payload.ax25_info.payload.grifex_beacon.lithium_rx
    :field lithium_tx: ax25_frame.payload.ax25_info.payload.grifex_beacon.lithium_tx
    :field fcpu_temp_0: ax25_frame.payload.ax25_info.payload.grifex_beacon.fcpu_temp_0
    :field fcpu_temp_1: ax25_frame.payload.ax25_info.payload.grifex_beacon.fcpu_temp_1
    :field li_3v3_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.li_3v3_voltage
    :field fcpu_3v3_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.fcpu_3v3_current
    :field li_3v3_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.li_3v3_current
    :field fcpu_3v3_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.fcpu_3v3_voltage
    :field li_vbatt_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.li_vbatt_voltage
    :field li_vbatt_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.li_vbatt_current
    :field battery_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.battery_voltage
    :field battery_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.battery_current
    :field battery_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.battery_temperature
    :field battery_bus_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.battery_bus_voltage
    :field battery_bus_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.battery_bus_current
    :field bus_voltage_5v: ax25_frame.payload.ax25_info.payload.grifex_beacon.bus_voltage_5v
    :field bus_current_5v: ax25_frame.payload.ax25_info.payload.grifex_beacon.bus_current_5v
    :field input_current_5v: ax25_frame.payload.ax25_info.payload.grifex_beacon.input_current_5v
    :field bus_voltage_3_3v: ax25_frame.payload.ax25_info.payload.grifex_beacon.bus_voltage_3_3v
    :field bus_current_3_3v: ax25_frame.payload.ax25_info.payload.grifex_beacon.bus_current_3_3v
    :field input_current_3_3v: ax25_frame.payload.ax25_info.payload.grifex_beacon.input_current_3_3v
    :field output_regulator_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.output_regulator_temperature
    :field eps_5v_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_5v_voltage
    :field eps_5v_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_5v_current
    :field eps_3_3_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_3_3_voltage
    :field eps_3_3v_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_3_3v_current
    :field channel_1_panel_voltage_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_panel_voltage_b
    :field channel_1_panel_current_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_panel_current_b
    :field channel_1_output_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_output_voltage
    :field channel_1_output_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_output_current
    :field channel_1_module_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_module_temperature
    :field channel_1_board_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_1_board_temperature
    :field channel_2_panel_voltage_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_panel_voltage_b
    :field channel_2_panel_current_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_panel_current_b
    :field channel_2_output_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_output_voltage
    :field channel_2_output_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_output_current
    :field channel_2_module_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_module_temperature
    :field channel_2_board_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_2_board_temperature
    :field channel_3_panel_voltage_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_panel_voltage_b
    :field channel_3_panel_current_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_panel_current_b
    :field channel_3_output_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_output_voltage
    :field channel_3_output_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_output_current
    :field channel_3_module_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_module_temperature
    :field channel_3_board_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_3_board_temperature
    :field channel_4_panel_voltage_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_panel_voltage_b
    :field channel_4_panel_current_b: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_panel_current_b
    :field channel_4_output_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_output_voltage
    :field channel_4_output_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_output_current
    :field channel_4_module_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_module_temperature
    :field channel_4_board_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.channel_4_board_temperature
    :field eps_ioe_state: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_ioe_state
    :field eps_ioe_mode: ax25_frame.payload.ax25_info.payload.grifex_beacon.eps_ioe_mode
    :field tcb_temp_0: ax25_frame.payload.ax25_info.payload.grifex_beacon.tcb_temp_0
    :field tcb_temp_1: ax25_frame.payload.ax25_info.payload.grifex_beacon.tcb_temp_1
    :field tcb_temp_2: ax25_frame.payload.ax25_info.payload.grifex_beacon.tcb_temp_2
    :field adcs1_ioe_state: ax25_frame.payload.ax25_info.payload.grifex_beacon.adcs1_ioe_state
    :field adcs1_ioe_mode: ax25_frame.payload.ax25_info.payload.grifex_beacon.adcs1_ioe_mode
    :field posy_mag_x: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_mag_x
    :field posy_mag_y: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_mag_y
    :field posy_mag_z: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_mag_z
    :field posx_mag_x: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_mag_x
    :field posx_mag_y: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_mag_y
    :field posx_mag_z: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_mag_z
    :field negy_mag_x: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_mag_x
    :field negy_mag_y: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_mag_y
    :field negy_mag_z: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_mag_z
    :field negx_mag_x: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_mag_x
    :field negx_mag_y: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_mag_y
    :field negx_mag_z: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_mag_z
    :field posy_internal_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_internal_temperature
    :field posy_external_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_external_temperature
    :field posx_internal_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_internal_temperature
    :field posx_external_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_external_temperature
    :field negy_internal_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_internal_temperature
    :field negy_external_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_external_temperature
    :field negx_internal_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_internal_temperature
    :field negx_external_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_external_temperature
    :field posy_photodiode: ax25_frame.payload.ax25_info.payload.grifex_beacon.posy_photodiode
    :field posx_photodiode: ax25_frame.payload.ax25_info.payload.grifex_beacon.posx_photodiode
    :field negy_photodiode: ax25_frame.payload.ax25_info.payload.grifex_beacon.negy_photodiode
    :field negx_photodiode: ax25_frame.payload.ax25_info.payload.grifex_beacon.negx_photodiode
    :field mzint_ioe1_state: ax25_frame.payload.ax25_info.payload.grifex_beacon.mzint_ioe1_state
    :field mzint_ioe1_mode: ax25_frame.payload.ax25_info.payload.grifex_beacon.mzint_ioe1_mode
    :field mzint_ioe2_state: ax25_frame.payload.ax25_info.payload.grifex_beacon.mzint_ioe2_state
    :field mzint_ioe2_mode: ax25_frame.payload.ax25_info.payload.grifex_beacon.mzint_ioe2_mode
    :field marina_gpio_status_data: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_gpio_status_data
    :field marina_completed_runs: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_completed_runs
    :field marina_aborted_runs: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_aborted_runs
    :field marina_vbatt_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_vbatt_voltage
    :field marina_vbatt_current: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_vbatt_current
    :field marina_temperature: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_temperature
    :field marina_2_5v_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_2_5v_voltage
    :field marina_1_0v_voltage: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_1_0v_voltage
    :field marina_exit_status: ax25_frame.payload.ax25_info.payload.grifex_beacon.marina_exit_status
    :field variable_1: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_1
    :field variable_2: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_2
    :field variable_3: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_3
    :field variable_4: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_4
    :field variable_5: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_5
    :field variable_6: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_6
    :field variable_7: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_7
    :field variable_8: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_8
    :field variable_9: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_9
    :field variable_10: ax25_frame.payload.ax25_info.payload.grifex_beacon.variable_10
    :field rtc_unix_time: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.rtc_unix_time
    :field numresets: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.numresets
    :field avgnumactivetasks1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.avgnumactivetasks1
    :field avgnumactivetasks5: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.avgnumactivetasks5
    :field avgnumactivetasks15: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.avgnumactivetasks15
    :field curnumrunnabletasks: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.curnumrunnabletasks
    :field totnumprocesses: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.totnumprocesses
    :field lastprocesspid: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lastprocesspid
    :field totmem: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.totmem
    :field freemem: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.freemem
    :field lithium_op_count: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lithium_op_count
    :field lithium_msp430_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lithium_msp430_temp
    :field lithium_rssi: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lithium_rssi
    :field lithium_rx: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lithium_rx
    :field lithium_tx: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.lithium_tx
    :field ch_1_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_1_module_output_current
    :field ch_1a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_1a_current
    :field ch_1_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_1_module_temp
    :field ch_1a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_1a_voltage
    :field ch_2_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_2_module_output_current
    :field ch_2a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_2a_current
    :field ch_2_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_2_module_temp
    :field ch_2a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_2a_voltage
    :field ch_3_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_3_module_output_current
    :field ch_3a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_3a_current
    :field ch_3_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_3_module_temp
    :field ch_3a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_3a_voltage
    :field ch_4_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_4_module_output_current
    :field ch_4a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_4a_current
    :field ch_4_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_4_module_temp
    :field ch_4a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_4a_voltage
    :field ch_5_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_5_module_output_current
    :field ch_5a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_5a_current
    :field ch_5_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_5_module_temp
    :field ch_5a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_5a_voltage
    :field ch_6_module_output_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_6_module_output_current
    :field ch_6a_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_6a_current
    :field ch_6_module_temp: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_6_module_temp
    :field ch_6a_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ch_6a_voltage
    :field regulator_input_current_5v: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.regulator_input_current_5v
    :field regulator_input_current_3_3v: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.regulator_input_current_3_3v
    :field bb_t_output: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bb_t_output
    :field bus_vbatt_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_vbatt_current
    :field bus_5v_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_5v_current
    :field bus_3_3v_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_3_3v_voltage
    :field bus_3_3v_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_3_3v_current
    :field bus_vbatt_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_vbatt_voltage
    :field bus_5v_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bus_5v_voltage
    :field eps_5v_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_5v_current
    :field eps_5v_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_5v_voltage
    :field eps_3_3v_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_3_3v_current
    :field bb_eps_batt_i: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.bb_eps_batt_i
    :field eps_3_3v_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_3_3v_voltage
    :field battery_temperature: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.battery_temperature
    :field ioe1_ioe_state: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ioe1_ioe_state
    :field ioe1_ioe_mode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.ioe1_ioe_mode
    :field fcpu1_ioe_state: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu1_ioe_state
    :field fcpu1_ioe_mode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu1_ioe_mode
    :field adcs1_ioe_state: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.adcs1_ioe_state
    :field adcs1_ioe_mode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.adcs1_ioe_mode
    :field eps_ioe_state: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_ioe_state
    :field eps_ioe_mode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.eps_ioe_mode
    :field mzint1_ioe_state: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.mzint1_ioe_state
    :field mzint1_ioe_mode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.mzint1_ioe_mode
    :field acb_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_temp_0
    :field acb_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_temp_1
    :field acb_vbatt_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_vbatt_voltage
    :field acb_vbatt_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_vbatt_current
    :field acb_5v_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_5v_voltage
    :field acb_5v_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_5v_current
    :field acb_3v3_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_3v3_voltage
    :field acb_3v3_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.acb_3v3_current
    :field fcpu_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu_temp_0
    :field fcpu_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu_temp_1
    :field li_3v3_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.li_3v3_voltage
    :field fcpu_3v3_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu_3v3_current
    :field li_3v3_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.li_3v3_current
    :field fcpu_3v3_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.fcpu_3v3_voltage
    :field li_vbatt_voltage: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.li_vbatt_voltage
    :field li_vbatt_current: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.li_vbatt_current
    :field negz_mag_x: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_mag_x
    :field negz_mag_y: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_mag_y
    :field negz_mag_z: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_mag_z
    :field negz_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_temp_0
    :field negz_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_temp_1
    :field posz_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posz_temp_0
    :field posz_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posz_temp_1
    :field negx_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negx_temp_0
    :field negx_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negx_temp_1
    :field posx_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_temp_0
    :field posx_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_temp_1
    :field negy_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negy_temp_0
    :field negy_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negy_temp_1
    :field posy_temp_0: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posy_temp_0
    :field posy_temp_1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posy_temp_1
    :field negz_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negz_photodiode
    :field posz_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posz_photodiode
    :field negx_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negx_photodiode
    :field posx_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_photodiode
    :field negy_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.negy_photodiode
    :field posy_photodiode: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posy_photodiode
    :field posx_mag_x: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_mag_x
    :field posx_mag_y: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_mag_y
    :field posx_mag_z: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.posx_mag_z
    :field cove_experiment_md5sum_p1: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_experiment_md5sum_p1
    :field cove_experiment_md5sum_p2: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_experiment_md5sum_p2
    :field cove_experiment_md5sum_p3: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_experiment_md5sum_p3
    :field cove_experiment_md5sum_p4: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_experiment_md5sum_p4
    :field cove_status_data: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_status_data
    :field cove_num_successes: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_num_successes
    :field cove_num_failures: ax25_frame.payload.ax25_info.payload.mcubed2_beacon.cove_num_failures
    :field crc: ax25_frame.payload.crc
    
    .. seealso::
       Source - https://docs.google.com/spreadsheets/d/1mGekVQyf4Ozlf6UqojZk0ji02DwLLDFp3S1XTffvqGk/edit#gid=1694629037
       https://drive.google.com/file/d/1XduQg8NTiXD0MORRmrdjMPdAokTbSP_1/view
       https://drive.google.com/file/d/1mv0lSleUe6LL0O4OmI-LSaQlulIeozMu/view
       https://docs.google.com/spreadsheets/d/1kTfqIfh5AEzD56a7lo57BiqL4Rb87qpOVoilp4uiptA/edit#gid=547446560
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Mxl.Ax25Frame(self._io, self, self._root)

    class TbexBeacon2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtc_unix_time_beacon_2 = self._io.read_u4le()
            self.numresets_beacon_2 = self._io.read_u2le()
            self.stamp_gpio_states_abbreviated = self._io.read_u1()
            self.fcpu_var_7 = self._io.read_u1()
            self.fcpu_var_8 = self._io.read_u1()
            self.fcpu_var_9 = self._io.read_u1()
            self.fcpu_var_10 = self._io.read_u1()
            self.command_received_from_fcpu = self._io.read_u2le()
            self.nx_wing_magnetometer_x = self._io.read_s2le()
            self.nx_wing_magnetometer_y = self._io.read_s2le()
            self.nx_wing_magnetometer_z = self._io.read_s2le()
            self.px_wing_magnetometer_x = self._io.read_s2le()
            self.px_wing_magnetometer_y = self._io.read_s2le()
            self.px_wing_magnetometer_z = self._io.read_s2le()
            self.py_body_magnetometer_x = self._io.read_s2le()
            self.py_body_magnetometer_y = self._io.read_s2le()
            self.py_body_magnetometer_z = self._io.read_s2le()
            self.ny_body_magnetometer_x = self._io.read_s2le()
            self.ny_body_magnetometer_y = self._io.read_s2le()
            self.ny_body_magnetometer_z = self._io.read_s2le()
            self.py_body_cell_voltage_1 = self._io.read_u2le()
            self.py_body_cell_voltage_2 = self._io.read_u2le()
            self.py_body_panel_circuitry_current = self._io.read_u2le()
            self.py_body_internal_temp = self._io.read_s2le()
            self.py_body_external_temp = self._io.read_s2le()
            self.ny_body_cell_voltage_1 = self._io.read_u2le()
            self.ny_body_cell_voltage_2 = self._io.read_u2le()
            self.ny_body_panel_circuitry_current = self._io.read_u2le()
            self.ny_body_internal_temp = self._io.read_s2le()
            self.ny_body_external_temp = self._io.read_s2le()
            self.nx_body_cell_voltage_1 = self._io.read_u2le()
            self.nx_body_cell_voltage_2 = self._io.read_u2le()
            self.nx_body_panel_circuitry_current = self._io.read_u2le()
            self.nx_body_internal_temp = self._io.read_s2le()
            self.nx_body_external_temp = self._io.read_s2le()
            self.px_body_cell_voltage_1 = self._io.read_u2le()
            self.px_body_cell_voltage_2 = self._io.read_u2le()
            self.px_body_panel_circuitry_current = self._io.read_u2le()
            self.px_body_internal_temp = self._io.read_s2le()
            self.px_body_external_temp = self._io.read_s2le()
            self.nx_deployable_temp_1 = self._io.read_s2le()
            self.nx_deployable_temp_2 = self._io.read_s2le()
            self.nx_deployable_panel_circuitry_current = self._io.read_u2le()
            self.px_deployable_temp_1 = self._io.read_s2le()
            self.px_deployable_temp_2 = self._io.read_s2le()
            self.px_deployable_panel_circuitry_current = self._io.read_u2le()
            self.py_deployable_temp_1 = self._io.read_s2le()
            self.py_deployable_temp_2 = self._io.read_s2le()
            self.py_deployable_panel_circuitry_current = self._io.read_u2le()
            self.ny_deployable_temp_1 = self._io.read_s2le()
            self.ny_deployable_temp_2 = self._io.read_s2le()
            self.ny_deployable_panel_circuitry_current = self._io.read_u2le()
            self.nx_wing_photodiode_a = self._io.read_u2le()
            self.nx_wing_photodiode_b = self._io.read_u2le()
            self.px_wing_photodiode_a = self._io.read_u2le()
            self.px_wing_photodiode_b = self._io.read_u2le()
            self.py_body_photodiode_a = self._io.read_u2le()
            self.py_body_photodiode_b = self._io.read_u2le()
            self.ny_body_photodiode_a = self._io.read_u2le()
            self.ny_body_photodiode_b = self._io.read_u2le()
            self.py_wing_photodiode_a = self._io.read_u2le()
            self.py_wing_photodiode_b = self._io.read_u2le()
            self.ny_wing_photodiode_a = self._io.read_u2le()
            self.ny_wing_photodiode_b = self._io.read_u2le()
            self.nx_body_photodiode_a = self._io.read_u2le()
            self.nx_body_photodiode_b = self._io.read_u2le()
            self.px_body_photodiode_a = self._io.read_u2le()
            self.px_body_photodiode_b = self._io.read_u2le()
            self.gyro_4_x = self._io.read_s2le()
            self.gyro_4_y = self._io.read_s2le()
            self.gyro_4_z = self._io.read_s2le()
            self.eimu_temperature = self._io.read_s2le()
            self.wheel_x_speed = self._io.read_s2le()
            self.wheel_y_speed = self._io.read_s2le()
            self.wheel_z_speed = self._io.read_s2le()
            self.tcb_temp_0 = self._io.read_s2le()
            self.tcb_3v3_current = self._io.read_u2le()
            self.tcb_vbatt_current = self._io.read_u2le()
            self.input_current = self._io.read_u2le()
            self.input_voltage = self._io.read_u2le()
            self.voltage_5_5 = self._io.read_u2le()
            self.voltage_3_0 = self._io.read_u2le()
            self.voltage_3_3 = self._io.read_u2le()
            self.rf_board_temperature = self._io.read_u2le()
            self.control_board_temperature = self._io.read_u2le()
            self.vhf_channel_forward_power = self._io.read_u2le()
            self.uhf_channel_forward_power = self._io.read_u2le()
            self.l_band_channel_forward_power = self._io.read_u2le()
            self.vhf_channel_reverse_power = self._io.read_u2le()
            self.uhf_channel_reverse_power = self._io.read_u2le()
            self.l_band_channel_reverse_power = self._io.read_u2le()
            self.pll_config_mask = self._io.read_u1()
            self.ppu_reset_count = self._io.read_u1()
            self.status_mask = self._io.read_u1()
            self.error_mask = self._io.read_u2le()
            self.crc = self._io.read_u2le()


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Mxl.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Mxl.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Mxl.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Mxl.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Mxl.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Mxl.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Mxl.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Mxl.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Mxl.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Mxl.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Mxl.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Mxl.Repeater(self._io, self, self._root)

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
            if _on == u"KF6RFX":
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Mxl.RapT(_io__raw_ax25_info, self, self._root)
            elif _on == u"NOCALL":
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Mxl.RapT(_io__raw_ax25_info, self, self._root)
            elif _on == u"CQ    ":
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Mxl.RapT(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class GrifexBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.framelength
            if _on == 261:
                self.grifex_beacon = Mxl.GrifexT(self._io, self, self._root)


    class TbexBeacon1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.operation_mode = self._io.read_u2le()
            self.rtc_unix_time = self._io.read_u4le()
            self.numresets = self._io.read_u2le()
            self.avgnumactivetasks1 = self._io.read_u2le()
            self.avgnumactivetasks5 = self._io.read_u2le()
            self.avgnumactivetasks15 = self._io.read_u2le()
            self.totnumprocesses = self._io.read_u2le()
            self.usedmemminuscache = self._io.read_u2le()
            self.freemempluscache = self._io.read_u2le()
            self.sd_usage = self._io.read_u2le()
            self.datamnt_usage = self._io.read_u2le()
            self.stamp_gpio_states = self._io.read_u2le()
            self.ioe_states = self._io.read_u1()
            self.lithium_op_count = self._io.read_u2le()
            self.lithium_msp430_temp = self._io.read_s2le()
            self.lithium_rssi = self._io.read_u1()
            self.lithium_rx = self._io.read_u4le()
            self.lithium_tx = self._io.read_u4le()
            self.fcpu_processor_temp = self._io.read_s2le()
            self.lithium_pa_temp = self._io.read_s2le()
            self.li_3v3_voltage = self._io.read_u2le()
            self.fcpu_3v3_current = self._io.read_u2le()
            self.li_3v3_current = self._io.read_u2le()
            self.fcpu_3v3_voltage = self._io.read_u2le()
            self.li_vbatt_voltage = self._io.read_u2le()
            self.li_vbatt_current = self._io.read_u2le()
            self.sd_imon_1 = self._io.read_u2le()
            self.sd_imon_2 = self._io.read_u2le()
            self.sd_imon_3 = self._io.read_u2le()
            self.sd_imon_4 = self._io.read_u2le()
            self.battery_voltage = self._io.read_u2le()
            self.battery_current = self._io.read_s2le()
            self.battery_temperature = self._io.read_u2le()
            self.battery_bus_voltage = self._io.read_u2le()
            self.battery_bus_current = self._io.read_u2le()
            self.bus_voltage_5v = self._io.read_u2le()
            self.bus_current_5v = self._io.read_u2le()
            self.input_current_5v = self._io.read_u2le()
            self.bus_voltage_3_3v = self._io.read_u2le()
            self.bus_current_3_3v = self._io.read_u2le()
            self.input_current_3_3v = self._io.read_u2le()
            self.output_regulator_temperature = self._io.read_u2le()
            self.eps_5v_voltage = self._io.read_u2le()
            self.eps_5v_current = self._io.read_u2le()
            self.eps_3_3_voltage = self._io.read_s2le()
            self.eps_3_3v_current = self._io.read_s2le()
            self.channel_1_panel_voltage_a = self._io.read_u2le()
            self.channel_1_panel_voltage_b = self._io.read_u2le()
            self.channel_1_panel_current_a = self._io.read_u2le()
            self.channel_1_panel_current_b = self._io.read_u2le()
            self.channel_1_output_current = self._io.read_u2le()
            self.channel_1_output_voltage = self._io.read_u2le()
            self.channel_1_board_temperature = self._io.read_s2le()
            self.channel_1_module_temperature = self._io.read_s2le()
            self.channel_2_panel_voltage_a = self._io.read_u2le()
            self.channel_2_panel_voltage_b = self._io.read_u2le()
            self.channel_2_panel_current_a = self._io.read_u2le()
            self.channel_2_panel_current_b = self._io.read_u2le()
            self.channel_2_output_current = self._io.read_u2le()
            self.channel_2_output_voltage = self._io.read_u2le()
            self.channel_2_board_temperature = self._io.read_s2le()
            self.channel_2_module_temperature = self._io.read_s2le()
            self.channel_3_panel_voltage_a = self._io.read_u2le()
            self.channel_3_panel_voltage_b = self._io.read_u2le()
            self.channel_3_panel_current_a = self._io.read_u2le()
            self.channel_3_panel_current_b = self._io.read_u2le()
            self.channel_3_output_current = self._io.read_u2le()
            self.channel_3_output_voltage = self._io.read_u2le()
            self.channel_3_board_temperature = self._io.read_s2le()
            self.channel_3_module_temperature = self._io.read_s2le()
            self.channel_4_panel_voltage_a = self._io.read_u2le()
            self.channel_4_panel_voltage_b = self._io.read_u2le()
            self.channel_4_panel_current_a = self._io.read_u2le()
            self.channel_4_panel_current_b = self._io.read_u2le()
            self.channel_4_output_current = self._io.read_u2le()
            self.channel_4_output_voltage = self._io.read_u2le()
            self.channel_4_board_temperature = self._io.read_s2le()
            self.channel_4_module_temperature = self._io.read_s2le()
            self.channel_5_module_input_voltage = self._io.read_u2le()
            self.channel_5_panel_current_a = self._io.read_u2le()
            self.channel_5_panel_current_b = self._io.read_u2le()
            self.channel_5_output_current = self._io.read_u2le()
            self.channel_5_board_temperature = self._io.read_s2le()
            self.channel_5_module_temperature = self._io.read_s2le()
            self.channel_6_module_input_voltage = self._io.read_u2le()
            self.channel_6_panel_current_a = self._io.read_u2le()
            self.channel_6_panel_current_b = self._io.read_u2le()
            self.channel_6_output_current = self._io.read_u2le()
            self.channel_6_board_temperature = self._io.read_s2le()
            self.channel_6_module_temperature = self._io.read_s2le()
            self.adcs_5v_voltage = self._io.read_u2le()
            self.adcs_5v_current = self._io.read_u2le()
            self.adcs_3v3_voltage = self._io.read_u2le()
            self.adcs_3v3_current = self._io.read_u2le()
            self.adcs_vbatt_curent = self._io.read_u2le()
            self.adcs_vbatt_voltage = self._io.read_u2le()
            self.adcs_temp_0 = self._io.read_s2le()
            self.adcs_temp_1 = self._io.read_s2le()
            self.eimu_current = self._io.read_u2le()
            self.adc_curr = self._io.read_u2le()
            self.sd_v = self._io.read_u2le()
            self.fcpu_var_1 = self._io.read_u1()
            self.fcpu_var_2 = self._io.read_u1()
            self.fcpu_var_3 = self._io.read_u1()
            self.fcpu_var_4 = self._io.read_u1()
            self.fcpu_var_5 = self._io.read_u1()
            self.fcpu_var_6 = self._io.read_u1()
            self.tbex_payload_current = self._io.read_u2le()
            self.tbex_payload_voltage = self._io.read_u2le()
            self.pim_3v3_current = self._io.read_u2le()
            self.pim_3v3_voltage = self._io.read_u2le()
            self.pim_vbatt_monitor = self._io.read_u2le()
            self.pim_bus_3v3_voltag = self._io.read_u2le()


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


    class Mcubed2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtc_unix_time = self._io.read_u4le()
            self.numresets = self._io.read_u2le()
            self.avgnumactivetasks1 = self._io.read_u2le()
            self.avgnumactivetasks5 = self._io.read_u2le()
            self.avgnumactivetasks15 = self._io.read_u2le()
            self.curnumrunnabletasks = self._io.read_u2le()
            self.totnumprocesses = self._io.read_u2le()
            self.lastprocesspid = self._io.read_u2le()
            self.totmem = self._io.read_u2le()
            self.freemem = self._io.read_u2le()
            self.lithium_op_count = self._io.read_u2le()
            self.lithium_msp430_temp = self._io.read_u2le()
            self.lithium_rssi = self._io.read_u1()
            self.lithium_rx = self._io.read_u4le()
            self.lithium_tx = self._io.read_u4le()
            self.ch_1_module_output_current = self._io.read_u2le()
            self.ch_1a_current = self._io.read_u2le()
            self.ch_1_module_temp = self._io.read_u2le()
            self.ch_1a_voltage = self._io.read_u2le()
            self.ch_2_module_output_current = self._io.read_u2le()
            self.ch_2a_current = self._io.read_u2le()
            self.ch_2_module_temp = self._io.read_u2le()
            self.ch_2a_voltage = self._io.read_u2le()
            self.ch_3_module_output_current = self._io.read_u2le()
            self.ch_3a_current = self._io.read_u2le()
            self.ch_3_module_temp = self._io.read_u2le()
            self.ch_3a_voltage = self._io.read_u2le()
            self.ch_4_module_output_current = self._io.read_u2le()
            self.ch_4a_current = self._io.read_u2le()
            self.ch_4_module_temp = self._io.read_u2le()
            self.ch_4a_voltage = self._io.read_u2le()
            self.ch_5_module_output_current = self._io.read_u2le()
            self.ch_5a_current = self._io.read_u2le()
            self.ch_5_module_temp = self._io.read_u2le()
            self.ch_5a_voltage = self._io.read_u2le()
            self.ch_6_module_output_current = self._io.read_u2le()
            self.ch_6a_current = self._io.read_u2le()
            self.ch_6_module_temp = self._io.read_u2le()
            self.ch_6a_voltage = self._io.read_u2le()
            self.regulator_input_current_5v = self._io.read_u2le()
            self.regulator_input_current_3_3v = self._io.read_u2le()
            self.bb_t_output = self._io.read_u2le()
            self.bus_vbatt_current = self._io.read_u2le()
            self.bus_5v_current = self._io.read_u2le()
            self.bus_3_3v_voltage = self._io.read_u2le()
            self.bus_3_3v_current = self._io.read_u2le()
            self.bus_vbatt_voltage = self._io.read_u2le()
            self.bus_5v_voltage = self._io.read_u2le()
            self.eps_5v_current = self._io.read_u2le()
            self.eps_5v_voltage = self._io.read_u2le()
            self.eps_3_3v_current = self._io.read_u2le()
            self.bb_eps_batt_i = self._io.read_s2le()
            self.eps_3_3v_voltage = self._io.read_u2le()
            self.battery_temperature = self._io.read_u2le()
            self.ioe1_ioe_state = self._io.read_u1()
            self.ioe1_ioe_mode = self._io.read_u1()
            self.fcpu1_ioe_state = self._io.read_u1()
            self.fcpu1_ioe_mode = self._io.read_u1()
            self.adcs1_ioe_state = self._io.read_u1()
            self.adcs1_ioe_mode = self._io.read_u1()
            self.eps_ioe_state = self._io.read_u1()
            self.eps_ioe_mode = self._io.read_u1()
            self.mzint1_ioe_state = self._io.read_u1()
            self.mzint1_ioe_mode = self._io.read_u1()
            self.acb_temp_0 = self._io.read_u2le()
            self.acb_temp_1 = self._io.read_u2le()
            self.acb_vbatt_voltage = self._io.read_u2le()
            self.acb_vbatt_current = self._io.read_u2le()
            self.acb_5v_voltage = self._io.read_u2le()
            self.acb_5v_current = self._io.read_u2le()
            self.acb_3v3_voltage = self._io.read_u2le()
            self.acb_3v3_current = self._io.read_u2le()
            self.fcpu_temp_0 = self._io.read_u2le()
            self.fcpu_temp_1 = self._io.read_u2le()
            self.li_3v3_voltage = self._io.read_u2le()
            self.fcpu_3v3_current = self._io.read_u2le()
            self.li_3v3_current = self._io.read_u2le()
            self.fcpu_3v3_voltage = self._io.read_u2le()
            self.li_vbatt_voltage = self._io.read_u2le()
            self.li_vbatt_current = self._io.read_u2le()
            self.negz_mag_x = self._io.read_s2le()
            self.negz_mag_y = self._io.read_s2le()
            self.negz_mag_z = self._io.read_s2le()
            self.negz_temp_0 = self._io.read_u2le()
            self.negz_temp_1 = self._io.read_u2le()
            self.posz_temp_0 = self._io.read_u2le()
            self.posz_temp_1 = self._io.read_u2le()
            self.negx_temp_0 = self._io.read_u2le()
            self.negx_temp_1 = self._io.read_u2le()
            self.posx_temp_0 = self._io.read_u2le()
            self.posx_temp_1 = self._io.read_u2le()
            self.negy_temp_0 = self._io.read_u2le()
            self.negy_temp_1 = self._io.read_u2le()
            self.posy_temp_0 = self._io.read_u2le()
            self.posy_temp_1 = self._io.read_u2le()
            self.negz_photodiode = self._io.read_u2le()
            self.posz_photodiode = self._io.read_u2le()
            self.negx_photodiode = self._io.read_u2le()
            self.posx_photodiode = self._io.read_u2le()
            self.negy_photodiode = self._io.read_u2le()
            self.posy_photodiode = self._io.read_u2le()
            self.posx_mag_x = self._io.read_s2le()
            self.posx_mag_y = self._io.read_s2le()
            self.posx_mag_z = self._io.read_s2le()
            self.cove_experiment_md5sum_p1 = self._io.read_u4le()
            self.cove_experiment_md5sum_p2 = self._io.read_u4le()
            self.cove_experiment_md5sum_p3 = self._io.read_u4le()
            self.cove_experiment_md5sum_p4 = self._io.read_u4le()
            self.cove_status_data = self._io.read_u1()
            self.cove_num_successes = self._io.read_u2le()
            self.cove_num_failures = self._io.read_u2le()


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Mxl.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Mxl.SsidMask(self._io, self, self._root)


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
                _ = Mxl.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class Mcubed2BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.framelength
            if _on == 257:
                self.mcubed2_beacon = Mxl.Mcubed2T(self._io, self, self._root)


    class TbexBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.framelength
            if _on == 219:
                self.tbex_beacon = Mxl.TbexBeacon2T(self._io, self, self._root)
            elif _on == 255:
                self.tbex_beacon = Mxl.TbexBeacon1T(self._io, self, self._root)


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
            self.callsign_ror = Mxl.Callsign(_io__raw_callsign_ror, self, self._root)


    class GrifexT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rtc_unix_time = self._io.read_u4le()
            self.numresets = self._io.read_u2le()
            self.avgnumactivetasks1 = self._io.read_u2le()
            self.avgnumactivetasks5 = self._io.read_u2le()
            self.avgnumactivetasks15 = self._io.read_u2le()
            self.curnumrunnabletasks = self._io.read_u2le()
            self.totnumprocesses = self._io.read_u2le()
            self.lastprocesspid = self._io.read_u2le()
            self.totmem = self._io.read_u2le()
            self.freemem = self._io.read_u2le()
            self.adcs_enable_status = self._io.read_u1()
            self.sd_usage = self._io.read_u4le()
            self.datamnt_usage = self._io.read_u4le()
            self.lithium_op_count = self._io.read_u2le()
            self.lithium_msp430_temp = self._io.read_u2le()
            self.lithium_rssi = self._io.read_u1()
            self.lithium_rx = self._io.read_u4le()
            self.lithium_tx = self._io.read_u4le()
            self.fcpu_temp_0 = self._io.read_u2le()
            self.fcpu_temp_1 = self._io.read_u2le()
            self.li_3v3_voltage = self._io.read_u2le()
            self.fcpu_3v3_current = self._io.read_u2le()
            self.li_3v3_current = self._io.read_u2le()
            self.fcpu_3v3_voltage = self._io.read_u2le()
            self.li_vbatt_voltage = self._io.read_u2le()
            self.li_vbatt_current = self._io.read_u2le()
            self.battery_voltage = self._io.read_u2le()
            self.battery_current = self._io.read_u2le()
            self.battery_temperature = self._io.read_u2le()
            self.battery_bus_voltage = self._io.read_u2le()
            self.battery_bus_current = self._io.read_u2le()
            self.bus_voltage_5v = self._io.read_u2le()
            self.bus_current_5v = self._io.read_u2le()
            self.input_current_5v = self._io.read_u2le()
            self.bus_voltage_3_3v = self._io.read_u2le()
            self.bus_current_3_3v = self._io.read_u2le()
            self.input_current_3_3v = self._io.read_u2le()
            self.output_regulator_temperature = self._io.read_u2le()
            self.eps_5v_voltage = self._io.read_u2le()
            self.eps_5v_current = self._io.read_u2le()
            self.eps_3_3_voltage = self._io.read_u2le()
            self.eps_3_3v_current = self._io.read_u2le()
            self.channel_1_panel_voltage_b = self._io.read_u2le()
            self.channel_1_panel_current_b = self._io.read_u2le()
            self.channel_1_output_voltage = self._io.read_u2le()
            self.channel_1_output_current = self._io.read_u2le()
            self.channel_1_module_temperature = self._io.read_u2le()
            self.channel_1_board_temperature = self._io.read_u2le()
            self.channel_2_panel_voltage_b = self._io.read_u2le()
            self.channel_2_panel_current_b = self._io.read_u2le()
            self.channel_2_output_voltage = self._io.read_u2le()
            self.channel_2_output_current = self._io.read_u2le()
            self.channel_2_module_temperature = self._io.read_u2le()
            self.channel_2_board_temperature = self._io.read_u2le()
            self.channel_3_panel_voltage_b = self._io.read_u2le()
            self.channel_3_panel_current_b = self._io.read_u2le()
            self.channel_3_output_voltage = self._io.read_u2le()
            self.channel_3_output_current = self._io.read_u2le()
            self.channel_3_module_temperature = self._io.read_u2le()
            self.channel_3_board_temperature = self._io.read_u2le()
            self.channel_4_panel_voltage_b = self._io.read_u2le()
            self.channel_4_panel_current_b = self._io.read_u2le()
            self.channel_4_output_voltage = self._io.read_u2le()
            self.channel_4_output_current = self._io.read_u2le()
            self.channel_4_module_temperature = self._io.read_u2le()
            self.channel_4_board_temperature = self._io.read_u2le()
            self.eps_ioe_state = self._io.read_u1()
            self.eps_ioe_mode = self._io.read_u1()
            self.tcb_temp_0 = self._io.read_u2le()
            self.tcb_temp_1 = self._io.read_u2le()
            self.tcb_temp_2 = self._io.read_u2le()
            self.adcs1_ioe_state = self._io.read_u1()
            self.adcs1_ioe_mode = self._io.read_u1()
            self.posy_mag_x = self._io.read_s2le()
            self.posy_mag_y = self._io.read_s2le()
            self.posy_mag_z = self._io.read_s2le()
            self.posx_mag_x = self._io.read_s2le()
            self.posx_mag_y = self._io.read_s2le()
            self.posx_mag_z = self._io.read_s2le()
            self.negy_mag_x = self._io.read_s2le()
            self.negy_mag_y = self._io.read_s2le()
            self.negy_mag_z = self._io.read_s2le()
            self.negx_mag_x = self._io.read_s2le()
            self.negx_mag_y = self._io.read_s2le()
            self.negx_mag_z = self._io.read_s2le()
            self.posy_internal_temperature = self._io.read_u2le()
            self.posy_external_temperature = self._io.read_u2le()
            self.posx_internal_temperature = self._io.read_u2le()
            self.posx_external_temperature = self._io.read_u2le()
            self.negy_internal_temperature = self._io.read_u2le()
            self.negy_external_temperature = self._io.read_u2le()
            self.negx_internal_temperature = self._io.read_u2le()
            self.negx_external_temperature = self._io.read_u2le()
            self.posy_photodiode = self._io.read_u2le()
            self.posx_photodiode = self._io.read_u2le()
            self.negy_photodiode = self._io.read_u2le()
            self.negx_photodiode = self._io.read_u2le()
            self.mzint_ioe1_state = self._io.read_u1()
            self.mzint_ioe1_mode = self._io.read_u1()
            self.mzint_ioe2_state = self._io.read_u1()
            self.mzint_ioe2_mode = self._io.read_u1()
            self.marina_gpio_status_data = self._io.read_u1()
            self.marina_completed_runs = self._io.read_u2le()
            self.marina_aborted_runs = self._io.read_u2le()
            self.marina_vbatt_voltage = self._io.read_u2le()
            self.marina_vbatt_current = self._io.read_u2le()
            self.marina_temperature = self._io.read_u2le()
            self.marina_2_5v_voltage = self._io.read_u2le()
            self.marina_1_0v_voltage = self._io.read_u2le()
            self.marina_exit_status = self._io.read_u1()
            self.variable_1 = self._io.read_u1()
            self.variable_2 = self._io.read_u1()
            self.variable_3 = self._io.read_u1()
            self.variable_4 = self._io.read_u1()
            self.variable_5 = self._io.read_u1()
            self.variable_6 = self._io.read_u1()
            self.variable_7 = self._io.read_u1()
            self.variable_8 = self._io.read_u1()
            self.variable_9 = self._io.read_u1()
            self.variable_10 = self._io.read_u1()


    class RapHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sync = self._io.read_bytes(2)
            if not self.sync == b"\xAB\xCD":
                raise kaitaistruct.ValidationNotEqualError(b"\xAB\xCD", self.sync, self._io, u"/types/rap_header_t/seq/0")
            self.primary_id = self._io.read_u2be()
            self.secondary_id = self._io.read_u2be()
            self.flags = self._io.read_u1()
            self.packet_length = self._io.read_u2be()
            self.header_checksum = self._io.read_u2be()

        @property
        def spacecraft(self):
            if hasattr(self, '_m_spacecraft'):
                return self._m_spacecraft if hasattr(self, '_m_spacecraft') else None

            self._m_spacecraft = (u"MCUBED-2" if self.secondary_id == 50 else (u"GRIFEX" if self.secondary_id == 66 else (u"TBEX-A" if self.secondary_id == 82 else (u"TBEX-B" if self.secondary_id == 83 else u"unknown"))))
            return self._m_spacecraft if hasattr(self, '_m_spacecraft') else None


    class RapT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_rap_header = self._io.read_bytes(11)
            _io__raw_rap_header = KaitaiStream(BytesIO(self._raw_rap_header))
            self.rap_header = Mxl.RapHeaderT(_io__raw_rap_header, self, self._root)
            _on = self.rap_header.secondary_id
            if _on == 50:
                self.payload = Mxl.Mcubed2BeaconT(self._io, self, self._root)
            elif _on == 66:
                self.payload = Mxl.GrifexBeaconT(self._io, self, self._root)
            elif _on == 82:
                self.payload = Mxl.TbexBeaconT(self._io, self, self._root)
            elif _on == 83:
                self.payload = Mxl.TbexBeaconT(self._io, self, self._root)
            self.crc = self._io.read_u4be()


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


