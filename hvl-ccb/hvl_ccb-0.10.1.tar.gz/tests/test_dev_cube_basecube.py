#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test module for the BaseCube device class.

NOTE: After a variable is set for the first time, the type is fixed! This can usually
happen for numerical values. Therefore, we should always use 'float' as datatype for
numerical variables.

GOOD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0.0)

BAD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0)
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from time import sleep
from typing import List

import pytest
from pytest_mock import MockerFixture

from hvl_ccb.comm import OpcUaCommunicationIOError, OpcUaCommunicationTimeoutError
from hvl_ccb.dev.cube import (
    constants,
    BaseCube,
    BaseCubeConfiguration,
    CubeEarthingStickOperationError,
    BaseCubeOpcUaCommunication,
    CubeStatusChangeError,
    CubeStopError,
    CubeRemoteControlError,
)
from masked_comm.opc import DemoServer


@pytest.fixture(scope="module")
def dev_config():
    return {
        "namespace_index": 3,
        "polling_delay_sec": 0.05,
        "polling_interval_sec": 0.01,
        "timeout_interval": 0.1,
        "timeout_status_change": 6,
        "noise_level_measurement_channel_1": 100,
        "noise_level_measurement_channel_2": 100,
        "noise_level_measurement_channel_3": 100,
        "noise_level_measurement_channel_4": 100,
    }


@pytest.fixture(scope="module")
def com_config():
    return {
        "host": "localhost",
        "port": 14123,
        "wait_timeout_retry_sec": 0.01,
        "max_timeout_retry_nr": 3,
    }


@pytest.fixture(scope="module")
def demo_opcua_server(dev_config):
    opcua_server = DemoServer(
        dev_config["namespace_index"], constants._CubeOpcEndpoint.BASE_CUBE, 14123
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

    for i, alarm in enumerate(constants._Alarms):
        opcua_server.set_var(alarm, bool(i % 2))

    # add remote control vars
    opcua_server.set_var(constants._OpcControl.ACTIVE, False)
    opcua_server.set_var(constants._OpcControl.LIVE, False)

    yield opcua_server

    opcua_server.stop()


@pytest.fixture(scope="module")
def opened_basecube_com(
    com_config,
    dev_config,
    demo_opcua_server: DemoServer,
):
    opc_comm = BaseCubeOpcUaCommunication(com_config)
    opc_comm.open()
    yield opc_comm
    opc_comm.close()


def _get_logged_messages(
    caplog,
    expected_logger_name: str,
    expected_level: int,
) -> List[str]:
    return [
        message
        for logger_name, level, message in caplog.record_tuples
        if logger_name == expected_logger_name and level == expected_level
    ]


def test_basecube_subscription_handler_datachange_safetystatus(
        opened_basecube_com,
        dev_config: dict,
        demo_opcua_server: DemoServer,
        caplog,  # pytest._logging.LogCaptureFixture
):
    ns_index = dev_config["namespace_index"]

    caplog.set_level(logging.INFO)

    # test a status datachange
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.INITIALIZING)
    )
    opened_basecube_com.init_monitored_nodes(str(constants._Safety.STATUS), ns_index)
    sleep(0.05)

    demo_opcua_server.set_var(
        constants._Safety.STATUS,
        int(constants.SafetyStatus.GREEN_NOT_READY),
    )
    sleep(0.05)

    # FIXME: does not work in gitlab CI
    # check presence of log messages in a correct order
    # assert [
    #     f"Safety: {str(constants.SafetyStatus.Initializing)}",
    #     f"Safety: {str(constants.SafetyStatus.GreenNotReady)}",
    # ] == _get_logged_messages(caplog, "hvl_ccb.dev.basecube.base", logging.INFO)


