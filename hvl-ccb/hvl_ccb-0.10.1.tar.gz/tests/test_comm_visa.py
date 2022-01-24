#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the VISA CommunicationProtocol.
"""

import dataclasses

import pytest

from hvl_ccb.comm import (
    VisaCommunication,
    VisaCommunicationError,
    VisaCommunicationConfig,
)


@pytest.fixture(scope='module')
def testconfig_instr():
    return VisaCommunicationConfig(
        interface_type=VisaCommunicationConfig.InterfaceType.TCPIP_INSTR,
        host='127.0.0.1',
        open_timeout=1,
    )


@pytest.fixture(scope='module')
def testconfig_socket():
    return VisaCommunicationConfig(
        interface_type=VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET,
        host='127.0.0.1',
        open_timeout=1,
    )


def test_visa_config(testconfig_instr, testconfig_socket):
    vcom = VisaCommunication(testconfig_instr)
    assert vcom is not None

    # test string value for interface_type
    vcom = VisaCommunication(
        dataclasses.replace(testconfig_instr, interface_type='TCPIP_INSTR')
    )
    assert vcom.config.interface_type == testconfig_instr.interface_type

    vcom = VisaCommunication(testconfig_socket)
    assert vcom is not None

    with pytest.raises(ValueError):
        dataclasses.replace(testconfig_instr, board=-1)

    with pytest.raises(ValueError):
        dataclasses.replace(testconfig_instr, timeout=-1)

    with pytest.raises(ValueError):
        dataclasses.replace(testconfig_instr, open_timeout=-1)

    with pytest.raises(ValueError):
        dataclasses.replace(testconfig_instr, write_termination='bla')

    with pytest.raises(ValueError):
        dataclasses.replace(testconfig_instr, read_termination='\n\r')


def test_visa_open_close(testconfig_instr):
    vcom_default_backend = VisaCommunication(testconfig_instr)

    # AttributeError should be caught
    vcom_default_backend.close()

    # open should raise a communication error, here from visa.VisaIOError
    with pytest.raises(VisaCommunicationError):
        vcom_default_backend.open()

    # test with pyvisa-py as backend (this will run on GitLab runners, as NI-VISA is
    # not installed there
    pyvisa_py_config = dataclasses.replace(testconfig_instr, visa_backend='@py')
    vcom_pyvisa_py_backend = VisaCommunication(pyvisa_py_config)

    with pytest.raises(VisaCommunicationError):
        vcom_pyvisa_py_backend.open()


def test_generate_cmd_string():
    assert VisaCommunication._generate_cmd_string(('cmd1', 'cmd2')) == \
        'cmd1' + VisaCommunication.MULTI_COMMANDS_SEPARATOR + 'cmd2'

    with pytest.raises(VisaCommunicationError):
        VisaCommunication._generate_cmd_string(
            tuple(
                [f'cmd{i}'
                 for i in range(0, VisaCommunication.MULTI_COMMANDS_MAX + 1)]
            )
        )


def test_read_write(testconfig_socket):
    com_socket = VisaCommunication(testconfig_socket)

    with pytest.raises(VisaCommunicationError):
        com_socket.write('bla')

    with pytest.raises(VisaCommunicationError):
        com_socket.query('bla')


def test_spoll(testconfig_socket, testconfig_instr):
    com_socket = VisaCommunication(testconfig_socket)
    com_instr = VisaCommunication(testconfig_instr)

    with pytest.raises(VisaCommunicationError):
        com_socket.spoll()

    with pytest.raises(VisaCommunicationError):
        com_instr.spoll()
