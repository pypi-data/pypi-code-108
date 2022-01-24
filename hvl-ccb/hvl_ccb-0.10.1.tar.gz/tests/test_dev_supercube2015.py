#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test module for the Supercube base device class in the old 2015 version.
"""

import pytest

from hvl_ccb.dev.supercube2015 import constants, Supercube2015Base
from masked_comm.opc import DemoServer


@pytest.fixture(scope="module")
def dev_config():
    return {
        "namespace_index": 7,
    }


@pytest.fixture(scope="module")
def com_config():
    return {
        "host": "localhost",
        "port": 14567,
        "endpoint_name": "",
    }


@pytest.fixture(scope="module")
def demo_opcua_server(dev_config):
    opcua_server = DemoServer(dev_config["namespace_index"], "B", 14567)
    opcua_server.start()

    # add socket nodes
    for socket in constants.GeneralSockets:
        opcua_server.set_var(socket, False)

    # add support input and output nodes
    for support in constants.GeneralSupport:
        opcua_server.set_var(support, False)

    for safety in constants.Safety:
        opcua_server.set_var(safety, False)

    for stick in constants.EarthingStick:
        opcua_server.set_var(stick, False)

    opcua_server.set_var(constants.Errors.stop_number, 0)
    opcua_server.set_var(constants.Errors.quit, False)

    opcua_server.set_var(constants.BreakdownDetection.activated, False)
    opcua_server.set_var(constants.BreakdownDetection.triggered, False)

    yield opcua_server

    opcua_server.stop()


@pytest.fixture(scope="module")
def cube(com_config, dev_config, demo_opcua_server: DemoServer):
    cube = Supercube2015Base(com_config, dev_config)
    cube.start()
    yield cube
    cube.stop()


def test_constants():
    assert constants.AlarmText.Alarm0 == "No Alarm."
    assert constants.AlarmText.get(-1) == constants.AlarmText.not_defined


def test_error_datachange(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.Errors.stop_number, 3)


def test_set_remote_control(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    with pytest.raises(NotImplementedError):
        cube.set_remote_control(False)


def test_get_support_input(cube: Supercube2015Base):
    assert cube.get_support_input(1, 1) is False


def test_support_output(cube: Supercube2015Base):
    cube.set_support_output(1, 1, False)
    assert cube.get_support_output(1, 1) is False
    cube.set_support_output(1, 1, True)
    assert cube.get_support_output(1, 1) is True

    with pytest.raises(TypeError):
        cube.set_support_output(1, 1, 1)
    with pytest.raises(TypeError):
        cube.set_support_output(1, 1, 0)
    with pytest.raises(TypeError):
        cube.set_support_output(1, 1, "off")
    with pytest.raises(TypeError):
        cube.set_support_output(1, 1, "on")


def test_set_support_output_impulse(cube: Supercube2015Base):
    cube.set_support_output_impulse(2, 2, 0.01, True)

    with pytest.raises(TypeError):
        cube.set_support_output_impulse(2, 2, 0.01, 1)
    with pytest.raises(TypeError):
        cube.set_support_output_impulse(2, 2, 0.01, 0)
    with pytest.raises(TypeError):
        cube.set_support_output_impulse(2, 2, 0.01, "off")
    with pytest.raises(TypeError):
        cube.set_support_output_impulse(2, 2, 0.01, "on")


def test_get_t13_socket(cube: Supercube2015Base):
    assert cube.get_t13_socket(1) is False
    cube.set_t13_socket(1, True)
    assert cube.get_t13_socket(1) is True

    with pytest.raises(ValueError):
        cube.get_t13_socket(4)


def test_set_t13_socket(cube: Supercube2015Base):
    cube.set_t13_socket(1, True)

    with pytest.raises(ValueError):
        cube.set_t13_socket(4, False)

    with pytest.raises(TypeError):
        cube.set_t13_socket(1, 1)
    with pytest.raises(TypeError):
        cube.set_t13_socket(1, 0)
    with pytest.raises(TypeError):
        cube.set_t13_socket(1, "off")
    with pytest.raises(TypeError):
        cube.set_t13_socket(1, "on")


def test_get_cee16(cube: Supercube2015Base):
    cube.set_cee16_socket(False)
    assert cube.get_cee16_socket() is False
    cube.set_cee16_socket(True)
    assert cube.get_cee16_socket() is True


def test_set_cee16(cube: Supercube2015Base):
    cube.set_cee16_socket(True)
    cube.set_cee16_socket(False)

    with pytest.raises(TypeError):
        cube.set_cee16_socket(1)
    with pytest.raises(TypeError):
        cube.set_cee16_socket(0)
    with pytest.raises(TypeError):
        cube.set_cee16_socket("off")
    with pytest.raises(TypeError):
        cube.set_cee16_socket("on")


def test_get_status(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.Safety.status_green, True)
    demo_opcua_server.set_var(constants.Safety.status_ready_for_red, False)
    assert cube.get_status() == constants.SafetyStatus.GreenNotReady

    demo_opcua_server.set_var(constants.Safety.status_ready_for_red, True)
    assert cube.get_status() == constants.SafetyStatus.GreenReady

    demo_opcua_server.set_var(constants.Safety.status_red, True)
    demo_opcua_server.set_var(constants.Safety.status_green, False)
    assert cube.get_status() == constants.SafetyStatus.RedReady

    demo_opcua_server.set_var(constants.Safety.switchto_operate, True)
    assert cube.get_status() == constants.SafetyStatus.RedOperate

    demo_opcua_server.set_var(constants.Safety.status_error, True)
    demo_opcua_server.set_var(constants.Safety.switchto_operate, False)
    demo_opcua_server.set_var(constants.Safety.status_red, False)
    assert cube.get_status() == constants.SafetyStatus.Error

    demo_opcua_server.set_var(constants.Safety.status_error, False)
    demo_opcua_server.set_var(constants.BreakdownDetection.triggered, True)
    demo_opcua_server.set_var(constants.BreakdownDetection.activated, True)
    assert cube.get_status() == constants.SafetyStatus.QuickStop
    demo_opcua_server.set_var(constants.BreakdownDetection.triggered, False)
    demo_opcua_server.set_var(constants.BreakdownDetection.activated, False)


def test_ready(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.Safety.status_ready_for_red, True)
    demo_opcua_server.set_var(constants.Safety.status_green, True)
    demo_opcua_server.set_var(constants.Safety.status_red, False)
    demo_opcua_server.set_var(constants.Safety.status_error, False)
    demo_opcua_server.set_var(constants.Safety.switchto_operate, False)
    cube.ready(True)
    cube.ready(False)


def test_operate(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.Safety.status_green, False)
    demo_opcua_server.set_var(constants.Safety.status_red, True)
    demo_opcua_server.set_var(constants.Safety.switchto_operate, False)
    demo_opcua_server.set_var(constants.Safety.status_ready_for_red, True)
    demo_opcua_server.set_var(constants.Safety.status_error, False)
    cube.operate(True)
    cube.operate(False)


def test_get_measurement_ratio(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants.MeasurementsDividerRatio.input_1,
        123.4,
    )
    assert cube.get_measurement_ratio(1) == 123.4


def test_get_measurement_voltage(
    cube: Supercube2015Base, demo_opcua_server: DemoServer
):
    demo_opcua_server.set_var(
        constants.MeasurementsScaledInput.input_1,
        110_000,
    )
    assert cube.get_measurement_voltage(1) == 110_000.0


def test_get_earthing_status(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.EarthingStick.status_1_connected, False)
    assert cube.get_earthing_status(1) == constants.EarthingStickStatus.inactive

    demo_opcua_server.set_var(constants.EarthingStick.status_1_connected, True)
    demo_opcua_server.set_var(constants.EarthingStick.status_1_closed, True)
    demo_opcua_server.set_var(constants.EarthingStick.status_1_open, False)
    assert cube.get_earthing_status(1) == constants.EarthingStickStatus.closed

    demo_opcua_server.set_var(constants.EarthingStick.status_1_closed, False)
    assert cube.get_earthing_status(1) == constants.EarthingStickStatus.error

    demo_opcua_server.set_var(constants.EarthingStick.status_1_open, True)
    assert cube.get_earthing_status(1) == constants.EarthingStickStatus.open


def test_earthing_manual(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants.Safety.status_red, False)

    assert cube.get_earthing_manual(1) is False
    cube.set_earthing_manual(1, True)
    assert cube.get_earthing_manual(1) is True

    demo_opcua_server.set_var(constants.Safety.switchto_operate, True)
    demo_opcua_server.set_var(constants.Safety.status_red, True)
    demo_opcua_server.set_var(constants.Safety.status_green, False)
    demo_opcua_server.set_var(constants.Safety.status_error, False)
    demo_opcua_server.set_var(constants.Safety.status_ready_for_red, True)
    with pytest.raises(RuntimeError):
        cube.set_earthing_manual(1, True)


def test_quit_error(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    cube.quit_error()
    assert demo_opcua_server.get_var(constants.Errors.quit) is False


def test_get_door_status(cube: Supercube2015Base, demo_opcua_server: DemoServer):
    with pytest.raises(NotImplementedError):
        cube.get_door_status(1)
