from enum import Enum
from ..exceptions import *
from ..network import NET_PROT
from .servo import EthercatServo
from ingenialink.constants import *
from .._ingenialink import lib, ffi
from ingenialink.utils._utils import cstr
from ingenialink.ipb.network import IPBNetwork
from ingenialink.network import EEPROM_FILE_FORMAT

import os
import ingenialogger
logger = ingenialogger.get_logger(__name__)


FIRMWARE_UPDATE_ERROR = {
    lib.UP_STATEMACHINE_ERROR: 'Slave could not enter the expected state',
    lib.UP_NOT_IN_BOOT_ERROR: 'Slave is not in Boot Mode',
    lib.UP_EEPROM_PDI_ERROR: 'EEPROM PDI Error',
    lib.UP_EEPROM_FILE_ERROR: 'File was not read properly',
    lib.UP_NOT_FOUND_ERROR: 'No slaves were found',
    lib.UP_NO_SOCKET: 'No socket connection was found. Execute as Root',
    lib.UP_FORCE_BOOT_ERROR: 'Could not force Boot mode',

    lib.SOEM_EC_ERR_TYPE_SDO_ERROR: 'EtherCAT Error. SDO error',
    lib.SOEM_EC_ERR_TYPE_EMERGENCY: 'EtherCAT Error. Emergency error',
    lib.SOEM_EC_ERR_TYPE_PACKET_ERROR: 'EtherCAT Error. Packet error',
    lib.SOEM_EC_ERR_TYPE_SDOINFO_ERROR: 'EtherCAT Error. SDO Info error',
    lib.SOEM_EC_ERR_TYPE_FOE_ERROR: 'EtherCAT Error. FOE error',
    lib.SOEM_EC_ERR_TYPE_FOE_BUF2SMALL: 'EtherCAT Error. Buffer too small error',
    lib.SOEM_EC_ERR_TYPE_FOE_PACKETNUMBER: 'EtherCAT Error. FOE Packet number error',
    lib.SOEM_EC_ERR_TYPE_SOE_ERROR: 'EtherCAT Error. SOE error',
    lib.SOEM_EC_ERR_TYPE_MBX_ERROR: 'EtherCAT Error. MBX error',
    lib.SOEM_EC_ERR_TYPE_FOE_FILE_NOTFOUND: 'EtherCAT Error. FOE File not found error',
    lib.SOEM_EC_ERR_TYPE_EOE_INVALID_RX_DATA: 'EtherCAT Error. Invalid RX Data error'
}


class EEPROM_TOOL_MODE(Enum):
    """EEPROM tool mode."""
    MODE_NONE = 0
    MODE_READBIN = 1
    MODE_READINTEL = 2
    MODE_WRITEBIN = 3
    MODE_WRITEINTEL = 4
    MODE_WRITEALIAS = 5
    MODE_INFO = 6