def test_basecube_subscription_handler_datachange_earthingstickstatus(
        opened_basecube_com,
        dev_config: dict,
        demo_opcua_server: DemoServer,
        caplog,  # pytest._logging.LogCaptureFixture
):
    ns_index = dev_config["namespace_index"]

    caplog.set_level(logging.INFO)

    # test an earthing stick status datachange
    for i in constants._EarthingStick._STICKS:
        demo_opcua_server.set_var(
            constants._EarthingStick("", i)._CMD_STATUS,
            int(constants.EarthingStickStatus.INACTIVE),
        )
        opened_basecube_com.init_monitored_nodes(
            constants._EarthingStick("", i)._CMD_STATUS, ns_index
        )
    sleep(0.05)

    for i in constants._EarthingStick._STICKS:
        demo_opcua_server.set_var(
            constants._EarthingStick("", i)._CMD_STATUS,
            int(constants.EarthingStickStatus.CLOSED)
        )
    sleep(0.05)

    # FIXME: does not work in gitlab CI
    # check presence of log messages in a correct order
    # assert (
    #     [
    #         f"Earthing {ess.number}: {str(constants.EarthingStickStatus.inactive)}"
    #         for ess in ess_tuple
    #     ]
    #     + [
    #         f"Earthing {ess.number}: {str(constants.EarthingStickStatus.closed)}"
    #         for ess in ess_tuple
    #     ]
    # ) == _get_logged_messages(caplog, "hvl_ccb.dev.basecube.base", logging.INFO)


@pytest.fixture(scope="module")
def cube(com_config, dev_config, demo_opcua_server: DemoServer):
    cube = BaseCube(com_config, dev_config)
    demo_opcua_server.set_var(constants._OpcControl.TIME, [0, 0, 0, 0, 0, 0, 0])
    cube.start()
    yield cube
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.STOP_SAFETY_STATUSES[-1]),
    )
    cube.stop()


def test_dev_config(dev_config):
    # currently there are no non-default config values
    config = BaseCubeConfiguration(**dev_config)
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
    ],
)
def test_invalid_config_dict_value_error(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        BaseCubeConfiguration(**invalid_config)


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"noise_level_measurement_channel_1": "100"},
    ],
)
def test_invalid_config_dict_type_error(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(TypeError):
        BaseCubeConfiguration(**invalid_config)


def test_set_remote_control(cube: BaseCube, demo_opcua_server: DemoServer):
    cube._set_remote_control(False)
    assert demo_opcua_server.get_var(constants._OpcControl.ACTIVE) is False
    cube._set_remote_control(True)
    assert demo_opcua_server.get_var(constants._OpcControl.ACTIVE) is True

    with pytest.raises(TypeError):
        cube._set_remote_control(1)
    with pytest.raises(TypeError):
        cube._set_remote_control(0)
    with pytest.raises(TypeError):
        cube._set_remote_control("off")
    with pytest.raises(TypeError):
        cube._set_remote_control("on")

    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    with pytest.raises(CubeRemoteControlError):
        cube._set_remote_control(False)
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )


def test_status_poller(
    com_config,
    dev_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
):

    cube = BaseCube(com_config, dev_config)
    poller = cube._status_poller
    assert poller is not None
    assert poller.polling_delay_sec == dev_config["polling_delay_sec"]
    assert poller.polling_interval_sec == dev_config["polling_interval_sec"]
    assert poller.polling_timeout_sec is None
    assert poller.spoll_handler == cube._spoll_handler

    spy_spoll_handler = mocker.spy(poller, "spoll_handler")
    spy_start_polling = mocker.spy(poller, "start_polling")
    spy_stop_polling = mocker.spy(poller, "stop_polling")

    poller.stop_polling()
    assert spy_stop_polling.spy_return is False
    demo_opcua_server.set_var(constants._OpcControl.TIME, [0, 0, 0, 0, 0, 0, 0])
    cube.start()

    spy_start_polling.assert_called()
    assert spy_start_polling.spy_return is True

    poller.start_polling()
    assert spy_start_polling.spy_return is False

    sleep(dev_config["polling_delay_sec"] + 3 * dev_config["polling_interval_sec"])
    spy_spoll_handler.assert_called()
    assert spy_spoll_handler.spy_return is None

    cube.stop()
    spy_stop_polling.assert_called()
    assert spy_stop_polling.spy_return is True


