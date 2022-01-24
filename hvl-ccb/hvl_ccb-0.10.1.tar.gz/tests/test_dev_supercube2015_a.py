#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test module for the Supercube Variant A class.
"""

import pytest

from hvl_ccb.dev.supercube2015 import Supercube2015WithFU, constants
from masked_comm.opc import DemoServer


@pytest.fixture(scope="module")
def dev_config():
    return {
        "namespace_index": 7,
    }


@pytest.fixture(scope="module")
def com_config():
    return {"host": "localhost", "port": 14224, "endpoint_name": ""}


@pytest.fixture(scope="module")
def demo_server(dev_config):
    opcua_server = DemoServer(dev_config["namespace_index"], "A", 14224)
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

    opcua_server.set_var(constants.BreakdownDetection.activated, False)
    opcua_server.set_var(constants.BreakdownDetection.triggered, False)

    yield opcua_server

    opcua_server.stop()


@pytest.fixture(scope="module")
def cube(com_config, dev_config, demo_server):
    cube = Supercube2015WithFU(com_config, dev_config)
    cube.start()
    yield cube
    cube.stop()


def test_instantiation(com_config):
    cube = Supercube2015WithFU(com_config)
    assert cube is not None


def test_set_voltage(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.voltage_target, 0.0)
    cube.set_target_voltage(20e3)
    assert demo_server.get_var(constants.Power.voltage_target) == 20.0


def test_get_voltage(cube: Supercube2015WithFU, demo_server: DemoServer):
    cube.set_target_voltage(1e3)
    assert cube.get_target_voltage() == 1e3


def test_get_max_voltage(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.voltage_max, 80)
    assert cube.get_max_voltage() == 80.0e3


def test_set_slope(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.voltage_slope, 1.5)
    cube.set_slope(5.5e3)
    assert demo_server.get_var(constants.Power.voltage_slope) == 5.5


def test_get_primary_voltage(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.voltage_primary, 23.2)
    assert cube.get_primary_voltage() == 23.2


def test_get_primary_current(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.current_primary, 1.2)
    assert cube.get_primary_current() == 1.2


def test_get_frequency(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.frequency, 50)
    assert cube.get_frequency() == 50.0


def test_get_power_setup(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.Power.setup, 1)
    assert cube.get_power_setup() == constants.PowerSetup(1)


def test_get_fso_active(cube: Supercube2015WithFU, demo_server: DemoServer):
    demo_server.set_var(constants.BreakdownDetection.activated, True)
    assert cube.get_fso_active() is True


def test_fso_reset(cube: Supercube2015WithFU, demo_server: DemoServer):
    cube.fso_reset()
    assert demo_server.get_var(constants.BreakdownDetection.reset) is False
