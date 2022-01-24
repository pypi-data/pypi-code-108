#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the Elektro Automatik PSI 9000 power supply device classes.
"""

import pytest

from hvl_ccb.dev import (
    PSI9000,
    PSI9000Error,
    PSI9000VisaCommunicationConfig,
    PSI9000Config,
)
from masked_comm import MaskedVisaCommunication


@pytest.fixture(scope="module")
def com_config():
    return {
        "interface_type": PSI9000VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET,
        "host": "127.0.0.1",
        "open_timeout": 10,
        "timeout": 50,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "spoll_interval": 0.01,
        "spoll_start_delay": 0,
        "wait_sec_system_lock": 0.01,
        "wait_sec_settings_effect": 0.01,
        "wait_sec_initialisation": 0.01,
    }


@pytest.fixture
def testdev(com_config, dev_config):
    com = MaskedVisaCommunication(com_config)
    dev = PSI9000(com, dev_config)
    return dev


def test_dev_config(dev_config):
    # currently there are no non-default config values
    PSI9000Config()

    config = PSI9000Config(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"power_limit": -1.0},
        {"voltage_lower_limit": 20, "voltage_upper_limit": 19.0},
        {
            "voltage_lower_limit": 4,
            "voltage_upper_limit": PSI9000Config._VOLTAGE_UPPER_LIMIT + 1,
        },
        {"current_lower_limit": -1.0},
        {
            "current_lower_limit": 4,
            "current_upper_limit": PSI9000Config._CURRENT_UPPER_LIMIT + 1,
        },
        {"wait_sec_system_lock": 0},
        {"wait_sec_system_lock": -1},
        {"wait_sec_settings_effect": 0},
        {"wait_sec_initialisation": 0},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        PSI9000Config(**invalid_config)


def test_instantiation(com_config):
    power_supply = PSI9000(com_config)
    assert power_supply is not None


def test_start_stop(testdev: PSI9000):
    power_supply = testdev
    test_com = power_supply.com

    power_supply.start()

    # stop successful
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    test_com.put_name("OUTput?", "OFF")
    power_supply.stop()

    # stop successful: output and lock on
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    test_com.put_name("OUTPut?", "ON")
    test_com.put_name("SOURce:VOLTage?", "0 V")
    test_com.put_name("SOURce:CURRent?", "0 A")
    test_com.put_name("OUTPut?", "OFF")
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    power_supply.stop()


def test_locking(testdev: PSI9000):
    power_supply = testdev
    test_com = power_supply.com

    # lock failed
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    with pytest.raises(PSI9000Error):
        power_supply.set_system_lock(True)
    assert test_com.get_written() == "SYSTem:LOCK ON"

    # lock successful
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    power_supply.set_system_lock(True)
    assert test_com.get_written() == "SYSTem:LOCK ON"

    # unlock failed due to still on current
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    test_com.put_name("MEASure:VOLTage?", "20 V")
    test_com.put_name("MEASure:CURRent?", "100 A")
    with pytest.raises(PSI9000Error):
        power_supply.set_system_lock(False)
    assert test_com.get_written() is None

    # unlock failed
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    test_com.put_name("MEASure:VOLTage?", "0 V")
    test_com.put_name("MEASure:CURRent?", "0 A")
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    with pytest.raises(PSI9000Error):
        power_supply.set_system_lock(False)
    assert test_com.get_written() == "SYSTem:LOCK OFF"

    # unlock successful
    test_com.put_name("SYSTem:LOCK:OWNer?", "REMOTE")
    test_com.put_name("MEASure:VOLTage?", "0 V")
    test_com.put_name("MEASure:CURRent?", "0 A")
    test_com.put_name("SYSTem:LOCK:OWNer?", "NONE")
    power_supply.set_system_lock(False)
    assert test_com.get_written() == "SYSTem:LOCK OFF"

    # illegal answer
    test_com.put_name("SYSTem:LOCK:OWNer?", "bla")
    with pytest.raises(PSI9000Error):
        power_supply.get_system_lock()


def test_output(testdev: PSI9000):
    power_supply = testdev
    test_com = power_supply.com

    test_com.put_name("OUTPut?", "ON")
    assert power_supply.get_output()

    test_com.put_name("OUTPut?", "OFF")
    assert not power_supply.get_output()

    test_com.put_name("OUTPut?", "bla")
    with pytest.raises(PSI9000Error):
        power_supply.get_output()

    # setting output
    test_com.put_name("OUTPut?", "ON")
    power_supply.set_output(True)
    assert test_com.get_written() == "OUTPut ON"

    test_com.put_name("OUTPut?", "OFF")
    power_supply.set_output(False)
    assert test_com.get_written() == "OUTPut OFF"

    test_com.put_name("OUTPut?", "ON")
    with pytest.raises(PSI9000Error):
        power_supply.set_output(False)
    assert test_com.get_written() == "OUTPut OFF"

    test_com.put_name("OUTPut?", "OFF")
    with pytest.raises(PSI9000Error):
        power_supply.set_output(True)
    assert test_com.get_written() == "OUTPut ON"


def test_get_uip_upper_limits(testdev: PSI9000):
    test_com = testdev.com

    # get upper limits
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "80 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "1000 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    assert testdev.get_uip_upper_limits() == (80, 1000, 10000)


def test_get_ui_lower_limits(testdev: PSI9000):
    test_com = testdev.com

    # get lower limits
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "2 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5 A")
    assert testdev.get_ui_lower_limits() == (2, 5)


def test_set_upper_limits(testdev: PSI9000):
    test_com = testdev.com

    # set upper limits, success
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "2 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5 A")
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "10 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "20 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    testdev.set_upper_limits(10, 20, 10000)
    assert test_com.get_written() == "SOURce:VOLTage:LIMit:HIGH 10"
    assert test_com.get_written() == "SOURce:CURRent:LIMit:HIGH 20"
    assert test_com.get_written() == "SOURce:POWer:LIMit:HIGH 10000"

    # set upper limits, set fail
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "2 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5 A")
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "10 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "200 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    with pytest.raises(PSI9000Error):
        testdev.set_upper_limits(10, 20, 10000)
    assert test_com.get_written() == "SOURce:VOLTage:LIMit:HIGH 10"
    assert test_com.get_written() == "SOURce:CURRent:LIMit:HIGH 20"
    assert test_com.get_written() == "SOURce:POWer:LIMit:HIGH 10000"

    # set upper limits, limit fail
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "20 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5 A")
    with pytest.raises(ValueError):
        testdev.set_upper_limits(10, 20, 10000)
    assert test_com.get_written() is None


def test_set_lower_limits(testdev: PSI9000):
    test_com = testdev.com

    # set lower limits, success
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "80 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "2000 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "2 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5.2 A")
    testdev.set_lower_limits(2, 5.2)
    assert test_com.get_written() == "SOURce:VOLTage:LIMit:LOW 2"
    assert test_com.get_written() == "SOURce:CURRent:LIMit:LOW 5.2"

    # set lower limits, set fail
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "80 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "2000 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "2 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "50 A")
    with pytest.raises(PSI9000Error):
        testdev.set_lower_limits(2, 5)
    assert test_com.get_written() == "SOURce:VOLTage:LIMit:LOW 2"
    assert test_com.get_written() == "SOURce:CURRent:LIMit:LOW 5"

    # set lower limits, limit fail
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "1 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "20 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    with pytest.raises(ValueError):
        testdev.set_lower_limits(0.5, 500)
    assert test_com.get_written() is None


def test_set_voltage_current(testdev: PSI9000):
    power_supply = testdev
    test_com = power_supply.com

    test_com.put_name("SOURce:VOLTage?", "20.2 V")
    test_com.put_name("SOURce:CURRent?", "123.4 A")
    power_supply.set_voltage_current(20.2, 123.4)
    assert test_com.get_written() == "SOURce:VOLTage 20.200000"
    assert test_com.get_written() == "SOURce:CURRent 123.400000"

    test_com.put_name("SOURce:VOLTage?", "20.2 V")
    test_com.put_name("SOURce:CURRent?", "10 A")
    test_com.put_name("SOURce:VOLTage:LIMit:HIGH?", "20 V")
    test_com.put_name("SOURce:CURRent:LIMit:HIGH?", "2000 A")
    test_com.put_name("SOURce:POWer:LIMit:HIGH?", "10000 W")
    test_com.put_name("SOURce:VOLTage:LIMit:LOW?", "1 V")
    test_com.put_name("SOURce:CURRent:LIMit:LOW?", "5 A")
    with pytest.raises(PSI9000Error):
        power_supply.set_voltage_current(20.2, 123.4)
    assert test_com.get_written() == "SOURce:VOLTage 20.200000"
    assert test_com.get_written() == "SOURce:CURRent 123.400000"


def test_check_master_slave_config(testdev: PSI9000):
    power_supply = testdev
    test_com = power_supply.com

    # MS disabled
    test_com.put_name("SYSTem:MS:ENABle?", "OFF")
    with pytest.raises(PSI9000Error):
        power_supply.check_master_slave_config()
    assert test_com.get_written() is None

    # device is not MASTER
    test_com.put_name("SYSTem:MS:ENABle?", "ON")
    test_com.put_name("SYSTem:MS:LINK?", "SLAVE")
    with pytest.raises(PSI9000Error):
        power_supply.check_master_slave_config()
    assert test_com.get_written() is None

    # initialization failed
    test_com.put_name("SYSTem:MS:ENABle?", "ON")
    test_com.put_name("SYSTem:MS:LINK?", "MASTER")
    test_com.put_name("SYSTem:MS:CONDition?", "NOT_INIT")
    with pytest.raises(PSI9000Error):
        power_supply.check_master_slave_config()
    assert test_com.get_written() == "SYSTem:MS:INITialisation"

    # wrong expected voltage, current nominal values
    test_com.put_name("SYSTem:MS:ENABle?", "ON")
    test_com.put_name("SYSTem:MS:LINK?", "MASTER")
    test_com.put_name("SYSTem:MS:CONDition?", "INIT")
    test_com.put_name("SYSTem:MS:NOMinal:VOLTage?", f"{PSI9000.MS_NOMINAL_VOLTAGE} V")
    test_com.put_name(
        "SYSTem:MS:NOMinal:CURRent?", f"{PSI9000.MS_NOMINAL_CURRENT - 1} A"
    )
    with pytest.raises(PSI9000Error):
        power_supply.check_master_slave_config()
    assert test_com.get_written() == "SYSTem:MS:INITialisation"

    # all right
    # wrong expected voltage, current nominal values
    test_com.put_name("SYSTem:MS:ENABle?", "ON")
    test_com.put_name("SYSTem:MS:LINK?", "MASTER")
    test_com.put_name("SYSTem:MS:CONDition?", "INIT")
    test_com.put_name("SYSTem:MS:NOMinal:VOLTage?", f"{PSI9000.MS_NOMINAL_VOLTAGE} V")
    test_com.put_name("SYSTem:MS:NOMinal:CURRent?", f"{PSI9000.MS_NOMINAL_CURRENT} A")
    power_supply.check_master_slave_config()
    assert test_com.get_written() == "SYSTem:MS:INITialisation"
