from .._ingenialink import lib, ffi
from ingenialink.ipb.servo import IPBServo

import ingenialogger
logger = ingenialogger.get_logger(__name__)


class EthercatServo(IPBServo):
    """Servo object for all the EtherCAT slave functionalities.

    Args:
        cffi_servo (CData): CData instance of the servo.
        cffi_net (CData): CData instance of the network.
        target (int): Target ID for the slave.
        dictionary_path (str): Path to the dictionary.
        servo_status_listener (bool): Toggle the listener of the servo for
            its status, errors, faults, etc.

    """
    def __init__(self, cffi_servo, cffi_net, target, dictionary_path=None,
                 servo_status_listener=True):
        servo = ffi.gc(cffi_servo, lib.il_servo_fake_destroy)
        super(EthercatServo, self).__init__(
            servo, cffi_net, target, dictionary_path)

        if servo_status_listener:
            self.start_status_listener()
        else:
            self.stop_status_listener()
