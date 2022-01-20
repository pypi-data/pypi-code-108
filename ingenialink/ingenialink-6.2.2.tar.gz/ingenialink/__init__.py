from .network import NetworkMonitor, NET_PROT, \
    NET_STATE, NET_DEV_EVT, NET_TRANS_PROT, Network, EEPROM_FILE_FORMAT
from .servo import SERVO_STATE, SERVO_FLAGS, SERVO_MODE, \
    SERVO_UNITS_TORQUE, SERVO_UNITS_POS, SERVO_UNITS_VEL, SERVO_UNITS_ACC, Servo
from .monitor import Monitor, MONITOR_TRIGGER

from .ipb.poller import IPBPoller
from .ipb.register import IPBRegister, REG_DTYPE, REG_ACCESS, REG_PHY
from .ipb.dictionary import IPBDictionary
from .ipb.servo import IPBServo

from .serial.network import SerialNetwork
from .serial.servo import SerialServo

from .ethernet.network import EthernetNetwork
from .ethernet.servo import EthernetServo

from .ethercat.network import EthercatNetwork
from .ethercat.servo import EthercatServo

from .canopen.servo import CanopenServo
from .canopen.network import CanopenNetwork, CAN_DEVICE, CAN_DEVICE, \
    CAN_BAUDRATE
from .canopen.poller import CanopenPoller
from .canopen.register import CanopenRegister
from .canopen.dictionary import CanopenDictionary

from ingenialink.utils.errors import err_ipb_last

from ._ingenialink import lib
from ingenialink.utils._utils import pstr

__all__ = ['EEPROM_FILE_FORMAT', 'NET_PROT', 'NET_DEV_EVT', 'NET_STATE',
           'NET_TRANS_PROT', 'SERVO_STATE', 'SERVO_FLAGS', 'SERVO_MODE',
           'SERVO_UNITS_TORQUE', 'SERVO_UNITS_POS', 'SERVO_UNITS_VEL',
           'SERVO_UNITS_ACC', 'NetworkMonitor', 'Network', 'Servo',
           'IPBDictionary', 'IPBRegister', 'REG_DTYPE', 'REG_ACCESS', 'REG_PHY',
           'Monitor', 'MONITOR_TRIGGER', 'IPBPoller', 'IPBServo',
           'SerialNetwork', 'SerialServo', 'EthercatNetwork', 'EthercatServo',
           'EthernetServo', 'EthernetNetwork',
           'CanopenNetwork', 'CAN_DEVICE', 'CAN_BAUDRATE',
           'CanopenServo', 'CanopenPoller', 'CanopenRegister', 'CanopenDictionary',
           'err_ipb_last']

__version__ = '6.2.2'

try:
    __ingenialink_C_version__ = pstr(lib.il_version())
except Exception:
    __ingenialink_C_version__ = '-'
