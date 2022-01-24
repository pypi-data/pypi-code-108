#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the R&S RTO1024 digital storage oscilloscope device class.
"""

import pytest

from hvl_ccb.dev import (
    RTO1024,
    RTO1024Config,
    RTO1024Error,
    RTO1024VisaCommunicationConfig,
)
from masked_comm import MaskedVisaCommunication


@pytest.fixture(scope="module")
def com_config():
    return {
        "interface_type": RTO1024VisaCommunicationConfig.InterfaceType.TCPIP_INSTR,
        "host": "127.0.0.1",
        "open_timeout": 10,
        "timeout": 50,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "waveforms_path": "C:\\Data\\DavidGraber\\02_waveforms",
        "settings_path": "C:\\Data\\DavidGraber\\01_settings",
        "backup_path": "D:\\backups",
        "spoll_interval": 0.01,
        "spoll_start_delay": 0,
        "command_timeout_seconds": 0.05,
        "wait_sec_short_pause": 0.01,
        "wait_sec_short_pause": 0.01,
        "wait_sec_post_acquisition_start": 0.01,
    }


@pytest.fixture()
def testdev(com_config, dev_config):
    com = MaskedVisaCommunication(com_config)
    dev = RTO1024(com, dev_config)
    dev.SPOLL_INTERVAL = 0.01
    dev.SPOLL_START_DELAY = 0
    assert dev is not None
    dev.start()
    assert dev.com.get_written() == "&GTR"
    assert dev.com.get_written() == "*RST"
    assert dev.com.get_written() == "*CLS"
    assert dev.com.get_written() == "SYST:DISP:UPD ON"
    assert dev.com.get_written() == "*ESE 127"
    yield dev
    dev.stop()


def test_dev_config(dev_config):
    config = RTO1024Config(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"spoll_interval": 0},
        {"spoll_interval": -1},
        {"spoll_start_delay": -1},
        {"command_timeout_seconds": 0},
        {"wait_sec_short_pause": 0},
        {"wait_sec_short_pause": -1},
        {"wait_sec_enable_history": 0},
        {"wait_sec_post_acquisition_start": 0},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict):
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        RTO1024Config(**invalid_config)


def test_instantiation(com_config, dev_config):
    dev = RTO1024(com_config, dev_config)
    assert dev is not None

    copy_config = dict(com_config)
    copy_config.pop("interface_type")
    dev = RTO1024(copy_config, dev_config)
    assert dev is not None


def test_stop(testdev: RTO1024):
    # case polling: send stopping instructions
    testdev.stop()
    assert testdev.com.get_written() == "*ESE 0"
    assert testdev.com.get_written() == "*SRE 0"
    assert testdev.com.get_written() == "&DCL"
    assert testdev.com.get_written() == "&GTL"
    # case not polling: do nothing, just log a warning
    testdev.stop()


def test_local_display(testdev: RTO1024):
    testdev.local_display(True)
    assert testdev.com.get_written() == "SYST:DISP:UPD ON"

    testdev.local_display(False)
    assert testdev.com.get_written() == "SYST:DISP:UPD OFF"


def test_set_acquire_length(testdev: RTO1024):
    testdev.set_acquire_length(10)
    assert testdev.com.get_written() == "TIMebase:RANGe 10"


def test_get_acquire_length(testdev: RTO1024):
    testdev.com.put_name("TIMebase:RANGe?", "5.00E-6")
    assert testdev.get_acquire_length() == 5e-6


def test_set_reference_point(testdev: RTO1024):
    testdev.set_reference_point(50)
    assert testdev.com.get_written() == "TIMebase:REFerence 50"


def test_get_reference_point(testdev: RTO1024):
    testdev.com.put_name("TIMebase:REFerence?", "20")
    assert testdev.get_reference_point() == 20


def test_set_repetitions(testdev: RTO1024):
    testdev.set_repetitions(10)
    assert testdev.com.get_written() == "ACQuire:COUNt 10"


def test_get_repetitions(testdev: RTO1024):
    testdev.com.put_name("ACQuire:COUNt?", "100")
    assert testdev.get_repetitions() == 100


def test_set_channel_state(testdev: RTO1024):
    testdev.set_channel_state(2, True)
    assert testdev.com.get_written() == "CHANnel2:STATe ON"

    testdev.set_channel_state(3, False)
    assert testdev.com.get_written() == "CHANnel3:STATe OFF"


def test_get_channel_state(testdev: RTO1024):
    testdev.com.put_name("CHANnel1:STATe?", "1")
    assert testdev.get_channel_state(1)


def test_set_channel_scale(testdev: RTO1024):
    testdev.set_channel_scale(1, 1e-3)
    assert testdev.com.get_written() == "CHANnel1:SCALe 0.001"


def test_get_channel_scale(testdev: RTO1024):
    testdev.com.put_name("CHANnel1:SCALe?", "0.001")
    assert testdev.get_channel_scale(1) == 0.001


def test_set_channel_range(testdev: RTO1024):
    testdev.set_channel_range(2, 1.5)
    assert testdev.com.get_written() == "CHANnel2:RANGe 1.500"


def test_get_channel_range(testdev: RTO1024):
    testdev.com.put_name("CHANnel1:RANGe?", "0.01")
    assert testdev.get_channel_range(1) == 0.01


def test_set_channel_position(testdev: RTO1024):
    testdev.set_channel_position(4, 4)
    assert testdev.com.get_written() == "CHANnel4:POSition 4.00"


def test_get_channel_position(testdev: RTO1024):
    testdev.com.put_name("CHANnel1:POSition?", "1.5")
    assert testdev.get_channel_position(1) == 1.5


def test_set_channel_offset(testdev: RTO1024):
    testdev.set_channel_offset(4, 4)
    assert testdev.com.get_written() == "CHANnel4:OFFSet 4.000"


def test_get_channel_offset(testdev: RTO1024):
    testdev.com.put_name("CHANnel1:OFFSet?", "0.6")
    assert testdev.get_channel_offset(1) == 0.6


def test_set_trigger_source(testdev: RTO1024):
    testdev.set_trigger_source(1)  # to channel 1
    assert testdev.com.get_written() == "TRIGger1:SOURce CHAN1"

    testdev.set_trigger_source(3, 2)  # to channel 3, B-Event
    assert testdev.com.get_written() == "TRIGger2:SOURce CHAN3"


def test_set_trigger_level(testdev: RTO1024):
    testdev.set_trigger_level(1, 2e-3)
    assert testdev.com.get_written() == "TRIGger1:LEVel1 0.002"


def test_set_trigger_mode(testdev: RTO1024):
    testdev.set_trigger_mode(RTO1024.TriggerModes.AUTO)
    assert testdev.com.get_written() == "TRIGger1:MODE AUTO"

    testdev.set_trigger_mode(RTO1024.TriggerModes.NORMAL)
    assert testdev.com.get_written() == "TRIGger1:MODE NORMAL"

    testdev.set_trigger_mode(RTO1024.TriggerModes.FREERUN)
    assert testdev.com.get_written() == "TRIGger1:MODE FREERUN"

    testdev.set_trigger_mode("Auto")
    assert testdev.com.get_written() == "TRIGger1:MODE AUTO"

    testdev.set_trigger_mode("normal")
    assert testdev.com.get_written() == "TRIGger1:MODE NORMAL"

    testdev.set_trigger_mode("FREERUN")
    assert testdev.com.get_written() == "TRIGger1:MODE FREERUN"

    with pytest.raises(RTO1024Error):
        testdev.set_trigger_mode("myunknownmode")

    assert testdev.com.get_written() is None


def test_file_copy(testdev: RTO1024):
    testdev.com.stb = 32
    testdev.file_copy("C:\\Data\\test.txt", "D:\\test.txt")
    testdev.com.stb = 0

    assert testdev.com.get_written() == "*CLS"
    assert (
        testdev.com.get_written() == "MMEMory:COPY 'C:\\Data\\test.txt', 'D:\\test.txt'"
    )
    assert testdev.com.get_written() == "*OPC"

    # test timeout
    with pytest.raises(RTO1024Error):
        testdev.file_copy("C:\\Data\\test.txt", "D:\\test.txt")


def test_backup_waveform(testdev: RTO1024):
    testdev.com.stb = 32
    testdev.backup_waveform("test")
    assert testdev.com.get_written() == "*CLS"
    assert (
        testdev.com.get_written()
        == "MMEMory:COPY 'C:\\Data\\DavidGraber\\02_waveforms\\test.Wfm.bin', "
        "'D:\\backups\\test.Wfm.bin'"
    )
    assert testdev.com.get_written() == "*OPC"
    assert testdev.com.get_written() == "*CLS"
    assert (
        testdev.com.get_written()
        == "MMEMory:COPY 'C:\\Data\\DavidGraber\\02_waveforms\\test.bin', "
        "'D:\\backups\\test.bin'"
    )
    assert testdev.com.get_written() == "*OPC"
    testdev.com.stb = 0


def test_list_directory(testdev: RTO1024):
    testdev.com.put_name(
        "MMEMory:CATalog? 'C:/Data'",
        '142422792,147771314176,".,DIR,0","..,DIR,0","DavidGraber,DIR,0","Myriam,DIR,'
        '0","test.Wfm.bin,BIN,142422792"',
    )

    dir_list = testdev.list_directory("C:/Data")
    expected = [
        ["DavidGraber", "DIR", "0"],
        ["Myriam", "DIR", "0"],
        ["test.Wfm.bin", "BIN", "142422792"],
    ]

    assert dir_list == expected


def test_save_waveform_history(testdev: RTO1024):
    testdev.com.put_name(
        f"MMEMory:CATalog? '{testdev.config.waveforms_path}'",
        '142422792,147771314176,".,DIR,0","..,DIR,0","DavidGraber,DIR,0","Myriam,DIR,'
        '0","test.Wfm.bin,BIN,142422792","test.bin,BIN,1234"',
    )
    testdev.com.stb = 32
    testdev.save_waveform_history("test", 1)
    testdev.com.stb = 0
    assert testdev.com.get_written() == "EXPort:WAVeform:FASTexport ON"
    assert testdev.com.get_written() == "CHAN:HIST ON"
    assert testdev.com.get_written() == "SYST:DISP:UPD OFF"
    assert testdev.com.get_written() == "EXPort:WAVeform:MULTichannel OFF"
    assert testdev.com.get_written() == "EXPort:WAVeform:SOURce C1W1"
    assert (
        testdev.com.get_written()
        == "EXPort:WAVeform:NAME 'C:\\Data\\DavidGraber\\02_waveforms\\test.bin'"
    )
    assert testdev.com.get_written() == "EXPort:WAVeform:DLOGging ON"
    assert testdev.com.get_written() == "*CLS"
    assert testdev.com.get_written() == "CHANnel:HISTory:PLAY"
    assert testdev.com.get_written() == "*OPC"
    assert testdev.com.get_written() == "EXPort:WAVeform:FASTexport OFF"
    assert testdev.com.get_written() == "SYST:DISP:UPD ON"

    # with timeout
    with pytest.raises(RTO1024Error):
        testdev.save_waveform_history("test", 1)

    # with "file not found"
    testdev.com.put_name(
        f"MMEMory:CATalog? '{testdev.config.waveforms_path}'",
        '142422792,147771314176,".,DIR,0","..,DIR,0","DavidGraber,DIR,0","Myriam,DIR,'
        '0"',
    )
    testdev.com.stb = 32
    with pytest.raises(RTO1024Error):
        testdev.save_waveform_history("test", 1)
    testdev.com.stb = 0


def test_run_continuous_acquisition(testdev: RTO1024):
    testdev.run_continuous_acquisition()
    assert testdev.com.get_written() == "RUN"


def test_run_single_acquisition(testdev: RTO1024):
    testdev.run_single_acquisition()
    assert testdev.com.get_written() == "SINGle"


def test_stop_acquisition(testdev: RTO1024):
    testdev.stop_acquisition()
    assert testdev.com.get_written() == "STOP"


def test_prepare_ultra_segmentation(testdev: RTO1024):
    testdev.prepare_ultra_segmentation()


def test_save_configuration(testdev: RTO1024):
    testdev.save_configuration("test_configuration")
    assert (
        testdev.com.get_written()
        ==
        "MMEMory:SAV 'C:\\Data\\DavidGraber\\01_settings\\test_configuration.dfl'"
    )


def test_load_configuration(testdev: RTO1024):
    testdev.load_configuration("test_configuration")
    assert (
        testdev.com.get_written()
        ==
        "MMEMory:RCL 'C:\\Data\\DavidGraber\\01_settings\\test_configuration.dfl'"
    )


def test_get_timestamps(testdev: RTO1024):
    testdev.com.put_name("ACQuire:AVAilable?", "3")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "-1.24")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "-0.87")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "0")
    ts = testdev.get_timestamps()
    assert ts == [-1.24, -0.87, 0]

    # with read errors
    testdev.com.put_name("ACQuire:AVAilable?", "3")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "-1.24")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "-1.24")
    testdev.com.put_name("CHANnel:WAVeform:HISTory:TSRelative?", "0")
    with pytest.raises(RTO1024Error):
        testdev.get_timestamps()


def test_activate_measurement(testdev: RTO1024):
    meas_n = 1
    source = "C1W2"
    meas = ["PDEL", "MIN", "MAX"]
    category = "AMPT"
    testdev.activate_measurements(meas_n, source, meas, category)
    assert testdev.com.get_written() == f"MEAS{meas_n}:ENAB ON"
    assert testdev.com.get_written() == f"MEAS{meas_n}:SOUR {source}"
    assert testdev.com.get_written() == f"MEAS{meas_n}:CAT {category}"
    if meas:
        assert testdev.com.get_written() == f"MEAS{meas_n}:MAIN {meas.pop(0)}"
    while meas:
        assert testdev.com.get_written() == f"MEAS{meas_n}:ADD {meas.pop(0)}, ON"


def test_read_measurement(testdev: RTO1024):
    meas_n = 3
    meas_name = "PDEL"
    testdev.com.put_name(f"MEAS{meas_n}:RES? {meas_name}", "0.12034")
    assert testdev.read_measurement(meas_n, meas_name) == 0.12034
