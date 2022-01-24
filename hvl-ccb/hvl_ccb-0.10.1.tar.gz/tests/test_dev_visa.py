#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for VisaDevice
"""
from time import sleep

import pytest

from hvl_ccb.comm import (
    CommunicationProtocol,
    VisaCommunicationConfig
)
from hvl_ccb.dev import VisaDevice
from masked_comm import MaskedVisaCommunication


@pytest.fixture(scope='module')
def com_config():
    return VisaCommunicationConfig(
        interface_type=VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET,
        board=0,
        host='192.168.1.31',
        port=5025
    )


@pytest.fixture(scope='module')
def dev_config():
    return {
        'spoll_interval': 0.01,
        'spoll_start_delay': 0.01,
    }


class WrongCommunicationProtocol(CommunicationProtocol):
    @staticmethod
    def config_cls():
        return VisaCommunicationConfig

    def open(self):
        pass

    def close(self):
        pass


def test_instantiation(com_config, dev_config):
    dev = VisaDevice(com_config, dev_config)

    assert com_config.address == "TCPIP0::192.168.1.31::5025::SOCKET"
    assert dev is not None

    dev_config_dict = dev_config

    assert dev.config.spoll_interval == dev_config_dict['spoll_interval']

    invalid_dev_config = dict(dev_config_dict)
    invalid_dev_config['spoll_interval'] = 0
    with pytest.raises(ValueError):
        VisaDevice(com_config, invalid_dev_config)

    assert dev.config.spoll_start_delay == dev_config_dict['spoll_start_delay']

    invalid_dev_config = dict(dev_config_dict)
    invalid_dev_config['spoll_start_delay'] = -1
    with pytest.raises(ValueError):
        VisaDevice(com_config, invalid_dev_config)


def test_basics(com_config, dev_config):
    com = MaskedVisaCommunication(com_config)
    dev = VisaDevice(com, dev_config)

    com.put_name('*IDN?', 'test_identification')
    assert dev.get_identification() == 'test_identification'

    com.put_name('SYSTem:ERRor:ALL?', '0,"No error"')
    assert dev.get_error_queue() == '0,"No error"'

    dev.reset()
    assert com.get_written() == '*RST'
    assert com.get_written() == '*CLS'

    dev.start()

    for i in range(8):
        com.stb = 2**i - 1
        sleep(0.1)

    dev.stop()

    assert com == dev.com
