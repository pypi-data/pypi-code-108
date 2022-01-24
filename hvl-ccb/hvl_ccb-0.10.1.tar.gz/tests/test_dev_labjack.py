#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the dev.labjack module.
"""

import pytest

from hvl_ccb.dev import LabJack, LabJackError, LabJackIdentifierDIOError
from masked_comm import MaskedLJMCommunication


@pytest.fixture(scope="module")
def com_config():
    return {
        "device_type": "ANY",
        "connection_type": "ANY",
        "identifier": "-2"  # identifier = -2 specifies LJM DEMO mode, see
        # https://labjack.com/support/software/api/ljm/demo-mode
    }


@pytest.fixture
def started_dev_comm(com_config):
    com = MaskedLJMCommunication(com_config)
    with LabJack(com) as lj:
        yield lj, com


def _force_dt(lj, com, dt):
    com.config.force_value("device_type", dt)
    com.put_name("PRODUCT_ID", dt.p_id)
    lj.get_product_type(force_query_id=True)


@pytest.fixture
def started_dev_comm_with_t7pro(started_dev_comm):
    lj, com = started_dev_comm
    # force T7-Pro device for following tests
    _force_dt(lj, com, com.config.DeviceType.T7_PRO)
    lj.get_product_type()
    yield lj, com


@pytest.fixture
def started_dev_comm_with_t4(started_dev_comm):
    lj, com = started_dev_comm
    # force T4 device for following tests
    _force_dt(lj, com, com.config.DeviceType.T4)
    lj.get_product_type()
    yield lj, com


def test_instantiation(com_config):
    lj = LabJack(com_config)
    assert lj is not None


def test_get_serial_number(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("SERIAL_NUMBER", 1234)
    assert lj.get_serial_number() == 1234
    with pytest.raises(TypeError):
        com.put_name("SERIAL_NUMBER", 1234.5)
        lj.get_serial_number()


def test_get_sbus_temp(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("SBUS0_TEMP", 298.15)
    assert lj.get_sbus_temp(0) == 298.15
    com.put_name("SBUS0_TEMP", "Not a float")
    with pytest.raises(TypeError):
        lj.get_sbus_temp(0)


def test_get_sbus_rh(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("SBUS0_RH", 40.5)
    assert lj.get_sbus_rh(0) == 40.5
    com.put_name("SBUS0_RH", "Not a float")
    with pytest.raises(TypeError):
        lj.get_sbus_rh(0)


def test_get_ain(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("AIN0", 1.23)
    assert lj.get_ain(0) == 1.23
    # multiple reads at once
    channels = ("AIN0", "AIN1")
    outputs = (5.00, 0.16)
    for channel, output in zip(channels, outputs):
        com.put_name(channel, output)
    assert lj.get_ain(0, 1) == outputs


def test_set_ain_range(started_dev_comm):
    lj, com = started_dev_comm

    lj.set_ain_range(0, lj.AInRange.TEN)
    assert com.get_written() == ("AIN0_RANGE", 10)

    lj.set_ain_range(0, lj.AInRange.ONE_TENTH)
    assert com.get_written() == ("AIN0_RANGE", 0.1)

    with pytest.raises(ValueError):
        lj.set_ain_range(0, 0.2)
    assert com.get_written() is None


def test_set_ain_resolution(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro

    ain_max_res = com.config.device_type.ain_max_resolution
    with pytest.raises(LabJackError):
        lj.set_ain_resolution(0, ain_max_res + 1)
    assert com.get_written() is None

    for res in range(ain_max_res + 1):
        lj.set_ain_resolution(0, res)
        assert com.get_written() == ("AIN0_RESOLUTION_INDEX", res)

    with pytest.raises(LabJackError):
        lj.set_ain_resolution(0, -1)
    assert com.get_written() is None

    with pytest.raises(LabJackError):
        lj.set_ain_resolution(0, com.config.device_type.ain_max_resolution + 1)
    assert com.get_written() is None


def test_set_ain_differential(started_dev_comm):
    lj, com = started_dev_comm

    lj.set_ain_differential(4, True)
    assert com.get_written() == ("AIN4_NEGATIVE_CH", 5)

    lj.set_ain_differential(4, False)
    assert com.get_written() == ("AIN4_NEGATIVE_CH", 199)

    with pytest.raises(LabJackError):
        lj.set_ain_differential(5, True)
    assert com.get_written() is None

    with pytest.raises(LabJackError):
        lj.set_ain_differential(14, True)
    assert com.get_written() is None


def test_set_ain_thermocouple(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro

    lj.set_ain_thermocouple(0, None)
    lj.set_ain_thermocouple(0, lj.ThermocoupleType.NONE)
    lj.set_ain_thermocouple(0, "K")
    lj.set_ain_thermocouple(0, lj.ThermocoupleType.K)
    with pytest.raises(ValueError):
        lj.set_ain_thermocouple(0, "B")

    lj.set_ain_thermocouple(0, thermocouple="T", unit="F")
    lj.set_ain_thermocouple(0, thermocouple="T", unit=lj.TemperatureUnit.F)
    with pytest.raises(ValueError):
        lj.set_ain_thermocouple(0, "K", unit="B")

    lj.set_ain_thermocouple(0, thermocouple="T", cjc_type="lm34")
    lj.set_ain_thermocouple(0, thermocouple="T", cjc_type=lj.CjcType.lm34)
    with pytest.raises(ValueError):
        lj.set_ain_thermocouple(0, "K", cjc_type="LM35")


def test_read_thermocouple(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("AIN0_EF_READ_A", 244.3)
    assert lj.read_thermocouple(0) == 244.30
    com.put_name("AIN0_EF_READ_A", "Not a float")
    with pytest.raises(TypeError):
        lj.read_thermocouple(0)


def test_read_resistance(started_dev_comm):
    lj, com = started_dev_comm
    com.put_name("AIN0_EF_READ_A", 20.00)
    assert lj.read_resistance(0) == 20.00
    com.put_name("AIN0_EF_READ_A", "Not a float")
    with pytest.raises(TypeError):
        lj.read_resistance(0)


def test_set_ain_resistance(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.set_ain_resistance(channel=2, vrange=lj.AInRange.ONE, resolution=8)


def test_get_product_id(started_dev_comm):
    lj, com = started_dev_comm
    p_id = com.config.device_type.p_id
    com.put_name("PRODUCT_ID", p_id)
    assert lj.get_product_id() is int(p_id)
    for wrong_p_id in ("Not an ID", 4.7):
        com.put_name("PRODUCT_ID", wrong_p_id)
        with pytest.raises(TypeError):
            lj.get_product_id()


def test_get_product_type(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    assert lj.get_product_type() is com.config.device_type
    # config device matches none of T7 devices from ID
    com.config.force_value("device_type", com.config.DeviceType.T4)
    com.put_name("PRODUCT_ID", com.config.DeviceType.T7_PRO.p_id)
    with pytest.raises(LabJackIdentifierDIOError):
        lj.get_product_type(force_query_id=True)
    # force no device type configured for the following tests => return T7 as a first
    # to match the unambiguous product ID for T7 devices
    com.config.force_value("device_type", None)
    com.put_name("PRODUCT_ID", com.config.DeviceType.T7_PRO.p_id)
    assert lj.get_product_type(force_query_id=True) is com.config.DeviceType.T7
    # force specific device type for following tests
    for dt in (
        com.config.DeviceType.T7_PRO,
        com.config.DeviceType.T7,
        com.config.DeviceType.T4,
    ):
        _force_dt(lj, com, dt)
        assert lj.get_product_type() is dt


def test_get_product_name(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    assert lj.get_product_name() == lj.com.config.device_type


def test_get_cal_current_source(started_dev_comm):
    lj, com = started_dev_comm
    for ten_name in ("10uA", lj.CalMicroAmpere.TEN):
        com.put_name(lj.CalMicroAmpere.TEN.current_source_query, 10.001)
        assert lj.get_cal_current_source(ten_name) == 10.001
    com.put_name(lj.CalMicroAmpere.TEN.current_source_query, "Not a float")
    with pytest.raises(TypeError):
        lj.get_cal_current_source(lj.CalMicroAmpere.TEN)
    for two_hundred_name in ("200uA", lj.CalMicroAmpere.TWO_HUNDRED):
        com.put_name(lj.CalMicroAmpere.TWO_HUNDRED.current_source_query, 200.001)
        assert lj.get_cal_current_source(two_hundred_name) == 200.001


def test_get_digital_input(started_dev_comm_with_t4):
    lj, com = started_dev_comm_with_t4

    com.put_name("EIO0", lj.DIOStatus.LOW)
    assert lj.get_digital_input("EIO0") == lj.DIOStatus.LOW
    com.put_name("EIO0", lj.DIOStatus.HIGH)
    assert lj.get_digital_input("EIO0") == lj.DIOStatus.HIGH
    com.put_name("EIO0", 2.0)
    with pytest.raises(LabJackIdentifierDIOError):
        lj.get_digital_input("EIO0")

    with pytest.raises(TypeError):
        com.put_name("EIO0", 2.5)
        lj.get_digital_input("EIO0")

    with pytest.raises(ValueError):
        lj.get_digital_input("Not a DIO Channel address")

    dio = lj.DIOChannel.MIO0  # only avail on T7
    com.put_name(dio.name, 0)
    with pytest.raises(LabJackIdentifierDIOError):
        lj.get_digital_input(dio)


def test_set_digital_output(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro

    lj.set_digital_output("FIO0", lj.DIOStatus.HIGH)
    assert com.get_written() == ("FIO0", lj.DIOStatus.HIGH)

    with pytest.raises(LabJackIdentifierDIOError):
        lj.set_digital_output("AIO0", 1)


def test_get_clock(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.get_clock()


def test_set_clock(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.set_clock()
    lj.set_clock(80_000_000)
    lj.set_clock(clock_frequency=5_000_000, clock_period=0)
    with pytest.raises(ValueError):
        lj.set_clock(10_000)
    with pytest.raises(ValueError):
        lj.set_clock(clock_frequency=80_000_000, clock_period=1_000_000)


def test_config_high_pulse(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.config_high_pulse(address="FIO0", t_start=0, t_width=1)
    with pytest.raises(LabJackError):
        lj.config_high_pulse(address="FIO6", t_start=0, t_width=1)
    lj.config_high_pulse(address="FIO0", t_start=999.999, t_width=.001, n_pulses=1000)
    with pytest.raises(TypeError):
        lj.config_high_pulse(address="FIO0", t_start=.21, t_width=.22, n_pulses=.23)
    with pytest.raises(ValueError):
        lj.config_high_pulse(address="FIO0", t_start=.2, t_width=-1)


def test_send_pulses(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.configured_pulse_addresses = ["FIO0", "FIO2"]
    lj.send_pulses("FIO0", "FIO2")
    with pytest.raises(LabJackError):
        lj.send_pulses("FIO0", "FIO3")


def test_disable_pulses(started_dev_comm_with_t7pro):
    lj, com = started_dev_comm_with_t7pro
    lj.disable_pulses()
    lj.configured_pulse_addresses = ["FIO0", "FIO2", "FIO4", "FIO5"]
    lj.disable_pulses("FIO3", "FIO5")
    lj.disable_pulses()
    assert lj.configured_pulse_addresses == []


def test_set_analog_output(started_dev_comm):
    lj, com = started_dev_comm

    lj.set_analog_output(1, 2.5)
    assert com.get_written() == ("DAC1", 2.5)
    lj.set_analog_output(0, 2)
    assert com.get_written() == ("DAC0", 2)