class EthercatNetwork(IPBNetwork):
    """Network for all EtherCAT communications.

    Args:
        interface_name (str): Interface name to be targeted.

    """
    def __init__(self, interface_name):
        super(EthercatNetwork, self).__init__()
        self.interface_name = interface_name
        """str: Interface name used in the network settings."""

    def load_firmware(self, fw_file, target=1, boot_in_app=True):
        """Loads a given firmware file to a target.

        .. warning::
            Choose the ``boot_in_app`` flag accordingly to your
            servo specifications otherwise the servo could enter
            a blocking state.

        .. warning ::
            It is needed to disconnect the drive(:func:`disconnect_from_slave`)
            after loading the firmware since the `Servo` object's data will
            become obsolete.

        Args:
            target (int): Targeted node ID to be loaded.
            fw_file (str): Path to the firmware file.
            boot_in_app (bool): If summit series -> True.
                                If capitan series -> False.
                                If custom device -> Contact manufacturer.

        Raises:
            ILFirmwareLoadError: The firmware load process fails
                with an error message.

        """
        if not os.path.isfile(fw_file):
            raise FileNotFoundError('Could not find {}.'.format(fw_file))

        self._cffi_network = ffi.new('il_net_t **')
        _interface_name = cstr(self.interface_name) \
            if self.interface_name else ffi.NULL
        _fw_file = cstr(fw_file) if fw_file else ffi.NULL
        r = lib.il_net_update_firmware(
            self._cffi_network, _interface_name, target, _fw_file, boot_in_app)
        if r < 0:
            error_msg = 'Error updating firmware. Error code: {}'.format(r)
            if r in FIRMWARE_UPDATE_ERROR:
                error_msg = FIRMWARE_UPDATE_ERROR[r]
            raise ILFirmwareLoadError(error_msg)

    def _read_eeprom(self, eeprom_file, slave, file_format):
        """Reads the EEPROM.

        Args:
            eeprom_file (str): Path to the EEPROM file.
            slave (int): Target slave number to be connected
            file_format (EEPROM_FILE_FORMAT): EEPROM tool mode.

        Raises:
            ILError: In case the operation does not succeed.

        """
        if file_format not in EEPROM_FILE_FORMAT:
            raise ILError('Invalid file format')
        if file_format == EEPROM_FILE_FORMAT.BINARY:
            mode = EEPROM_TOOL_MODE.MODE_READBIN.value
        else:
            mode = EEPROM_TOOL_MODE.MODE_READINTEL.value

        self._cffi_network = ffi.new('il_net_t **')
        _interface_name = cstr(self.interface_name) if self.interface_name else ffi.NULL
        _eeprom_file = cstr(eeprom_file) if eeprom_file else ffi.NULL

        r = lib.il_net_eeprom_tool(
            self._cffi_network, _interface_name, slave, mode, _eeprom_file)
        if r < 0:
            raise ILError('Failed reading EEPROM file.')

    def _write_eeprom(self, eeprom_file, slave, file_format):
        """Loads an EEPROM file to use as configuration.

        Args:
            eeprom_file (str): Path to the EEPROM file.
            slave (int): Target slave number to be connected
            file_format (EEPROM_FILE_FORMAT): EEPROM tool mode.

        Raises:
            ILError: In case the operation does not succeed.

        """
        if file_format not in EEPROM_FILE_FORMAT:
            raise ILError('Invalid file format')
        if file_format == EEPROM_FILE_FORMAT.BINARY:
            mode = EEPROM_TOOL_MODE.MODE_WRITEBIN.value
        else:
            mode = EEPROM_TOOL_MODE.MODE_WRITEINTEL.value

        self._cffi_network = ffi.new('il_net_t **')
        _interface_name = cstr(self.interface_name) if self.interface_name else ffi.NULL
        _eeprom_file = cstr(eeprom_file) if eeprom_file else ffi.NULL

        r = lib.il_net_eeprom_tool(
            self._cffi_network, _interface_name, slave, mode, _eeprom_file)
        if r < 0:
            raise ILError('Failed writing EEPROM file.')

    def _write_eeprom_alias(self, eeprom_file, slave):
        """Writes the configuration station alias.

        Args:
            eeprom_file (str): Path to the EEPROM file.
            slave (int): Target slave number to be connected

        Raises:
            ILError: In case the operation does not succeed.

        """
        self._cffi_network = ffi.new('il_net_t **')
        _interface_name = cstr(self.interface_name) if self.interface_name else ffi.NULL
        _eeprom_file = cstr(eeprom_file) if eeprom_file else ffi.NULL

        r = lib.il_net_eeprom_tool(
            self._cffi_network, _interface_name, slave,
            EEPROM_TOOL_MODE.MODE_WRITEALIAS.value, _eeprom_file)
        if r < 0:
            raise ILError('Failed writing EEPROM alias.')

    def scan_slaves(self):
        """Scan all the slaves connected in the network.

        Returns:
            list: List of number of slaves connected to the network.

        """
        _interface_name = cstr(self.interface_name) \
            if self.interface_name else ffi.NULL

        number_slaves = lib.il_net_num_slaves_get(_interface_name)
        return [slave + 1 for slave in range(number_slaves)]

    def connect_to_slave(self, target=1, dictionary="", use_eoe_comms=1,
                         reconnection_retries=DEFAULT_MESSAGE_RETRIES,
                         reconnection_timeout=DEFAULT_MESSAGE_TIMEOUT,
                         servo_status_listener=True,
                         net_status_listener=True):
        """Connect a slave through an EtherCAT connection.

        Args:
            target (int): Number of the target slave.
            dictionary (str): Path to the dictionary to be loaded.
            use_eoe_comms (int): Specify which architecture is the target based on.
            reconnection_retries (int): Number of reconnection retried before declaring
                a connected or disconnected stated.
            reconnection_timeout (int): Time in ms of the reconnection timeout.
            servo_status_listener (bool): Toggle the listener of the servo for
                its status, errors, faults, etc.
            net_status_listener (bool): Toggle the listener of the network
                status, connection and disconnection.

        Returns:
            EthercatServo: Instance of the connected servo.

        """
        servo = None
        _interface_name = cstr(self.interface_name) \
            if self.interface_name else ffi.NULL
        _dictionary = cstr(dictionary) if dictionary else ffi.NULL

        _servo = ffi.new('il_servo_t **')
        self._cffi_network = ffi.new('il_net_t **')
        r = lib.il_servo_connect_ecat(3, _interface_name, self._cffi_network,
                                      _servo, _dictionary, 1061,
                                      target, use_eoe_comms)
        if r <= 0:
            _servo = None
            self._cffi_network = None
            raise ILError('Could not find any servos connected.')
        else:
            net_ = ffi.cast('il_net_t *', self._cffi_network[0])
            servo_ = ffi.cast('il_servo_t *', _servo[0])
            servo = EthercatServo(servo_, net_, target, dictionary,
                                  servo_status_listener)
            self._cffi_network = net_
            self.servos.append(servo)

        if net_status_listener:
            self.start_status_listener()

        self.set_reconnection_retries(reconnection_retries)
        self.set_recv_timeout(reconnection_timeout)

        return servo

    def disconnect_from_slave(self, servo):
        """Disconnects the slave from the network.

        Args:
            servo (EthernetServo): Instance of the servo connected.

        """
        # TODO: This stops all connections no only the target servo.
        if servo in self.servos:
            self.servos.remove(servo)
        self.stop_status_listener()
        lib.il_servo_destroy(servo._cffi_servo)
        r = lib.il_net_master_stop(self._cffi_network)
        lib.il_net_destroy(self._cffi_network)
        self._cffi_network = None
        if r < 0:
            raise ILError('Error disconnecting the drive. '
                          'Return code: {}'.format(r))

    @property
    def protocol(self):
        """NET_PROT: Obtain network protocol."""
        return NET_PROT.ECAT
