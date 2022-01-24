#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the .dev.heinzinger_pnc sub-package.
"""

import logging

import pytest

from hvl_ccb import comm, dev
from masked_comm.serial import HeinzingerLoopSerialCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": dev.HeinzingerSerialCommunicationConfig.Parity.NONE,
        "stopbits": dev.HeinzingerSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": dev.HeinzingerSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "default_number_of_recordings": 16,
        "number_of_decimals": 6,
        "wait_sec_stop_commands": 0.01,
    }


class ConcreteHeinzingerDI(dev.HeinzingerDI):
    def start(self):
        super().start()


@pytest.fixture
def started_heinzinger_di(com_config, dev_config):
    serial_port = HeinzingerLoopSerialCommunication(com_config)
    serial_port.open()
    serial_port.put_text("my_interface_version")
    with ConcreteHeinzingerDI(serial_port, dev_config) as di:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, di


@pytest.fixture
def start_pnc_device(com_config, dev_config):
    def _start_pnc_device(serial_number):
        serial_port = HeinzingerLoopSerialCommunication(com_config)
        serial_port.open()
        serial_port.put_text("my_interface_version")
        serial_port.put_text(serial_number)

        def started_pnc():
            with dev.HeinzingerPNC(serial_port, dev_config) as pnc:
                while serial_port.get_written() is not None:
                    pass
                yield serial_port, pnc

        return started_pnc()

    return _start_pnc_device


def test_di_number_of_recordings(started_heinzinger_di):
    com, di = started_heinzinger_di

    # set a new value
    di.set_number_of_recordings(4)
    assert com.get_written() == "AVER 4"

    com.put_text("4")
    assert di.get_number_of_recordings() == 4

    # assigning integer not amongst accepted values
    with pytest.raises(ValueError):
        di.set_number_of_recordings(3)


def test_com_config(com_config):
    config = dev.HeinzingerSerialCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


def test_dev_config(dev_config):
    # currently there are no non-default config values
    dev.HeinzingerConfig()

    config = dev.HeinzingerConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"default_number_of_recordings": 0},
        {"number_of_decimals": 0},
        {"number_of_decimals": 11},
        {"wait_sec_stop_commands": 0},
        {"number_of_decimals": 6, "wait_sec_stop_commands": -1},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        dev.HeinzingerConfig(**invalid_config)


def test_di_instantiation(com_config, dev_config):
    di = ConcreteHeinzingerDI(com_config)
    assert di is not None

    di = ConcreteHeinzingerDI(com_config, dev_config)
    assert di is not None


def test_di_start(started_heinzinger_di):
    com, di = started_heinzinger_di
    # starting again should work
    com.put_text("my_interface_version")
    di.start()
    assert com.get_written() == "VERS?"


def test_di_stop(started_heinzinger_di):
    com, di = started_heinzinger_di
    # starting again should work
    di.stop()
    assert com.get_written() == "VOLT 0.000000"
    assert com.get_written() == "OUTP OFF"

    # check that a second stop() works
    di.stop()
    assert not com.get_written()


def test_di_output_status(started_heinzinger_di):
    com, di = started_heinzinger_di
    assert di.output_status == di.OutputStatus.UNKNOWN
    di.output_on()
    assert di.output_status == di.OutputStatus.ON
    di.output_off()
    assert di.output_status == di.OutputStatus.OFF


def test_di_output_on(started_heinzinger_di):
    com, di = started_heinzinger_di
    di.output_on()
    assert com.get_written() == "OUTP ON"
    assert di.output_status == di.OutputStatus.ON


def test_di_output_off(started_heinzinger_di):
    com, di = started_heinzinger_di
    di.output_off()
    assert com.get_written() == "OUTP OFF"
    assert di.output_status == di.OutputStatus.OFF


def test_di_set_voltage(started_heinzinger_di):
    com, di = started_heinzinger_di

    # test if the correct text is sent to the com
    di.set_voltage(0.123456789)
    assert com.get_written().strip() == "VOLT 0.123457"


def test_di_measure_voltage(started_heinzinger_di):
    com, di = started_heinzinger_di
    volt = 1.2
    com.put_text(str(volt))
    result = di.measure_voltage()
    assert result == volt and com.get_written() == "MEAS:VOLT?"


def test_di_set_current(started_heinzinger_di):
    com, di = started_heinzinger_di

    # test if the correct text is sent to the com
    di.set_current(0.123456789)
    assert com.get_written().strip() == "CURR 0.123457"


def test_di_measure_current(started_heinzinger_di):
    com, di = started_heinzinger_di
    curr = 0.25
    com.put_text(str(curr))
    result = di.measure_current()
    assert result == curr and com.get_written() == "MEAS:CURR?"


def test_di_com_error(com_config, dev_config):

    wrong_config = dict(com_config)
    wrong_config["port"] = "NOT A PORT"
    di = ConcreteHeinzingerDI(wrong_config, dev_config)
    assert not di.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        di.start()

    di = ConcreteHeinzingerDI(com_config, dev_config)
    assert not di.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        di.reset_interface()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.get_interface_version()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.get_serial_number()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.output_on()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.output_off()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.get_number_of_recordings()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.set_number_of_recordings(dev.HeinzingerConfig.RecordingsEnum.EIGHT)
    with pytest.raises(comm.SerialCommunicationIOError):
        di.measure_voltage()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.set_voltage(1)
    with pytest.raises(comm.SerialCommunicationIOError):
        di.get_voltage()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.measure_current()
    with pytest.raises(comm.SerialCommunicationIOError):
        di.set_current(1)
    with pytest.raises(comm.SerialCommunicationIOError):
        di.get_current()


def test_pnc_instantiation(com_config, dev_config):
    pnc = dev.HeinzingerPNC(com_config)
    assert pnc is not None

    wrong_config = dict(dev_config)
    wrong_config["default_number_of_recordings"] = 0
    with pytest.raises(ValueError):
        dev.HeinzingerPNC(com_config, wrong_config)

    assert pnc.unit_voltage == dev.HeinzingerPNC.UnitVoltage.UNKNOWN
    assert pnc.unit_current == dev.HeinzingerPNC.UnitCurrent.UNKNOWN


def test_pnc_com_error(com_config, dev_config):
    pnc = dev.HeinzingerPNC(com_config)
    assert not pnc.com.is_open

    with pytest.raises(comm.SerialCommunicationIOError):
        pnc.identify_device()
    with pytest.raises(comm.SerialCommunicationIOError):
        pnc.set_voltage(0)
    with pytest.raises(comm.SerialCommunicationIOError):
        pnc.set_current(0)


# test different possible serial numbers to check if the info is read correctly
devices_data = [
    ("PNChp 60000-1neg 354211082", 60000, 1, dev.HeinzingerPNC.UnitVoltage.V, "mA"),
    ("314807440/PNChp 60000-1neg.", 60000, 1, "V", dev.HeinzingerPNC.UnitCurrent.mA),
    ("PNChp 1500-40 ump. 375214277", 1500, 40, "V", "mA"),
    ("PNC 100000-6pos 375214277", 100, 6, dev.HeinzingerPNC.UnitVoltage.kV, "mA"),
    ("PNC 600-3000pos 375214277", 600, 3, "V", dev.HeinzingerPNC.UnitCurrent.A),
]


@pytest.mark.parametrize("device_data", devices_data)
def test_pnc_start(start_pnc_device, com_config, device_data):
    started_pnc = start_pnc_device(device_data[0])
    com, pnc = next(started_pnc)

    # starting the device again should work
    com.put_text("my_interface_version")
    com.put_text(device_data[0])
    pnc.start()
    assert com.get_written() == "VERS?"
    assert com.get_written() == "*IDN?"
    assert pnc.max_voltage_hardware == pnc.max_voltage == device_data[1]
    assert pnc.max_current_hardware == pnc.max_current == device_data[2]
    assert pnc.unit_voltage == device_data[3]
    assert pnc.unit_current == device_data[4]
    assert com.get_written() == "AVER " + str(
        pnc.config.default_number_of_recordings.value
    )


def test_pnc_not_recognized(start_pnc_device):
    with pytest.raises(dev.HeinzingerPNCDeviceNotRecognizedException):
        next(start_pnc_device("ABC 600-3000pos 375214277"))


def test_pnc_set_max_voltage(start_pnc_device):
    started_pnc = start_pnc_device("PNC 600-3000pos 375214277")
    com, pnc = next(started_pnc)

    # set max_voltage to half the current value
    next_value = pnc.max_voltage / 2
    pnc.max_voltage = next_value
    assert pnc.max_voltage == next_value

    # assigning value higher than hardware maximum
    with pytest.raises(ValueError):
        pnc.max_voltage = pnc.max_voltage_hardware * 2

    # assigning negative value
    with pytest.raises(ValueError):
        pnc.max_voltage = -1


def test_pnc_set_max_current(start_pnc_device):
    started_pnc = start_pnc_device("PNC 600-3000pos 375214277")
    com, pnc = next(started_pnc)

    # set max_voltage to half the current value
    next_value = pnc.max_current / 2
    pnc.max_current = next_value
    assert pnc.max_current == next_value

    # assigning value higher than hardware maximum
    with pytest.raises(ValueError):
        pnc.max_current = pnc.max_current_hardware * 2

    # assigning negative value
    with pytest.raises(ValueError):
        pnc.max_current = -1


# test different values for voltage and current
devices_u = [
    ("PNC 600-3000pos 375214277", 600, "VOLT 600.000000", 700),
    ("PNChp 1500-40 ump. 375214277", 1, "VOLT 1.000000", 1600),
    ("PNChp 60000-1neg 354211082", 50000, "VOLT 50000.000000", 60000.1),
    ("PNC 100000-6pos 375214277", 100, "VOLT 100.000000", 101),
]


@pytest.mark.parametrize("device_data", devices_u)
def test_pnc_set_voltage(start_pnc_device, device_data):
    started_pnc = start_pnc_device(device_data[0])
    com, pnc = next(started_pnc)

    # test if the correct text is sent to the com
    pnc.set_voltage(device_data[1])
    assert com.get_written().strip() == device_data[2]

    # test if an error is raised when trying to set a too high voltage
    with pytest.raises(dev.HeinzingerPNCMaxVoltageExceededException):
        pnc.set_voltage(device_data[3])


# test different values for voltage and current
devices_i = [
    ("PNC 600-3000pos 375214277", 2.999999, "CURR 2.999999", 1000),
    ("PNChp 1500-40 ump. 375214277", 39, "CURR 39.000000", 41),
    ("PNChp 60000-1neg 354211082", 1, "CURR 1.000000", 2),
    ("PNC 100000-6pos 375214277", 0, "CURR 0.000000", 6.1),
]


@pytest.mark.parametrize("device_data", devices_i)
def test_pnc_set_current(start_pnc_device, device_data):
    started_pnc = start_pnc_device(device_data[0])
    com, pnc = next(started_pnc)

    # test if the correct text is sent to the com
    pnc.set_current(device_data[1])
    assert com.get_written().strip() == device_data[2]

    # test if an error is raised when trying to set a too high current
    with pytest.raises(dev.HeinzingerPNCMaxCurrentExceededException):
        pnc.set_current(device_data[3])
