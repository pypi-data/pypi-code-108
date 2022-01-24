from .snmp import SnmpPDU
from .. import PDUState


class PDU41004(SnmpPDU):
    system_id = '3808.1.1.3.3'
    outlet_labels = '3.1.1.2'
    outlet_status = '3.1.1.4'

    state_mapping = {
        PDUState.ON: 1,
        PDUState.OFF: 2,
        PDUState.REBOOT: 3,
    }

    state_transition_delay_seconds = 5


class PDU15SWHVIEC12ATNET(SnmpPDU):
    system_id = '3808.1.1.5'
    outlet_labels = '6.3.1.2'
    outlet_status = '6.3.1.3'
    outlet_ctrl = '6.5.1.3'

    state_mapping = {
        PDUState.ON: 2,
        PDUState.OFF: 3,
        PDUState.REBOOT: 4,
    }

    # The RMCARD205 management card in this PDU kindly chooses
    # different ints for control vs status codes.
    inverse_state_mapping = {
        1: PDUState.ON,
        2: PDUState.OFF,
        3: PDUState.REBOOT,
    }

    state_transition_delay_seconds = 5
