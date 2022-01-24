#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test module for the PICube class

NOTE: After a variable is set for the first time, the type is fixed! This can usually
happen for numerical values. Therefore, we should always use 'float' as datatype for
numerical variables.

GOOD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0.0)

BAD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0)
"""

import pytest
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from time import sleep

from hvl_ccb.dev.cube import constants, PICube, PICubeConfiguration
from masked_comm.opc import DemoServer


@pytest.fixture(scope="module")
def dev_config():
    return {
        "namespace_index": 3,
        "polling_delay_sec": 0.05,
        "polling_interval_sec": 0.01,
        "timeout_interval": 0.1,
        "timeout_status_change": 6,
        "timeout_test_parameters": 2,
        "noise_level_measurement_channel_1": 100,
        "noise_level_measurement_channel_2": 100,
        "noise_level_measurement_channel_3": 100,
        "noise_level_measurement_channel_4": 100,
    }


@pytest.fixture(scope="module")
def com_config():
    return {"host": "localhost", "port": 14124}


@pytest.fixture(scope="module")
def demo_opcua_server(dev_config):
    opcua_server = DemoServer(
        dev_config["namespace_index"], constants._CubeOpcEndpoint.PI_CUBE, 14124
    )
    opcua_server.start()

    # add socket for CEE16
    opcua_server.set_var(constants._CEE16, False)
    # add T13 sockets
    for socket in constants._T13Socket._SOCKETS:
        opcua_server.set_var(constants._T13Socket(socket)._CMD, False)

    # add support input and output nodes
    for io, port, contact in product(
            constants._SupportPort._IOS,
            constants._SupportPort._PORTS,
            constants._SupportPort._CONTACTS
    ):
        opcua_server.set_var(constants._SupportPort("", port)._cmd(io, contact), False)

    opcua_server.set_var(constants._OpcControl.ACTIVE, False)
    opcua_server.set_var(constants._OpcControl.LIVE, False)

    yield opcua_server

    opcua_server.stop()


@pytest.fixture(scope="module")
def cube(com_config, dev_config, demo_opcua_server):
    cube = PICube(com_config, dev_config)
    demo_opcua_server.set_var(constants._OpcControl.TIME, [0, 0, 0, 0, 0, 0, 0])
    cube.start()
    yield cube
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.STOP_SAFETY_STATUSES[-1]),
    )
    cube.stop()


def test_instantiation(com_config):
    cube = PICube(com_config)
    assert cube is not None


def test_dev_config(dev_config):
    # currently there are no non-default config values
    config = PICubeConfiguration(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"namespace_index": -1},
        {"polling_interval_sec": -1},
        {"polling_interval_sec": 0},
        {"polling_delay_sec": -1},
        {"timeout_interval": 0},
        {"timeout_status_change": -1},
        {"timeout_test_parameters": -1},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        PICubeConfiguration(**invalid_config)


def test_high_voltage_test_parameter(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_150KV.value
    )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_TARGET, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_SLOPE, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_MAX, 50e3)
    demo_opcua_server.set_var(
        constants._Power.POLARITY, int(constants.Polarity.POSITIVE)
    )
    cube.test_parameter.voltage = 20e3
    cube.test_parameter.slope = 5.5e3
    assert cube.test_parameter.voltage == 20e3
    assert cube.test_parameter.slope == 5.5e3


def test_low_voltage_test_parameter(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.POWER_INVERTER_220V.value
    )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_TARGET, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_SLOPE, 0.0)
    cube.test_parameter.voltage = 10.5
    cube.test_parameter.slope = 1.5
    assert cube.test_parameter.voltage == 10.5
    assert cube.test_parameter.slope == 1.5


def test_dc_test_parameter(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.DC_140KV.value
    )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_TARGET, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_SLOPE, 0.0)
    demo_opcua_server.set_var(
        constants._Power.POLARITY, constants.Polarity.POSITIVE.value
    )
    cube.test_parameter.voltage = 10_500
    cube.test_parameter.slope = 1_500
    assert cube.test_parameter.voltage == 10_500
    assert cube.test_parameter.slope == 1_500
    demo_opcua_server.set_var(
        constants._Power.POLARITY, constants.Polarity.NEGATIVE.value
    )
    cube.test_parameter.voltage = -10_500
    assert cube.test_parameter.voltage == -10_500


def test_test_parameter_power_setup(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_150KV.value
    )
    assert cube.test_parameter.power_setup is None
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.NO_SOURCE.value
    )
    assert cube.test_parameter.power_setup is None


def test_test_parameters_error(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_150KV.value
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_TARGET, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_SLOPE, 0.0)
    demo_opcua_server.set_var(constants._Power.VOLTAGE_MAX, 50.)
    with pytest.raises(ValueError):
        cube.test_parameter.voltage = 60e3

    with pytest.raises(ValueError):
        cube.test_parameter.slope = 20e3

    # try to set slope and voltage in wrong Safety Status State
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    cube.test_parameter.slope = 1
    cube.test_parameter.voltage = 1


def _switch_safety_status(
    demo_opcua_server: DemoServer,
    safety_status: constants.SafetyStatus,
    delay: float = PICubeConfiguration.timeout_interval * 2,
):
    sleep(delay)
    demo_opcua_server.set_var(constants._Safety.STATUS, int(safety_status))


def _operate_test_procedure(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Power.VOLTAGE_ACTUAL, 0)
    demo_opcua_server.set_var(
        constants._SafetyStatusTransition.SWITCH_TO_OPERATE.command, False
    )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(
        _switch_safety_status, demo_opcua_server, constants.SafetyStatus.RED_OPERATE,
    )
    cube.operate = True
    assert demo_opcua_server.get_var(
        constants._SafetyStatusTransition.SWITCH_TO_OPERATE.command
    ) is True
    executor.submit(
        _switch_safety_status, demo_opcua_server, constants.SafetyStatus.RED_READY,
    )
    assert cube.operate is True
    cube.operate = False
    assert demo_opcua_server.get_var(
        constants._SafetyStatusTransition.SWITCH_TO_OPERATE.command
    ) is False
    assert cube.operate is False


def test_operate(cube: PICube, demo_opcua_server: DemoServer):
    _operate_test_procedure(cube, demo_opcua_server)
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )
    assert cube.operate is None
    demo_opcua_server.set_var(constants._Power.VOLTAGE_ACTUAL, 60_000)
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    cube.operate = False


def test_operate_dc(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.DC_140KV.value
    )
    _operate_test_procedure(cube, demo_opcua_server)


def test_operate_pi(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.POWER_INVERTER_220V.value
    )
    _operate_test_procedure(cube, demo_opcua_server)


def test_operate_external(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.EXTERNAL_SOURCE.value
    )
    _operate_test_procedure(cube, demo_opcua_server)


def test_get_max_voltage_high_voltage(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_150KV.value
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_MAX, 80.)
    assert cube.voltage_max == 80_000.0


def test_get_max_voltage_power_inverter(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.POWER_INVERTER_220V.value
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_MAX, 80.)
    assert cube.voltage_max == 80.0


def test_get_actual_voltage(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_150KV.value
    )
    demo_opcua_server.set_var(constants._Power.VOLTAGE_ACTUAL, 80)
    assert cube.voltage_actual == 80_000.0


def test_get_primary_voltage(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Power.VOLTAGE_PRIMARY, 23.2)
    assert cube.voltage_primary == 23.2


def test_get_primary_current(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Power.CURRENT_PRIMARY, 1.2)
    assert cube.current_primary == 1.2


def test_get_frequency(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Power.FREQUENCY, 50)
    assert cube.frequency == 50.0


def test_get_power_setup(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, int(constants.PowerSetup.EXTERNAL_SOURCE)
    )
    assert cube.power_setup == constants.PowerSetup.EXTERNAL_SOURCE


def test_get_polarity(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.DC_140KV.value
    )
    demo_opcua_server.set_var(
        constants._Power.POLARITY, int(constants.Polarity.POSITIVE)
    )
    assert cube.polarity == constants.Polarity.POSITIVE
    demo_opcua_server.set_var(
        constants._Power.POLARITY, int(constants.Polarity.NEGATIVE)
    )
    assert cube.polarity == constants.Polarity.NEGATIVE


def test_get_polarity_error(cube: PICube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Power.SETUP, constants.PowerSetup.AC_100KV.value
    )
    demo_opcua_server.set_var(
        constants._Power.POLARITY, int(constants.Polarity.POSITIVE)
    )
    assert cube.polarity is None
