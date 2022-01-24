from .snmp import SnmpPDU
from .. import PDUState


class ApcMasterswitchPDU(SnmpPDU):
    system_id = '318.1.1.4'
    outlet_labels = '4.2.1.4'
    outlet_status = '4.2.1.3'

    state_mapping = {
        PDUState.ON: 1,
        PDUState.OFF: 2,
        PDUState.REBOOT: 3,
    }
