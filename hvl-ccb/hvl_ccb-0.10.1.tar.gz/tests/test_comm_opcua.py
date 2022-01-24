#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the OPC UA communication protocol.
"""

from time import sleep
from typing import Type

import pytest
from pytest_mock import MockerFixture

from hvl_ccb.comm import (
    OpcUaCommunication,
    OpcUaCommunicationConfig,
    OpcUaCommunicationIOError,
    OpcUaCommunicationTimeoutError,
    OpcUaSubHandler,
)
from masked_comm.opc import DemoServer


@pytest.fixture(scope="module")
def com_config():
    return {
        "host": "127.0.0.1",
        "port": 14125,
        "endpoint_name": "",
        "sub_handler": MySubHandler(),
        "wait_timeout_retry_sec": 0.01,
        "max_timeout_retry_nr": 3,
    }


def test_com_config(com_config):
    # test default values
    config = OpcUaCommunicationConfig(
        **{key: com_config[key] for key in OpcUaCommunicationConfig.required_keys()}
    )
    for key, value in OpcUaCommunicationConfig.optional_defaults().items():
        assert getattr(config, key) == value

    # test setting test values
    config = OpcUaCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"wait_timeout_retry_sec": -0.01},
        {"wait_timeout_retry_sec": 0},
        {"max_timeout_retry_nr": -1},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict):
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        OpcUaCommunicationConfig(**invalid_config)


@pytest.fixture(scope="module")
def demo_opcua_server():
    opcua_server = DemoServer(100, "x", 14125)
    opcua_server.start()

    yield opcua_server

    opcua_server.stop()


@pytest.fixture(scope="module")
def connected_comm_protocol(com_config, demo_opcua_server):
    opc_comm = OpcUaCommunication(com_config)
    opc_comm.open()
    yield opc_comm
    opc_comm.close()


class MySubHandler(OpcUaSubHandler):
    def __init__(self):
        self.change_counter = 0

    def datachange_notification(self, node, val, data):
        super().datachange_notification(node, val, data)
        print(node, val, data)
        self.change_counter += 1


def test_opcua_open_close(com_config, demo_opcua_server):
    # comm I/O errors on open
    config_dict = dict(com_config)
    for config_key, wrong_value in (
        ("host", "Not a host"),
        ("port", 0),
    ):
        config_dict[config_key] = wrong_value
        with pytest.raises(ValueError):
            OpcUaCommunication(config_dict)

    # successful open and close
    opc_comm = OpcUaCommunication(com_config)
    assert opc_comm is not None

    try:
        assert not opc_comm.is_open
        opc_comm.open()
        assert opc_comm.is_open
    finally:
        opc_comm.close()
        assert not opc_comm.is_open


def test_read(connected_comm_protocol, demo_opcua_server):
    demo_opcua_server.set_var("testvar_read", 1.23)
    assert connected_comm_protocol.read("testvar_read", 100) == 1.23


def test_write_read(com_config, demo_opcua_server):
    demo_opcua_server.set_var("testvar_write", 1.23)

    comm_protocol = OpcUaCommunication(com_config)

    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.write("testvar_write", 100, 2.04)
    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.read("testvar_write", 100)

    comm_protocol.open()
    try:
        comm_protocol.write("testvar_write", 100, 2.04)
        assert comm_protocol.read("testvar_write", 100) == 2.04
    finally:
        comm_protocol.close()


def _test_write_client_error(
    raised_error: Type[Exception],
    expected_error: Type[OpcUaCommunicationIOError],
    com_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
):
    comm_protocol = OpcUaCommunication(com_config)

    comm_protocol.open()

    # patch UASocketProtocol.send_request to raise a mock TimeoutError as if coming from
    # used therein concurrent.futures.Future

    # Use bound method (otherwise live unpatch does not work):
    send_request_orig = comm_protocol._client.uaclient.protocol.send_request

    async def send_request(self, request, callback=None, **kwargs):
        if not callback:
            raise raised_error("mock error")
        # method already bound - ignore `self`
        return await send_request_orig(request, callback, **kwargs)

    mocker.patch(
        "asyncua.client.ua_client.UASocketProtocol.send_request",
        side_effect=send_request,
        autospec=True,
    )

    # check error caught and wrapped

    with pytest.raises(expected_error):
        comm_protocol.write("testvar_write", 100, 2.04)

    # comm is closed already on re-tries fails, but should be idempotent

    mocker.patch(
        "asyncua.client.ua_client.UASocketProtocol.send_request",
        side_effect=send_request_orig,
    )

    comm_protocol.close()


def test_write_timeout_error(
    com_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
):
    from concurrent.futures import TimeoutError

    _test_write_client_error(
        TimeoutError,
        OpcUaCommunicationTimeoutError,
        com_config,
        demo_opcua_server,
        mocker,
    )


def test_write_cancelled_error(
    com_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
):
    from concurrent.futures import CancelledError

    _test_write_client_error(
        CancelledError,
        OpcUaCommunicationIOError,
        com_config,
        demo_opcua_server,
        mocker,
    )


def test_init_monitored_nodes(com_config, demo_opcua_server):
    demo_opcua_server.set_var("mon1", 0)
    demo_opcua_server.set_var("mon2", 0)
    demo_opcua_server.set_var("mon3", 0)

    comm_protocol = OpcUaCommunication(com_config)

    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.init_monitored_nodes("mon1", 100)
    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.init_monitored_nodes(["mon2", "mon3"], 100)

    comm_protocol.open()
    try:
        comm_protocol.init_monitored_nodes("mon1", 100)
        comm_protocol.init_monitored_nodes(["mon2", "mon3"], 100)
    finally:
        comm_protocol.close()


def test_datachange(connected_comm_protocol, demo_opcua_server):
    demo_opcua_server.set_var("test_datachange", 0.1)
    connected_comm_protocol.init_monitored_nodes("test_datachange", 100)
    sleep(0.05)

    counter_before = connected_comm_protocol._sub_handler.change_counter
    sleep(1)
    demo_opcua_server.set_var("test_datachange", 0.2)
    assert demo_opcua_server.get_var("test_datachange") == 0.2
    sleep(0.05)
    counter_after = connected_comm_protocol._sub_handler.change_counter
    assert counter_after == counter_before + 1
