from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import copy
import time

from server.pdu import PDUState, PDUPort, PDU
from server.pdu.drivers.apc import ApcMasterswitchPDU
from server.pdu.drivers.cyberpower import PDU41004
from server.pdu.drivers.dummy import DummyPDU
from server.pdu.drivers.snmp import (
    retry_on_known_errors,
    SnmpPDU,
    ManualSnmpPDU,
    snmp_get,
    snmp_set,
    snmp_walk
)


def test_PDUState_UNKNOW_is_invalid_action():
    assert PDUState.UNKNOWN not in PDUState.valid_actions()
    assert PDUState.UNKNOWN.is_valid_action is False


def test_PDUState_valid_actions_contain_basics():
    for action in ["ON", "OFF", "REBOOT"]:
        assert action in [s.name for s in PDUState.valid_actions()]
        assert getattr(PDUState, action).is_valid_action is True


def test_PDUPort_get_set():
    pdu = MagicMock(get_port_state=MagicMock(return_value=PDUState.OFF))
    port = PDUPort(pdu, 42, label="My Port")
    assert port.label == "My Port"

    last_shutdown = port.last_shutdown

    pdu.set_port_state.assert_not_called()
    pdu.get_port_state.assert_not_called()

    assert pdu.set_port_state.call_count == 0
    port.set(PDUState.ON)
    pdu.set_port_state.assert_called_with(42, PDUState.ON)
    assert pdu.set_port_state.call_count == 1
    assert port.last_shutdown == last_shutdown

    assert port.state == PDUState.OFF
    pdu.get_port_state.assert_called_with(42)

    # Check that setting the port to the same value does not change anything
    port.set(PDUState.OFF)
    assert pdu.set_port_state.call_count == 1
    assert port.last_shutdown == last_shutdown

    # Check that whenever we set the PDU state to OFF, we update last_shutdown
    pdu.get_port_state.return_value = PDUState.ON
    port.set(PDUState.OFF)
    assert port.last_shutdown > last_shutdown


def test_PDUPort_eq():
    params = {
        "pdu": "pdu",
        "port_id": 42,
        "label": "label",
        "min_off_time": "min_off_time"
    }

    assert PDUPort(**params) == PDUPort(**params)
    for param in params:
        n_params = dict(params)
        n_params[param] = "modified"
        assert PDUPort(**params) != PDUPort(**n_params)


def test_PDU_defaults():
    pdu = PDU("MyPDU")

    assert pdu.name == "MyPDU"
    assert pdu.ports == []
    assert pdu.set_port_state(42, PDUState.ON) is False
    assert pdu.get_port_state(42) == PDUState.UNKNOWN


def test_PDU_supported_pdus():
    pdus = PDU.supported_pdus()
    assert "dummy" in pdus


def test_PDU_create():
    pdu = PDU.create("dummy", "name", {})
    assert pdu.name == "name"

    with pytest.raises(ValueError):
        PDU.create("invalid", "name", {})


# Drivers

@pytest.fixture(autouse=True)
def reset_easysnmp_mock(monkeypatch):
    import server.pdu.drivers.snmp as snmp

    global snmp_get, snmp_set, snmp_walk, time_sleep
    m1, m2, m3, m4 = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    # REVIEW: I wonder if there's a clever way of covering the
    # difference in import locations between here and snmp.py
    monkeypatch.setattr(snmp, "snmp_walk", m1)
    monkeypatch.setattr(snmp, "snmp_get", m2)
    monkeypatch.setattr(snmp, "snmp_set", m3)
    monkeypatch.setattr(time, "sleep", m4)
    snmp_walk = m1
    snmp_get = m2
    snmp_set = m3
    time_sleep = m4


@patch("random.random", return_value=0.42)
def test_driver_BaseSnmpPDU_retry_on_known_errors__known_error(random_mock):
    global retriable_error_call_count
    retriable_error_call_count = 0

    @retry_on_known_errors
    def retriable_error():
        global retriable_error_call_count

        assert time_sleep.call_count == retriable_error_call_count

        retriable_error_call_count += 1
        raise SystemError("<built-in function set> returned NULL without setting an error")

    with pytest.raises(ValueError):
        retriable_error()

    time_sleep.assert_called_with(1.42)
    assert time_sleep.call_count == retriable_error_call_count
    assert retriable_error_call_count == 3


def test_driver_BaseSnmpPDU_retry_on_known_errors__unknown_error():
    global unretriable_error_call_count
    unretriable_error_call_count = 0

    @retry_on_known_errors
    def unretriable_error():
        global unretriable_error_call_count
        unretriable_error_call_count += 1
        raise SystemError("Unknown error")

    with pytest.raises(SystemError):
        unretriable_error()

    time_sleep.assert_not_called()
    assert unretriable_error_call_count == 1