def test_status_poller_timeout_error(
    com_config,
    dev_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
):

    cube = BaseCube(com_config, dev_config)
    demo_opcua_server.set_var(constants._OpcControl.TIME, [0, 0, 0, 0, 0, 0, 0])
    cube.start()
    assert cube._status_poller.is_polling()
    assert cube.com.is_open

    # patch UASocketProtocol.send_request to raise a mock TimeoutError as if coming from
    # used therein concurrent.futures.Future;
    # raise error only on disable remote control done via poller thread on stop()
    # => write(constants.OpcControl.active, False)

    # Use bound method (otherwise live unpatch does not work):
    send_request_orig = cube.com._client.uaclient.protocol.send_request

    async def send_request(self, request, *args, **kwargs):
        if (
            hasattr(request, "Parameters")
            and hasattr(request.Parameters, "NodesToWrite")
        ):
            node_to_write = request.Parameters.NodesToWrite[0]
            if (
                node_to_write.NodeId.Identifier == constants._OpcControl.ACTIVE
                and node_to_write.Value.Value.Value is False
            ):
                from concurrent.futures import TimeoutError

                raise TimeoutError("mock timeout error")
        # method already bound - ignore `self`
        return await send_request_orig(request, *args, **kwargs)

    mocker.patch(
        "asyncua.client.ua_client.UASocketProtocol.send_request",
        side_effect=send_request,
        autospec=True,
    )

    # check poller thread error caught and wrapped
    with pytest.raises(OpcUaCommunicationTimeoutError):
        cube._set_remote_control(False)
    assert not cube._status_poller.is_polling()
    assert cube.com.is_open

    # check that stopping also does raises the error, but cleans up otherwise
    cube._set_remote_control(True)
    with pytest.raises(OpcUaCommunicationTimeoutError):
        cube.stop()
    assert not cube._status_poller.is_polling()
    assert not cube.com.is_open

    # unpatch and try to stop dev again - will raise error due to broken com,
    # but not the timeout
    mocker.patch(
        "asyncua.client.ua_client.UASocketProtocol.send_request",
        side_effect=send_request_orig,
    )

    with pytest.raises(OpcUaCommunicationIOError) as excinfo:
        cube.stop()
        assert excinfo.type is not OpcUaCommunicationTimeoutError
    assert not cube._status_poller.is_polling()
    assert not cube.com.is_open


def test_support_input(cube: BaseCube):
    assert cube.support_1.input_1 is False
    assert cube.support_1.input_2 is False


def test_support_output(cube: BaseCube):
    cube.support_1.output_1 = False
    assert cube.support_1.output_1 is False
    cube.support_1.output_1 = True
    assert cube.support_1.output_1 is True

    cube.support_1.output_2 = False
    assert cube.support_1.output_2 is False
    cube.support_1.output_2 = True
    assert cube.support_1.output_2 is True

    with pytest.raises(TypeError):
        cube.support_1.output_1 = 1
    with pytest.raises(TypeError):
        cube.support_1.output_1 = 0
    with pytest.raises(TypeError):
        cube.support_1.output_1 = "off"
    with pytest.raises(TypeError):
        cube.support_1.output_1 = "on"


def test_t13_socket(cube: BaseCube):
    assert cube.t13_socket_1 is False
    cube.t13_socket_1 = True
    assert cube.t13_socket_1 is True
    with pytest.raises(TypeError):
        cube.t13_socket_1 = 1
    with pytest.raises(TypeError):
        cube.t13_socket_1 = 0
    with pytest.raises(TypeError):
        cube.t13_socket_1 = "off"
    with pytest.raises(TypeError):
        cube.t13_socket_1 = "on"


def test_cee16_socket(cube: BaseCube):
    cube.cee16_socket = False
    assert cube.cee16_socket is False
    cube.cee16_socket = True
    assert cube.cee16_socket is True

    with pytest.raises(TypeError):
        cube.cee16_socket = 1
    with pytest.raises(TypeError):
        cube.cee16_socket = 0
    with pytest.raises(TypeError):
        cube.cee16_socket = "off"
    with pytest.raises(TypeError):
        cube.cee16_socket = "on"


def test_get_status(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Safety.STATUS, 1)
    assert cube.status == constants.SafetyStatus.GREEN_NOT_READY

    demo_opcua_server.set_var(constants._Safety.STATUS, 2)
    assert cube.status == constants.SafetyStatus.GREEN_READY


def _switch_safety_status(
    demo_opcua_server: DemoServer,
    safety_status: constants.SafetyStatus,
    delay: float = BaseCubeConfiguration.timeout_interval * 2,
):
    sleep(delay)
    demo_opcua_server.set_var(constants._Safety.STATUS, int(safety_status))


def test_ready(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._SafetyStatusTransition.SWITCH_TO_READY.command, False
    )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(
        _switch_safety_status, demo_opcua_server, constants.SafetyStatus.RED_READY,
    )
    cube.ready = True
    assert demo_opcua_server.get_var(
        constants._SafetyStatusTransition.SWITCH_TO_READY.command
    ) is True
    executor.submit(
        _switch_safety_status, demo_opcua_server, constants.SafetyStatus.GREEN_READY,
    )
    assert cube.ready is True
    cube.ready = False
    assert demo_opcua_server.get_var(
        constants._SafetyStatusTransition.SWITCH_TO_READY.command
    ) is False
    assert cube.ready is False
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    assert cube.ready is None


