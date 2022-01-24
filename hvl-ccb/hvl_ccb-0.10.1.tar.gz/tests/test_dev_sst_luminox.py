#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the SST Luminox Oxygen sensor device class.
"""

import pytest

from hvl_ccb.comm import SerialCommunicationIOError
from hvl_ccb.dev import (
    Luminox,
    LuminoxConfig,
    LuminoxMeasurementType,
    LuminoxMeasurementTypeError,
    LuminoxOutputMode,
    LuminoxOutputModeError,
)
from masked_comm.serial import LuminoxLoopSerialCommunication


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "timeout": 0.05,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "wait_sec_post_activate": 0.01,
        "wait_sec_trials_activate": 0.01,
        "nr_trials_activate": 1,
    }


@pytest.fixture
def testdev(com_config, dev_config):
    serial_port = LuminoxLoopSerialCommunication(com_config)
    with Luminox(serial_port, dev_config) as lumi:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, lumi


@pytest.mark.parametrize(
    "config_key,wrong_value",
    [
        ("wait_sec_post_activate", 0),
        ("wait_sec_post_activate", -1),
        ("wait_sec_trials_activate", 0),
        ("wait_sec_trials_activate", -1),
        ("nr_trials_activate", 0),
    ],
)
def test_invalid_config_value(dev_config, config_key, wrong_value):
    invalid_config = dict(dev_config)
    invalid_config[config_key] = wrong_value
    with pytest.raises(ValueError):
        LuminoxConfig(**invalid_config)


def test_instantiation(com_config, dev_config):
    mbw = Luminox(com_config, dev_config)
    assert mbw is not None


def test_com_error(com_config, dev_config):
    wrong_config = dict(com_config)
    wrong_config["port"] = "NOT A PORT"
    lumi = Luminox(wrong_config, dev_config)
    assert not lumi.com.is_open

    with pytest.raises(SerialCommunicationIOError):
        lumi.start()

    lumi = Luminox(com_config, dev_config)
    assert not lumi.com.is_open


def test_activate_output(testdev):
    com, lumi = testdev
    com.put_text(f"M 00{com.config.terminator_str()}")
    lumi.activate_output(LuminoxOutputMode.streaming)
    assert lumi.output == LuminoxOutputMode.streaming

    with pytest.raises(LuminoxOutputModeError):
        lumi.activate_output(LuminoxOutputMode.polling)


def test_start(testdev):
    com, lumi = testdev

    # starting again should work
    lumi.start()


def test_read_stream(testdev):
    com, lumi = testdev
    expected_measurement_values = {
        LuminoxMeasurementType.partial_pressure_o2: "0190.1",
        LuminoxMeasurementType.temperature_sensor: "-27.3",
        LuminoxMeasurementType.barometric_pressure: "0970",
        LuminoxMeasurementType.percent_o2: "020.31",
        LuminoxMeasurementType.sensor_status: "0000",
    }
    read_txt_stream = (
        " ".join(
            f"{measurement} {value}"
            for (measurement, value) in expected_measurement_values.items()
        )
        + com.config.terminator_str()
    )
    com.put_text(read_txt_stream)

    lumi.output = LuminoxOutputMode.polling
    with pytest.raises(LuminoxOutputModeError):
        lumi.read_streaming()

    lumi.output = LuminoxOutputMode.streaming
    readout = lumi.read_streaming()
    expected_measurement_values = {
        measurement: float(value)
        for (measurement, value) in expected_measurement_values.items()
    }
    assert readout == expected_measurement_values


@pytest.mark.parametrize(
    "wrong_stream_read",
    [
        "O 0190.1 T -27.3 P  e 0000 % 020.31",  # missing value
        "O 0190.1 T -27.3 P 0970 e 0000 % ",  # missing value #2
        "O 0190.1 T -27.3 0970 e 0000 % 020.31",  # missing type symbol
    ],
)
def test_read_stream_measurement_type_error(testdev, wrong_stream_read):
    com, lumi = testdev
    lumi.output = LuminoxOutputMode.streaming
    com.put_text(wrong_stream_read)
    with pytest.raises(LuminoxMeasurementTypeError):
        lumi.read_streaming()


@pytest.mark.parametrize(
    "measurement_type, value_str",
    [
        (LuminoxMeasurementType.partial_pressure_o2, f"{190.1:06.1f}"),
        (LuminoxMeasurementType.temperature_sensor, f"{-12.3:05.1f}"),
        (LuminoxMeasurementType.serial_number, "00123 56895"),
    ],
)
def test_query_single_measurement(testdev, measurement_type, value_str):
    com, lumi = testdev

    com.put_text(f"{measurement_type.command} {value_str}{com.config.terminator_str()}")

    lumi.output = LuminoxOutputMode.polling
    value = lumi.query_polling(measurement_type)
    expected_value = measurement_type.cast_type(value_str)
    assert value == expected_value


def test_query_single_measurement_all_measurements(testdev):
    com, lumi = testdev

    expected_measurement_values = {
        LuminoxMeasurementType.partial_pressure_o2: "0190.1",
        LuminoxMeasurementType.temperature_sensor: "-27.3",
        LuminoxMeasurementType.barometric_pressure: "0970",
        LuminoxMeasurementType.percent_o2: "020.31",
        LuminoxMeasurementType.sensor_status: "0000",
    }
    read_txt_stream = (
        " ".join(
            f"{measurement} {value}"
            for (measurement, value) in expected_measurement_values.items()
        )
        + com.config.terminator_str()
    )
    com.put_text(read_txt_stream)

    lumi.output = LuminoxOutputMode.polling
    value = lumi.query_polling(LuminoxMeasurementType.all_measurements)
    expected_measurement_values = {
        measurement: float(value)
        for (measurement, value) in expected_measurement_values.items()
    }
    assert value == expected_measurement_values


def test_query_single_measurement_error_streaming_mode(testdev):
    com, lumi = testdev

    measurement_type = LuminoxMeasurementType.partial_pressure_o2
    expected_value = 190.1
    com.put_text(
        f"{measurement_type} {expected_value:06.1f}" f"{com.config.terminator_str()}"
    )

    lumi.output = LuminoxOutputMode.streaming
    with pytest.raises(LuminoxOutputModeError):
        lumi.query_polling(LuminoxMeasurementType.partial_pressure_o2)


def test_query_single_measurement_warning(testdev):
    com, lumi = testdev

    expected_value = 190.1
    com.put_text(
        f"{LuminoxMeasurementType.partial_pressure_o2} {expected_value:06.1f}"
        f" IGNORE ME{com.config.terminator_str()}"
    )

    lumi.output = LuminoxOutputMode.polling
    value = lumi.query_polling(LuminoxMeasurementType.partial_pressure_o2)
    assert value == expected_value
    # opt: check if the warning was actually issued


@pytest.mark.parametrize(
    "wrong_partial_pressure_o2_read",
    [
        "Z 0190.1",  # wrong type symbol
        str(LuminoxMeasurementType.partial_pressure_o2),  # missing value
        "0190.1",  # missing type symbol
    ],
)
def test_query_single_measurement_type_error(testdev, wrong_partial_pressure_o2_read):
    com, lumi = testdev
    lumi.output = LuminoxOutputMode.polling
    com.put_text(wrong_partial_pressure_o2_read)
    with pytest.raises(LuminoxMeasurementTypeError):
        lumi.query_polling(LuminoxMeasurementType.partial_pressure_o2)


def test_query_single_measurement_str_enum_name(testdev):
    com, lumi = testdev

    measurement_type = LuminoxMeasurementType.serial_number
    expected_value = "00123 56895"
    com.put_text(
        f"{measurement_type.command} {expected_value}{com.config.terminator_str()}"
    )

    lumi.output = LuminoxOutputMode.polling
    value = lumi.query_polling(measurement_type.name)
    assert value == expected_value

    with pytest.raises(ValueError):
        lumi.query_polling(measurement_type.name.replace("_", " "))


def test_query_single_measurement_str_enum_value(testdev):
    com, lumi = testdev

    measurement_type = LuminoxMeasurementType.serial_number
    expected_value = "00123 56895"
    com.put_text(
        f"{measurement_type.command} {expected_value}{com.config.terminator_str()}"
    )

    lumi.output = LuminoxOutputMode.polling
    value = lumi.query_polling(measurement_type.value)
    assert value == expected_value

    with pytest.raises(ValueError):
        lumi.query_polling(measurement_type.command + " ?")