class MockSnmpPDU(SnmpPDU):
    system_id = '1234.1.2.3.4'
    outlet_labels = '4.5.4.5'
    outlet_status = '4.5.4.6'

    state_mapping = {
        PDUState.ON: 2,
        PDUState.OFF: 3,
        PDUState.REBOOT: 4,
    }

    state_transition_delay_seconds = 5


def test_driver_SnmpPDU_eq():
    params = {
        "hostname": "hostname",
        "community": "community"
    }

    assert MockSnmpPDU("name", params) == MockSnmpPDU("name", params)
    for param in params:
        n_params = dict(params)
        n_params[param] = "modified"
        assert MockSnmpPDU("name", params) != MockSnmpPDU("name", n_params)


def test_driver_SnmpPDU_listing_ports():
    pdu = MockSnmpPDU("MyPDU", {"hostname": "127.0.0.1"})
    snmp_walk.return_value = [MagicMock(value="P1"), MagicMock(value="P2")]
    snmp_walk.assert_not_called()
    ports = pdu.ports
    snmp_walk.assert_called_with(pdu.outlet_labels_oid,
                                 hostname=pdu.hostname, community=pdu.community,
                                 version=1)

    # Check that the labels are stored, and the port IDs are 1-indexed
    for i in range(0, 2):
        assert ports[i].port_id == i+1
        assert ports[i].label == f"P{i+1}"

    snmp_walk.side_effect = SystemError("<built-in function walk> returned NULL without setting an error")
    with pytest.raises(ValueError):
        pdu.ports


def test_driver_BaseSnmpPDU_port_label_mapping():
    pdu = MockSnmpPDU("MyPDU", {"hostname": "127.0.0.1"})
    snmp_walk.return_value = [
        MagicMock(value="P1"),
        MagicMock(value="P2")
    ]
    snmp_set.return_value = True
    assert pdu.set_port_state("P1", PDUState.REBOOT) is True
    snmp_set.assert_called_with(pdu.outlet_ctrl_oid(1),
                                pdu.state_mapping[PDUState.REBOOT], 'i',
                                hostname=pdu.hostname, community=pdu.community,
                                version=1)
    assert pdu.set_port_state("P2", PDUState.REBOOT) is True
    snmp_set.assert_called_with(pdu.outlet_ctrl_oid(2),
                                pdu.state_mapping[PDUState.REBOOT], 'i',
                                hostname=pdu.hostname, community=pdu.community,
                                version=1)
    with pytest.raises(ValueError):
        pdu.set_port_state("flubberbubber", PDUState.OFF)


def test_driver_BaseSnmpPDU_get_port():
    pdu = MockSnmpPDU("MyPDU", {"hostname": "127.0.0.1"})
    type(snmp_get.return_value).value = \
        PropertyMock(return_value=pdu.state_mapping[PDUState.REBOOT])
    snmp_get.assert_not_called()
    pdu_state = pdu.get_port_state(2)
    assert pdu_state == PDUState.REBOOT
    snmp_get.assert_called_with(pdu.outlet_status_oid(2),
                                hostname=pdu.hostname, community=pdu.community,
                                version=1)

    snmp_get.side_effect = SystemError("<built-in function get> returned NULL without setting an error")
    with pytest.raises(ValueError):
        pdu.get_port_state(2)


def test_driver_BaseSnmpPDU_set_port():
    pdu = MockSnmpPDU("MyPDU", {"hostname": "127.0.0.1"})
    type(snmp_get.return_value).value = \
        PropertyMock(return_value=pdu.state_mapping[PDUState.REBOOT])
    snmp_set.return_value = True
    snmp_set.assert_not_called()
    assert pdu.set_port_state(2, PDUState.REBOOT) is True
    snmp_set.assert_called_with(pdu.outlet_ctrl_oid(2),
                                pdu.state_mapping[PDUState.REBOOT], 'i',
                                hostname=pdu.hostname, community=pdu.community,
                                version=1)

    snmp_set.side_effect = SystemError("<built-in function set> returned NULL without setting an error")
    with pytest.raises(ValueError):
        pdu.set_port_state(2, PDUState.REBOOT)


def test_driver_BaseSnmpPDU_action_translation():
    pdu = MockSnmpPDU("MyPDU", {"hostname": "127.0.0.1"})

    # Check the state -> SNMP value translation
    for action in PDUState.valid_actions():
        assert pdu.inverse_state_mapping[pdu.state_mapping[action]] == action

    with pytest.raises(KeyError):
        pdu.state_mapping[PDUState.UNKNOWN]


def test_driver_ApcMasterswitchPDU_check_OIDs():
    pdu = ApcMasterswitchPDU("MyPDU", {"hostname": "127.0.0.1"})

    assert pdu.outlet_labels_oid == f"{pdu.oid_enterprise}.318.1.1.4.4.2.1.4"
    assert pdu.outlet_status_oid(10) == f"{pdu.oid_enterprise}.318.1.1.4.4.2.1.3.10"
    assert pdu.outlet_ctrl_oid(10) == f"{pdu.oid_enterprise}.318.1.1.4.4.2.1.3.10"