def test_operate(cube: BaseCube, demo_opcua_server: DemoServer):
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
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )
    assert cube.operate is None


def test_switch_safety_status(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_NOT_READY)
    )
    with pytest.raises(CubeStatusChangeError):
        cube._switch_safety_status(
            constants._SafetyStatusTransition.SWITCH_TO_READY, True
        )
    with pytest.raises(CubeStatusChangeError):
        cube._switch_safety_status(
            constants._SafetyStatusTransition.SWITCH_TO_READY, False
        )
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )
    with pytest.raises(CubeStatusChangeError):
        cube._switch_safety_status(
            constants._SafetyStatusTransition.SWITCH_TO_READY, True
        )


def test_get_measurement_ratio(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._MeasurementChannel("", 1, 400)._CMD_RATIO, 123.4
    )
    assert cube.measurement_ch_1.ratio == 123.4


def test_get_measurement_voltage(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._MeasurementChannel("", 1, 400)._CMD_SCALE, True
    )
    demo_opcua_server.set_var(
        constants._MeasurementChannel("", 1, 400)._CMD_VOLTAGE, 110
    )
    assert cube.measurement_ch_1.voltage == 110_000.0
    demo_opcua_server.set_var(
        constants._MeasurementChannel("", 1, 400)._CMD_SCALE, False
    )
    demo_opcua_server.set_var(
        constants._MeasurementChannel("", 1, 400)._CMD_VOLTAGE, 110
    )
    assert cube.measurement_ch_1.voltage == 110


def test_get_earthing_stick_status(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._EarthingStick("", 1)._CMD_STATUS, 1)
    assert cube.earthing_stick_1.status == constants.EarthingStickStatus(1)


def test_get_earthing_stick_operating_status(
    cube: BaseCube, demo_opcua_server: DemoServer
):
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_OPERATING_STATUS,
        constants.EarthingStickOperatingStatus.AUTO,
    )
    assert (
        cube.earthing_stick_1.operating_status
        is constants.EarthingStickOperatingStatus.AUTO
    )


def test_get_earthing_stick_manual(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_MANUAL,
        bool(constants.EarthingStickOperation.CLOSE)
    )
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.CLOSE


def test_operate_earthing_stick(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_OPERATING_STATUS,
        constants.EarthingStickOperatingStatus.MANUAL,
    )
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_MANUAL,
        bool(constants.EarthingStickOperation.OPEN)
    )

    # Tests @ READ_READY
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.OPEN
    cube.earthing_stick_1.operate = constants.EarthingStickOperation.CLOSE
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.CLOSE
    cube.earthing_stick_1.operate = False
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.OPEN

    # Tests @ READ_OPERATE
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_OPERATE)
    )
    cube.earthing_stick_1.operate = constants.EarthingStickOperation.OPEN
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.OPEN
    cube.earthing_stick_1.operate = constants.EarthingStickOperation.CLOSE
    assert cube.earthing_stick_1.operate is constants.EarthingStickOperation.CLOSE

    # No operation @ GREEN_READY
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.GREEN_READY)
    )
    with pytest.raises(CubeEarthingStickOperationError):
        cube.earthing_stick_1.operate = True

    # No operation in non-manual mode
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_OPERATING_STATUS,
        constants.EarthingStickOperatingStatus.AUTO,
    )
    with pytest.raises(CubeEarthingStickOperationError):
        cube.earthing_stick_1.operate = True


def test_operate_earthing_stick_error(
    cube: BaseCube,
    demo_opcua_server: DemoServer,
):
    demo_opcua_server.set_var(
        constants._EarthingStick("", 1)._CMD_OPERATING_STATUS,
        constants.EarthingStickOperatingStatus.AUTO,
    )
    with pytest.raises(CubeEarthingStickOperationError):
        cube.earthing_stick_1.operate = constants.EarthingStickOperation.CLOSE


def test_quit_error(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Errors.QUIT, False)
    cube.quit_error()
    assert demo_opcua_server.get_var(constants._Errors.QUIT) is False


def test_get_door_status(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._Door(1, "")._CMD, 2)
    assert cube.door_1_status == constants.DoorStatus(2)


