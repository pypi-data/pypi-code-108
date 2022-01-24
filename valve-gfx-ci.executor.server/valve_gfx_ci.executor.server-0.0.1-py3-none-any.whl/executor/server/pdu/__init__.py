from datetime import datetime
from enum import IntEnum

import time
from logging import getLogger, getLevelName, Formatter, StreamHandler


logger = getLogger(__name__)
logger.setLevel(getLevelName('DEBUG'))
log_formatter = \
    Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] %(funcName)s: "
              "%(message)s")
console_handler = StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


class PDUState(IntEnum):
    UNKNOWN = 0
    OFF = 1
    ON = 2
    REBOOT = 3

    @classmethod
    def valid_actions(cls):
        return [s for s in PDUState if s.value > 0]

    @property
    def is_valid_action(self):
        return self in self.valid_actions()


class PDUPort:
    def __init__(self, pdu, port_id, label=None, min_off_time=5):
        self.pdu = pdu
        self.port_id = port_id
        self.label = label
        self.min_off_time = min_off_time

        self.last_shutdown = datetime.now()

    def set(self, state):
        # Check the current state before writing it
        cur_state = self.state
        logger.debug("set: %s -> %s", cur_state, state)
        if cur_state == state:
            return

        if cur_state == PDUState.OFF and state == PDUState.ON:
            # Enforce a minimum amount of time between state changes
            time_spent_off = (datetime.now() - self.last_shutdown).total_seconds()
            if time_spent_off < self.min_off_time:
                time.sleep(self.min_off_time - time_spent_off)

        self.pdu.set_port_state(self.port_id, state)

        if state == PDUState.OFF:
            self.last_shutdown = datetime.now()

    @property
    def state(self):
        return self.pdu.get_port_state(self.port_id)

    def __eq__(self, other):
        for attr in ["pdu", "port_id", "label", "min_off_time"]:
            if getattr(self, attr, None) != getattr(other, attr, None):
                return False
        return True


class PDU:
    def __init__(self, name):
        self.name = name
        # FIXME: It would be better to poll on state changes than wait
        # arbitrary amounts of time. Abstracting state transitions
        # into a method, so that subclasses can do more intelligent
        # things (in SNMP, a better thing can be done, for instance),
        # would be a start. There's a couple things in play for these pauses,
        #  1. The firmware on different PDUs needs differing amounts
        #  of time to settle in state transitions.  2. SNMP PDUs
        #  typically offer a way for the user to add state transition
        #  delays of their own, and these come with defaults that we
        #  need to wait *at least* that long for. We should do a
        #  better job of provisioning these values to suit our needs.
        if not hasattr(self, 'state_transition_delay_seconds'):
            self.state_transition_delay_seconds = 1

    @property
    def ports(self):
        # NOTICE: Left for drivers to implement
        return []

    def set_port_state(self, port_id, state):
        # NOTICE: Left for drivers to implement
        return False

    def get_port_state(self, port_id):
        # NOTICE: Left for drivers to implement
        return PDUState.UNKNOWN

    @classmethod
    def supported_pdus(cls):
        from .drivers.apc import ApcMasterswitchPDU
        from .drivers.cyberpower import PDU41004, PDU15SWHVIEC12ATNET
        from .drivers.dummy import DummyPDU
        from .drivers.virtual import VirtualPDU
        from .drivers.snmp import SnmpPDU

        return {
            "apc_masterswitch": ApcMasterswitchPDU,
            "cyberpower_pdu41004": PDU41004,
            "cyberpower_pdu15swhviec12atnet": PDU15SWHVIEC12ATNET,
            "dummy": DummyPDU,
            "vpdu": VirtualPDU,
            "snmp": SnmpPDU,
        }

    @classmethod
    def create(cls, model_name, pdu_name, config):
        driver = cls.supported_pdus().get(model_name)

        if driver is None:
            raise ValueError(f"Unknown model name '{model_name}'")

        return driver(pdu_name, config)