def test_driver_PDU41004_check_OIDs():
    pdu = PDU41004("MyPDU", {"hostname": "127.0.0.1"})
    assert pdu.outlet_labels_oid == f"{pdu.oid_enterprise}.3808.1.1.3.3.3.1.1.2"
    assert pdu.outlet_status_oid(10) == f"{pdu.oid_enterprise}.3808.1.1.3.3.3.1.1.4.10"
    assert pdu.outlet_ctrl_oid(10) == f"{pdu.oid_enterprise}.3808.1.1.3.3.3.1.1.4.10"


def test_driver_DummyPDU():
    ports = ['P1', 'P2', 'P3']
    pdu = DummyPDU("MyPDU", {"ports": ports})

    assert [p.label for p in pdu.ports] == ports
    assert pdu.get_port_state(0) == PDUState.ON
    pdu.set_port_state(0, PDUState.OFF)
    assert pdu.get_port_state(0) == PDUState.OFF


def test_driver_ManualSnmpPDU_check_OIDs_and_default_actions():
    pdu = ManualSnmpPDU("MyPDU", config={
        "hostname": "127.0.0.1",
        "system_id": "1.2.3.4",
        "outlet_labels": "5.6.7.8",
        "outlet_status": "5.6.7.9",
        "outlet_ctrl": "5.6.7.10",
        "state_mapping": {
            "on": 1,
            "off": 2,
            "reboot": 3,
        },
    })

    assert pdu.community == "private"
    assert pdu.outlet_labels == "5.6.7.8"
    assert pdu.outlet_status_oid(10) == "1.3.6.1.4.1.1.2.3.4.5.6.7.9.10"
    assert pdu.outlet_ctrl_oid(10) == "1.3.6.1.4.1.1.2.3.4.5.6.7.10.10"
    assert pdu.state_mapping.keys() == set([PDUState.ON, PDUState.OFF, PDUState.REBOOT])
    assert pdu.inverse_state_mapping.keys() == set([1, 2, 3])
    for k, _ in pdu.state_mapping.items():
        assert pdu.inverse_state_mapping[pdu.state_mapping[k]] == k


def test_driver_ManualSnmpPDU_invalid_actions():
    with pytest.raises(ValueError):
        ManualSnmpPDU("MyPDU", config={
            "hostname": "127.0.0.1",
            "system_id": "1.2.3.4",
            "outlet_labels": "5.6.7.8",
            "outlet_status": "5.6.7.9",
            "outlet_ctrl": "5.6.7.10",
            "state_mapping": {
                "on": "FUDGE",
                "off": 2,
                "reboot": 3,
            },
        })


def test_driver_ManualSnmpPDU_missing_actions():
    with pytest.raises(AssertionError):
        ManualSnmpPDU("MyPDU", config={
            "hostname": "127.0.0.1",
            "system_id": "1.2.3.4",
            "outlet_labels": "5.6.7.8",
            "outlet_status": "5.6.7.9",
            "outlet_ctrl": "5.6.7.10",
            "state_mapping": {
                "off": 2,
                "reboot": 3,
            },
        })


def test_driver_ManualSnmpPDU_missing_parameters():
    valid_config = {
        "hostname": "127.0.0.1",
        "system_id": "1.2.3.4",
        "outlet_labels": "5.6.7.8",
        "outlet_status": "5.6.7.9",
        "outlet_ctrl": "5.6.7.10",
        "state_mapping": {
            "on": 1,
            "off": 2,
            "reboot": 3,
        },
    }

    ManualSnmpPDU("MyPDU", config=valid_config)
    for required_param in ["hostname", "system_id", "outlet_labels", "outlet_status", "state_mapping"]:
        new_config = copy.deepcopy(valid_config)
        del new_config[required_param]
        with pytest.raises((ValueError, AssertionError)):
            ManualSnmpPDU("MyPDU", config=new_config)


def test_driver_ManualSnmpPDU_weird_inverses():
    valid_config = {
        "hostname": "127.0.0.1",
        "system_id": "1.2.3.4",
        "outlet_labels": "5.6.7.8",
        "outlet_status": "5.6.7.9",
        "outlet_ctrl": "5.6.7.10",
        "state_mapping": {
            "on": 1,
            "off": 2,
            "reboot": 3,
        },
        "inverse_state_mapping": {
            "on": 2,
            "off": 3,
            "reboot": 4,
        },
    }

    pdu = ManualSnmpPDU("MyPDU", config=valid_config)
    for k, _ in pdu.state_mapping.items():
        assert pdu.inverse_state_mapping[pdu.state_mapping[k]] == k + 1
