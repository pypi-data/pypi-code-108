#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#

import logging
import threading

import pytest

from hvl_ccb.dev.highland_t560.base import (T560Error,
                                            TriggerMode,
                                            AutoInstallMode,
                                            GateMode)
from hvl_ccb.dev.highland_t560.channel import Polarity
from hvl_ccb.dev.highland_t560.device import T560
from tests.masked_comm.telnet_mockup import LocalT560Server
from tests.masked_comm.uitls import get_free_tcp_port

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="function")
def com_telnet():
    host = "127.0.0.1"
    return {
        "host": host,
        "port": get_free_tcp_port(host),
        "timeout": 0.05,
        "wait_sec_read_text_nonempty": 0.05,
        "default_n_attempts_read_text_nonempty": 2
    }


def start_t560_telnet(com):
    ts = LocalT560Server(port=com["port"], timeout=com["timeout"])
    x = threading.Thread(target=ts.open)
    x.start()
    t560 = T560(com)
    x.join()

    return ts, t560


def full_start_devices(com):
    ts, t560 = start_t560_telnet(com)
    t560.start()
    return ts, t560


def test_devices(com_telnet):
    ts, t560 = start_t560_telnet(com_telnet)
    assert ts is not None
    assert t560.__class__ is T560
    t560.stop()
    ts.close()


def test_error_response(com_telnet):
    ts, t560 = full_start_devices(com_telnet)
    with pytest.raises(T560Error):
        t560.com.query("Throw an error")
    t560.stop()
    ts.close()


def test_device_settings(com_telnet):
    ts, t560 = full_start_devices(com_telnet)
    t560._status
    t560.activate_clock_output()
    t560.use_external_clock()
    t560.save_device_configuration()
    t560.load_device_configuration()
    t560.auto_install_mode = 0
    ts.auto_install_response = "0"
    with pytest.raises(ValueError):
        t560.auto_install_mode = 3
    with pytest.raises(ValueError):
        t560.auto_install_mode = "OFF"
    assert t560.auto_install_mode == AutoInstallMode.OFF
    t560.stop()
    ts.close()


def test_trigger_settings(com_telnet):
    ts, t560 = full_start_devices(com_telnet)
    t560.trigger_mode = TriggerMode.COMMAND
    ts.trigger_response = "Trig REM HIZ Level 1.250 Div 00 SYN 00010000.00"
    assert t560.trigger_mode == TriggerMode.COMMAND
    with pytest.raises(ValueError):
        t560.trigger_level = 5
    t560.fire_trigger()
    t560.trigger_level = 2
    ts.trigger_response = "Trig REM HIZ Level 2.000 Div 00 SYN 00010000.00"
    assert t560.trigger_level == 2
    with pytest.raises(ValueError):
        t560.trigger_level = 5
    with pytest.raises(ValueError):
        t560.trigger_mode = "INT"
    t560.disarm_trigger()
    t560.frequency = 16_000_000
    ts.trigger_response = "Trig REM HIZ Level 1.250 Div 00 SYN 16,000,000"
    with pytest.raises(ValueError):
        t560.frequency = 20_000_000
    t560.period = 1E-7
    ts.trigger_response = "Trig REM HIZ Level 1.250 Div 00 SYN 10,000,000"
    with pytest.raises(ValueError):
        t560.period = 1E-8
    assert t560.period == 1E-7
    assert t560.frequency == 10_000_000
    ts.trigger_response = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        t560._trigger_status
    t560.stop()
    ts.close()


def test_gate_settings(com_telnet):
    ts, t560 = full_start_devices(com_telnet)
    t560.gate_mode = GateMode.INPUT
    ts.gate_response = "Gate INP POS HIZ Shots 0000000066"
    with pytest.raises(ValueError):
        t560.gate_mode = "ON"
    assert t560.gate_mode == "INP"
    t560.gate_polarity = "NEG"
    ts.gate_response = "Gate INP NEG HIZ Shots 0000000066"
    assert t560.gate_polarity == Polarity.ACTIVE_LOW
    ts.gate_response = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        t560._gate_status
    t560.stop()
    ts.close()


def test_channel_settings(com_telnet):
    ts, t560 = full_start_devices(com_telnet)
    t560.ch_b.polarity = "NEG"
    ts.channel_response = "Ch B  NEG  ON  Dly  00.000,000  Wid  00.000,002"
    with pytest.raises(ValueError):
        t560.ch_b.polarity = "+"
    assert t560.ch_b.polarity == Polarity.ACTIVE_LOW
    t560.ch_c.enabled = True
    ts.channel_response = "Ch C  POS  ON  Dly  00.000,000  Wid  00.000,002"
    assert t560.ch_c.enabled
    t560.ch_d.enabled = False
    ts.channel_response = "Ch D  POS  OFF  Dly  00.000,000  Wid  00.000,002"
    with pytest.raises(TypeError):
        t560.ch_d.enabled = "YES"
    assert not t560.ch_d.enabled
    t560.ch_a.delay = 1E-6
    ts.channel_response = "Ch A  POS  OFF  Dly  00.000,001  Wid  00.000,002"
    with pytest.raises(ValueError):
        t560.ch_a.delay = 100
    assert t560.ch_a.delay == 1E-6
    t560.ch_a.width = 1
    ts.channel_response = "Ch A  POS  OFF  Dly  00.000,001  Wid  01.000,000"
    with pytest.raises(ValueError):
        t560.ch_a.width = -1
    assert t560.ch_a.width
    ts.channel_response = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        t560.ch_a._status
    t560.stop()
    ts.close()
