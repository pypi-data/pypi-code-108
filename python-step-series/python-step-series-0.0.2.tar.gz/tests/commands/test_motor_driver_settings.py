#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC commands for motor driver settings build properly."""


from stepseries import commands


def test_set_microstep_mode() -> None:
    builder = commands.SetMicrostepMode(4, 3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.STEP_SEL
    assert osc_message_str == "/setMicrostepMode 4 3"


def test_get_microstep_mode() -> None:
    builder = commands.GetMicrostepMode(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getMicrostepMode 4"


def test_enable_low_speed_optimize() -> None:
    builder = commands.EnableLowSpeedOptimize(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableLowSpeedOptimize 2 1"


def test_set_low_speed_optimize_threshold() -> None:
    builder = commands.SetLowSpeedOptimizeThreshold(3, 0.5)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.lowSpeedOptimizationThreshold
    assert osc_message_str == "/setLowSpeedOptimizeThreshold 3 0.5"


def test_get_low_speed_optimize_threshold() -> None:
    builder = commands.GetLowSpeedOptimizeThreshold(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getLowSpeedOptimizeThreshold 1"


def test_enable_busy_report() -> None:
    builder = commands.EnableBusyReport(1, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableBusyReport 1 1"


def test_get_busy() -> None:
    builder = commands.GetBusy(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getBusy 1"


def test_enable_hiz_report() -> None:
    builder = commands.EnableHiZReport(1, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableHizReport 1 1"


def test_get_hiz() -> None:
    builder = commands.GetHiZ(1)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getHiZ 1"


def test_get_dir() -> None:
    builder = commands.GetDir(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getDir 2"


def test_enable_dir_report() -> None:
    builder = commands.EnableDirReport(4, False)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableDirReport 4 0"


def test_enable_motor_status_report() -> None:
    builder = commands.EnableMotorStatusReport(2, True)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.enable
    assert osc_message_str == "/enableMotorStatusReport 2 1"


def test_get_motor_status() -> None:
    builder = commands.GetMotorStatus(2)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getMotorStatus 2"


def test_set_position_report_interval() -> None:
    builder = commands.SetPositionReportInterval(4, 150)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 2
    assert params[0] == builder.motorID
    assert params[1] == builder.interval
    assert osc_message_str == "/setPositionReportInterval 4 150"


def test_set_position_list_report_interval() -> None:
    builder = commands.SetPositionListReportInterval(10)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.interval
    assert osc_message_str == "/setPositionListReportInterval 10"


def test_get_adc_val() -> None:
    builder = commands.GetAdcVal(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getAdcVal 3"


def test_get_status() -> None:
    builder = commands.GetStatus(3)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getStatus 3"


def test_get_config_register() -> None:
    builder = commands.GetConfigRegister(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/getConfigRegister 4"


def test_reset_motor_driver() -> None:
    builder = commands.ResetMotorDriver(4)
    osc_message = builder.build()
    osc_message_str = builder.stringify()
    params = osc_message.params

    assert osc_message.address == builder.address
    assert len(params) == 1
    assert params[0] == builder.motorID
    assert osc_message_str == "/resetMotorDriver 4"