def test_base_descriptor(cube: BaseCube, demo_opcua_server: DemoServer):
    with pytest.raises(AttributeError):
        cube.door_1_status = True


def test_get_earthing_rod_status(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._EarthingRod(1, "")._CMD, 0)
    assert cube.earthing_rod_1_status == constants.EarthingRodStatus(0)
    demo_opcua_server.set_var(constants._EarthingRod(1, "")._CMD, 1)
    assert cube.earthing_rod_1_status == constants.EarthingRodStatus(1)


def test_get_breakdown_detection_active(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._BreakdownDetection.ACTIVATED, True)
    assert cube.breakdown_detection_active is True


def test_get_breakdown_detection_triggered(
        cube: BaseCube, demo_opcua_server: DemoServer
):
    demo_opcua_server.set_var(constants._BreakdownDetection.TRIGGERED, True)
    assert cube.breakdown_detection_triggered is True


def test_breakdown_detection_reset(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(constants._BreakdownDetection.RESET, False)
    cube.breakdown_detection_reset()
    assert demo_opcua_server.get_var(constants._BreakdownDetection.RESET) is False


def test_set_status_board(cube: BaseCube, demo_opcua_server: DemoServer):

    n_max = len(constants.MessageBoard)

    with pytest.raises(ValueError):
        cube.set_status_board(["x"] * (n_max + 1))
    with pytest.raises(ValueError):
        cube.set_status_board(["x"], pos=[n_max])

    for line in constants.MessageBoard:
        demo_opcua_server.set_var(line, "")

    msgs = ["Hello World", "Hello Fabian", "Hello HVL"]

    cube.set_status_board(msgs[:1])
    assert demo_opcua_server.get_var(constants.MessageBoard.line(1)) == msgs[0]
    cube.set_status_board(msgs[:1], pos=[1], clear_board=False)
    assert demo_opcua_server.get_var(constants.MessageBoard.line(1)) == msgs[0]
    assert demo_opcua_server.get_var(constants.MessageBoard.line(2)) == msgs[0]

    positions = [4, 8, 12]
    cube.set_status_board(msgs, positions, clear_board=False)
    for i, p in enumerate(positions):
        assert demo_opcua_server.get_var(constants.MessageBoard.line(p + 1)) == msgs[i]

    cube.set_status_board([str(i) for i in range(15)])
    for i in range(15):
        assert demo_opcua_server.get_var(constants.MessageBoard.line(i + 1)) == str(i)


def test_set_message_board(cube: BaseCube, demo_opcua_server: DemoServer):

    n_max = len(constants.MessageBoard)

    with pytest.raises(ValueError):
        cube.set_message_board(["x"] * (n_max + 1))

    for line in constants.MessageBoard:
        demo_opcua_server.set_var(line, "")

    msgs = ["ERROR: This is unexpected", "Good choice"]
    cube.set_message_board(msgs[:1])
    assert demo_opcua_server.get_var(constants.MessageBoard.line(1)).endswith(msgs[0])

    # push two messages to first two lines, in the given order
    cube.set_message_board(msgs)
    assert demo_opcua_server.get_var(constants.MessageBoard.line(1)).endswith(msgs[0])
    assert demo_opcua_server.get_var(constants.MessageBoard.line(2)).endswith(msgs[1])
    assert demo_opcua_server.get_var(constants.MessageBoard.line(3)).endswith(msgs[0])

    # overwrite all messages except last, which is pushed to be last line
    cube.set_message_board("x" * (n_max - 1))
    for n in range(len(constants.MessageBoard) - 1):
        assert demo_opcua_server.get_var(constants.MessageBoard.line(n + 1)).endswith(
            "x"
        )
    last_msg = demo_opcua_server.get_var(constants.MessageBoard.line(n_max))
    assert last_msg.endswith(msgs[0])


def test_active_alarms(cube: BaseCube, demo_opcua_server: DemoServer):
    cube._com.config.sub_handler.alarm_status = constants._AlarmsOverview()
    cube._com.config.sub_handler.alarm_status.alarm_50 = constants._AlarmStatus.ACTIVE
    assert cube.active_alarms(False) == [50]
    assert cube.active_alarms(True) == ["OPC Connection active"]


def test_stop(cube: BaseCube, demo_opcua_server: DemoServer):
    demo_opcua_server.set_var(
        constants._Safety.STATUS, int(constants.SafetyStatus.RED_READY)
    )
    with pytest.raises(CubeStopError):
        cube.stop()
