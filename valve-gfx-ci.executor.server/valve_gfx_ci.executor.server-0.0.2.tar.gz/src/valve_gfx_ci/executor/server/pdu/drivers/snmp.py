from easysnmp import snmp_get, snmp_set, snmp_walk
from .. import logger, PDU, PDUPort, PDUState
from typing import Dict

import random
import time


def _is_int(s):
    try:
        s = int(s)
        return True
    except ValueError:
        return False


def retry_on_known_errors(func):
    retriable_errors = [
        "<built-in function set> returned NULL without setting an error",
        "<built-in function get> returned NULL without setting an error",
        "<built-in function walk> returned NULL without setting an error",
    ]

    def retry(*args, **kwargs):
        retries = 3

        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except SystemError as e:
                if str(e) in retriable_errors:
                    logger.warning(f"Caught the re-triable error '{str(e)}', retrying ({i+1}/{retries})")

                    # Wait a minimum of 1 second, plus a random delay to reduce the chances of concurrent requests
                    time.sleep(1 + random.random())
                    continue
                raise e

        raise ValueError(f"The function {func} failed {retries} times in a row")

    return retry


class SnmpPDU(PDU):
    oid_enterprise = '1.3.6.1.4.1'

    def __init__(self, name, config):
        self.hostname = config.get('hostname', None)
        if not self.hostname:
            raise ValueError('SnmpPDU requires a "hostname" configuration key')
        self.community = config.get('community', 'private')

        assert self.system_id
        assert self.outlet_labels
        assert self.outlet_status

        if not hasattr(self, 'outlet_ctrl'):
            # Some PDUs offer a RW status tree, others require a separate
            # tree for writes. Default to the seemingly more common case
            # of a RW tree.
            self.outlet_ctrl = self.outlet_status

        # FIXME: THe UNKNOWN status is a bit of an odd one, not all PDUs expose such a concept.
        assert self.state_mapping.keys() == set([PDUState.ON, PDUState.OFF, PDUState.REBOOT])
        if not hasattr(self, 'inverse_state_mapping'):
            self.inverse_state_mapping: Dict[int, PDUState] = \
                dict([(value, key) for key, value in self.state_mapping.items()])
        else:
            assert self.inverse_state_mapping.keys() == set([PDUState.ON, PDUState.OFF, PDUState.REBOOT])
        super().__init__(name)

    @property
    def outlet_system_id(self):
        return f'{self.oid_enterprise}.{self.system_id}'

    @property
    def outlet_labels_oid(self):
        return f'{self.outlet_system_id}.{self.outlet_labels}'

    def outlet_status_oid(self, port_id):
        assert isinstance(port_id, int)
        return f'{self.outlet_system_id}.{self.outlet_status}.{port_id}'

    def outlet_ctrl_oid(self, port_id: int):
        assert isinstance(port_id, int)
        return f'{self.outlet_system_id}.{self.outlet_ctrl}.{port_id}'

    @property
    def ports(self):
        ports = []

        try:
            names = [x.value for x in
                     snmp_walk(self.outlet_labels_oid,
                               hostname=self.hostname,
                               community=self.community,
                               version=1)]
        except SystemError as e:
            raise ValueError(f"The snmp_walk() call failed with the following error: {e}")

        for i, name in enumerate(names):
            ports.append(PDUPort(self, i+1, name))

        return ports

    def _port_spec_to_int(self, port_spec):
        if _is_int(port_spec):
            return port_spec
        else:
            for port in self.ports:
                if port.label == port_spec:
                    return port.port_id
            raise ValueError(
                f"{port_spec} can not be interpreted as a valid port")

    @retry_on_known_errors
    def set_port_state(self, port_spec, state):
        SNMP_INTEGER_TYPE = 'i'

        port_id = self._port_spec_to_int(port_spec)
        logger.debug('setting OID %s to state %s with value %d',
                     self.outlet_ctrl_oid(port_id),
                     state,
                     self.state_mapping[state])
        ret = snmp_set(self.outlet_ctrl_oid(port_id),
                       self.state_mapping[state],
                       SNMP_INTEGER_TYPE,
                       hostname=self.hostname,
                       version=1,
                       community=self.community)

        if self.state_transition_delay_seconds is not None:
            logger.debug("Enforcing %s seconds of delay for state change", self.state_transition_delay_seconds)
            # TODO: keep track of state changes to avoid a forced sleep.
            # TODO: Polling for the state change would be better in general.
            # The root cause of this is because PDUs maintain their
            # own configurables how long to delay between
            # transitions, we should probably control that via SNMP,
            # as well.
            time.sleep(self.state_transition_delay_seconds)

        return ret

    @retry_on_known_errors
    def get_port_state(self, port_spec):
        port_id = self._port_spec_to_int(port_spec)
        vs = snmp_get(self.outlet_status_oid(port_id),
                      hostname=self.hostname,
                      version=1,
                      community=self.community)
        value = int(vs.value)
        logger.debug('retrieved OID %s with value %d, maps to state %s',
                     self.outlet_status_oid(port_id),
                     value,
                     self.inverse_state_mapping[value])
        return self.inverse_state_mapping[value]

    def __eq__(self, other):
        return not any([
            getattr(self, attr, None) != getattr(other, attr, None)
            for attr in ["name",
                         "hostname",
                         "community",
                         "system_id",
                         "outlet_labels",
                         "outlet_status",
                         "outlet_ctrl",
                         "state_mapping",
                         "inverse_state_mapping"]])


class ManualSnmpPDU(SnmpPDU):
    def __init__(self, name, config):
        self.system_id = config.get('system_id')
        self.outlet_labels = config.get('outlet_labels')
        self.outlet_status = config.get('outlet_status')
        # Some PDUs offer a RW status tree, others require a separate
        # tree for writes. Default to the seemingly more common case
        # of a RW tree.
        self.outlet_ctrl = config.get('outlet_ctrl', self.outlet_status)

        def populate_state_mapping(state_mapping, d):
            for state, internal_value in d.items():
                v = int(internal_value)
                if state.lower() == "on":
                    state_mapping[PDUState.ON] = v
                elif state.lower() == "off":
                    state_mapping[PDUState.OFF] = v
                elif state.lower() == "reboot":
                    state_mapping[PDUState.REBOOT] = v
                    # Unknown deliberately excluded.
        self.state_mapping = {}
        populate_state_mapping(self.state_mapping,
                               config.get('state_mapping', {}))
        if 'inverse_state_mapping' in config:
            self.inverse_state_mapping = {}
            populate_state_mapping(self.inverse_state_mapping,
                                   config.get('inverse_state_mapping'))

        super().__init__(name, config)
