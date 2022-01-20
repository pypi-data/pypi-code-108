import os

from .._ingenialink import lib, ffi
from ingenialink.constants import *
from ingenialink.exceptions import *
from ingenialink.ipb.register import *
from ingenialink.utils._utils import *
from ingenialink.register import dtype_size
from ingenialink.ipb.dictionary import IPBDictionary
from ingenialink.servo import Servo, SERVO_MODE, SERVO_STATE, SERVO_UNITS_ACC, \
    SERVO_UNITS_TORQUE, SERVO_UNITS_POS, SERVO_UNITS_VEL

import io
import numpy as np
from xml.dom import minidom
import xml.etree.ElementTree as ET

import ingenialogger
logger = ingenialogger.get_logger(__name__)

PRODUCT_ID_REGISTERS = {
    0: IPBRegister(
        identifier='', units='', subnode=0, address=0x06E1, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    ),
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06E1, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    )
}

SERIAL_NUMBER_REGISTERS = {
    0: IPBRegister(
        identifier='', units='', subnode=0, address=0x06E6, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    ),
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06E6, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    )
}

SOFTWARE_VERSION_REGISTERS = {
    0: IPBRegister(
        identifier='', units='', subnode=0, address=0x06E4, cyclic='CONFIG',
        dtype=REG_DTYPE.STR, access=REG_ACCESS.RO
    ),
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06E4, cyclic='CONFIG',
        dtype=REG_DTYPE.STR, access=REG_ACCESS.RO
    )
}

REVISION_NUMBER_REGISTERS = {
    0: IPBRegister(
        identifier='', units='', subnode=0, address=0x06E2, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    ),
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06E2, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RO
    )
}

DIST_NUMBER_SAMPLES = IPBRegister(
    identifier='', units='', subnode=0, address=0x00C4, cyclic='CONFIG',
    dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
)
DIST_DATA = IPBRegister(
    identifier='', units='', subnode=0, address=0x00B4, cyclic='CONFIG',
    dtype=REG_DTYPE.U16, access=REG_ACCESS.WO
)

STORE_COCO_ALL = IPBRegister(
    identifier='', units='', subnode=0, address=0x06DB, cyclic='CONFIG',
    dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
)

RESTORE_COCO_ALL = IPBRegister(
    identifier='', units='', subnode=0, address=0x06DC, cyclic='CONFIG',
    dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
)

STATUS_WORD = IPBRegister(
    identifier='', units='', subnode=1, address=0x0011, cyclic='CONFIG',
    dtype=REG_DTYPE.U16, access=REG_ACCESS.RW
)

STORE_MOCO_ALL_REGISTERS = {
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06DB, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
    ),
    2: IPBRegister(
        identifier='', units='', subnode=2, address=0x06DB, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
    ),
    3: IPBRegister(
        identifier='', units='', subnode=3, address=0x06DB, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW
    )
}

RESTORE_MOCO_ALL_REGISTERS = {
    1: IPBRegister(
        identifier='', units='', subnode=1, address=0x06DC, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW, reg_range=None
    ),
    2: IPBRegister(
        identifier='', units='', subnode=2, address=0x06DC, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW, reg_range=None
    ),
    3: IPBRegister(
        identifier='', units='', subnode=3, address=0x06DC, cyclic='CONFIG',
        dtype=REG_DTYPE.U32, access=REG_ACCESS.RW, reg_range=None
    )
}


class IPBServo(Servo):
    """IPB Servo defines a general class for all IPB based slaves.

    Args:
        cffi_servo (CData): CData instance of the servo.
        cffi_net (CData): CData instance of the network.
        target (int, str): Target ID for the slave.
        dictionary_path (str): Path to the dictionary.

    """
    def __init__(self, cffi_servo, cffi_net, target, dictionary_path=None):
        self._cffi_servo = cffi_servo
        """CFFI instance of the servo."""
        self._cffi_network = cffi_net
        """CFFI instance of the network."""

        super(IPBServo, self).__init__(target)
        _dictionary_path = cstr(dictionary_path) if dictionary_path else ffi.NULL

        self.__dictionary = IPBDictionary(dictionary_path, self._cffi_servo)

        self.__observers_servo_state = {}
        self.__handlers_servo_state = {}
        self.__observers_emergency_state = {}

        if not hasattr(self, '_errors') or not self._errors:
            self._errors = self._get_all_errors(_dictionary_path)

        prod_name = '' if self.dictionary.part_number is None \
            else self.dictionary.part_number
        self.full_name = '{} {}'.format(prod_name, self.name)

    @staticmethod
    def _get_all_errors(dictionary):
        """Obtain all errors defined in the dictionary.

        Args:
            dictionary: Path to the dictionary file.

        Returns:
            dict: Current errors definde in the dictionary.

        """
        errors = {}
        if str(dictionary) != "<cdata 'void *' NULL>":
            tree = ET.parse(dictionary)
            for error in tree.iter("Error"):
                label = error.find(".//Label")
                id = int(error.attrib['id'], 0)
                errors[id] = [
                    error.attrib['id'],
                    error.attrib['affected_module'],
                    error.attrib['error_type'].capitalize(),
                    label.text
                ]
        return errors

    def _get_reg(self, reg, subnode):
        """Validates a register.

        Args:
            reg (IPBRegister): Targeted register to validate.
            subnode (int): Subnode for the register.

        Returns:
            IPBRegister: Instance of the desired register from the dictionary.

        Raises:
            ILIOError: If the dictionary is not loaded.
            ILWrongRegisterError: If the register has invalid format.

        """
        if isinstance(reg, IPBRegister):
            return reg

        elif isinstance(reg, str):
            _dict = self.dictionary
            if not _dict:
                raise ValueError('No dictionary loaded')
            if reg not in _dict.registers(subnode):
                raise_err(lib.IL_REGNOTFOUND, 'Register not found ({})'.format(reg))
            return _dict.registers(subnode)[reg]
        else:
            raise TypeError('Invalid register')

    def raw_read(self, reg, subnode=1):
        """Raw read from servo.

        Args:
            reg (IPBRegister): Register.

        Returns:
            int: Otained value

        Raises:
            TypeError: If the register type is not valid.

        """
        return self.read(reg, subnode=subnode)

    def read(self, reg, subnode=1):
        """Read from servo.

        Args:
            reg (str, Register): Register.

        Returns:
            float: Obtained value

        Raises:
            TypeError: If the register type is not valid.

        """
        _reg = self._get_reg(reg, subnode)

        # Obtain data pointer and function to call
        t, f = self._raw_read[_reg.dtype]
        v = ffi.new(t)

        r = f(self._cffi_servo, _reg._reg, ffi.NULL, v)
        raise_err(r)

        value = self.extended_buffer if _reg.dtype == REG_DTYPE.STR else v[0]
        if isinstance(value, str):
            value = value.replace('\x00', '')
        return value

    def raw_write(self, reg, data, confirm=True, extended=0, subnode=1):
        """Raw write to servo.

        Args:
            reg (IPBRegister): Register.
            data (int): Data.
            confirm (bool, optional): Confirm write.
            extended (int, optional): Extended frame.

        Raises:
            TypeError: If any of the arguments type is not valid or
                unsupported.

        """
        self.write(reg, data, confirm, extended, subnode)

    def write(self, reg, data, confirm=True, extended=0, subnode=1):
        """Write to servo.

        Args:
            reg (IPBRegister, str): Register or UID to be written.
            data (int): Data to be written.
            confirm (bool, optional): Confirm write.
            extended (int, optional): Extended frame.

        Raises:
            TypeError: If any of the arguments type is not valid or
                unsupported.

        """
        _reg = self._get_reg(reg, subnode)

        # Auto cast floats if register is not float
        if isinstance(data, float) and _reg.dtype != REG_DTYPE.FLOAT:
            data = int(data)

        # Obtain function to call
        f = self._raw_write[_reg.dtype]

        r = f(self._cffi_servo, _reg._reg, ffi.NULL, data, confirm, extended)
        raise_err(r)

    def read_sdo(self, idx, subidx, dtype, slave=1):
        """Read SDO from network.

        Args:
            idx (int): Register index.
            subidx (int): Register subindex.
            dtype (REG_DTYPE): Register data type.
            slave (int, Optional): Identifier of an slave in the network.

        Returns:
            float: Obtained value

        Raises:
            TypeError: If the register type is not valid.

        """
        v = ffi.new('double *')
        r = lib.il_net_SDO_read(self._cffi_network, slave, idx, subidx, dtype, v)
        raise_err(r)

        return v[0]

    def read_string_sdo(self, idx, subidx, size, slave=1):
        """Read string SDO from network.

        Args:
            idx (int): Register index.
            subidx (int): Register subindex.
            size (int): Size in bytes to read.
            slave (int, Optional): Identifier of an slave in the network.

        Returns:
            str: Obtained value

        Raises:
            TypeError: If the register type is not valid.

        """
        v = ffi.new("char[" + str(size) + "]")
        r = lib.il_net_SDO_read_array(self._cffi_network, slave, idx, subidx, size, v)
        raise_err(r)

        return pstr(v)

    def read_array_sdo(self, idx, subidx, length, dtype, slave=1):
        """Read array SDO from network.

        Args:
            idx (int): Register index.
            subidx (int): Register subindex.
            length (int): Array length.
            dtype (REG_DTYPE): Register data type.
            slave (int, Optional): Identifier of an slave in the network.

        Returns:
            list: Obtained value

        Raises:
            ValueError: If the register type is not valid.

        """
        enum_dtype = REG_DTYPE(dtype)
        size = dtype_size(enum_dtype)*length
        var_type = {
            REG_DTYPE.U8: "uint8_t",
            REG_DTYPE.S8: "int8_t",
            REG_DTYPE.U16: "uint16_t",
            REG_DTYPE.S16: "int16_t",
            REG_DTYPE.U32: "uint32_t",
            REG_DTYPE.S32: "int32_t",
            REG_DTYPE.U64: "uint64_t",
            REG_DTYPE.S64: "int64_t",
            REG_DTYPE.FLOAT: "float"
        }
        v = ffi.new("{}[{}]".format(var_type[enum_dtype], length))
        r = lib.il_net_SDO_read_array(self._cffi_network, slave, idx, subidx, size, v)
        raise_err(r)
        return list(v)

    def read_sdo_complete_access(self, idx, size, slave=1):
        """Read SDO complete access from network.

        Args:
            idx (int): Register index.
            size (int): Size in bytes to read.
            slave (int, Optional): Identifier of an slave in the network.

        Returns:
            bytes: Obtained value

        """
        v = ffi.new("char[" + str(size) + "]")
        r = lib.il_net_SDO_read_complete_access(
            self._cffi_network, slave, idx, size, v)
        raise_err(r)

        return b"".join(v)

    def write_sdo(self, idx, subidx, dtype, value, slave=1):
        """Write SDO from network.

        Args:
            idx (int): Register index.
            subidx (int): Register subindex.
            dtype (REG_DTYPE): Register data type.
            value (float): Value to write.
            slave (int, Optional): Identifier of an slave in the network.

        Returns:
            float: Obtained value

        Raises:
            TypeError: If the register type is not valid.

        """
        r = lib.il_net_SDO_write(self._cffi_network, slave, idx, subidx, dtype, value)
        raise_err(r)

    def destroy(self):
        """Destroy servo instance.

        Returns:
            int: Result code.

        """
        return lib.il_servo_destroy(self._cffi_servo)

    def reset(self):
        """Reset servo.

        Notes:
            You may need to reconnect the network after reset.

        """
        r = lib.il_servo_reset(self._cffi_servo)
        raise_err(r)

    def get_state(self, subnode=1):
        """Obtain state of the servo.

        Args:
            subnode (int, optional): Subnode.

        Returns:
            tuple: Servo state and state flags.

        """
        state = ffi.new('il_servo_state_t *')
        flags = ffi.new('int *')

        lib.il_servo_state_get(self._cffi_servo, state, flags, subnode)

        return SERVO_STATE(state[0]), flags[0]

    def enable(self, subnode=1, timeout=DEFAULT_PDS_TIMEOUT):
        """Enable PDS.

        Args:
            subnode (int, optional): Subnode.
            timeout (int): Timeout in milliseconds.

        Raises:
            ILTimeoutError: The servo could not be enabled due to timeout.
            ILError: The servo could not be enabled.

        """
        r = lib.il_servo_enable(self._cffi_servo, subnode, timeout)
        raise_err(r)

    def disable(self, subnode=1, timeout=DEFAULT_PDS_TIMEOUT):
        """Disable PDS.

        Args:
            subnode (int): Subnode of the drive.
            timeout (int): Timeout in milliseconds.

        Raises:
            ILTimeoutError: The servo could not be disabled due to timeout.
            ILError: Failed to disable PDS.

        """
        r = lib.il_servo_disable(self._cffi_servo, subnode, timeout)
        raise_err(r)

    def fault_reset(self, subnode=1, timeout=DEFAULT_PDS_TIMEOUT):
        """Fault reset.

        Args:
            subnode (int, optional): Subnode.
            timeout (int): Timeout in milliseconds.

        Raises:
            ILTimeoutError: The servo could not be reset due to timeout.
            ILError: Failed to fault reset.

        """
        r = lib.il_servo_fault_reset(self._cffi_servo, subnode, timeout)
        raise_err(r)

    def switch_on(self, timeout=2.):
        """Switch on PDS.

        This function switches on the PDS but it does not enable the motor.
        For most application cases, you should only use the `enable`
        function.

        Args:
            subnode (int): Subnode of the drive.
            timeout (int): Timeout in milliseconds.

        Raises:
            ILTimeoutError: The servo could not be disabled due to timeout.
            ILError: Failed to disable PDS.

        """
        r = lib.il_servo_switch_on(self._cffi_servo, to_ms(timeout))
        raise_err(r)

    def homing_start(self):
        """Start the homing procedure."""
        r = lib.il_servo_homing_start(self._cffi_servo)
        raise_err(r)

    def homing_wait(self, timeout):
        """Wait until homing completes.

        Notes:
            The homing itself has a configurable timeout. The timeout given
            here is purely a 'communications' timeout, e.g. it could happen
            that the statusword change is never received. This timeout
            should be >= than the programmed homing timeout.

        Args:
            timeout (int, float): Timeout (s).

        """
        r = lib.il_servo_homing_wait(self._cffi_servo, to_ms(timeout))
        raise_err(r)

    def store_parameters(self, subnode=None):
        """Store all the current parameters of the target subnode.

        Args:
            subnode (int): Subnode of the axis. `None` by default which stores
            all the parameters.

        Raises:
            ILError: Invalid subnode.
            ILObjectNotExist: Failed to write to the registers.

        """
        if subnode is None:
            # Store all
            r = 0
            try:
                self.write(reg=STORE_COCO_ALL,
                           data=PASSWORD_STORE_ALL,
                           subnode=0)
                logger.info('Store all successfully done.')
            except Exception:
                logger.warning('Store all COCO failed. Trying MOCO...')
                r = -1
            if r < 0:
                if self.dictionary.subnodes > SINGLE_AXIS_MINIMUM_SUBNODES:
                    # Multiaxis
                    for dict_subnode in self.dictionary.subnodes:
                        self.write(reg=STORE_MOCO_ALL_REGISTERS[dict_subnode],
                                   data=PASSWORD_STORE_ALL,
                                   subnode=dict_subnode)
                        logger.info('Store axis {} successfully done.'.format(
                            dict_subnode))
                else:
                    # Single axis
                    self.write(reg=STORE_MOCO_ALL_REGISTERS[1],
                               data=PASSWORD_STORE_ALL,
                               subnode=1)
                    logger.info('Store all successfully done.')
        elif subnode == 0:
            # Store only subnode 0
            self.write(reg=STORE_COCO_ALL,
                       data=PASSWORD_STORE_RESTORE_SUB_0,
                       subnode=subnode)
            logger.info('Store subnode 0 successfully done.')
        elif subnode > 0 and subnode in STORE_MOCO_ALL_REGISTERS:
            # Store axis
            self.write(reg=STORE_MOCO_ALL_REGISTERS[subnode],
                       data=PASSWORD_STORE_ALL,
                       subnode=subnode)
            logger.info('Store axis {} successfully done.'.format(subnode))
        else:
            raise ILError('Invalid subnode.')
        sleep(1.5)

    def restore_parameters(self, subnode=None):
        """Restore all the current parameters of all the slave to default.

        .. note::
            The drive needs a power cycle after this
            in order for the changes to be properly applied.

        Args:
            subnode (int): Subnode of the axis. `None` by default which restores
            all the parameters.

        Raises:
            ILError: Invalid subnode.
            ILObjectNotExist: Failed to write to the registers.

        """
        if subnode is None:
            # Restore All
            self.write(reg=RESTORE_COCO_ALL,
                       data=PASSWORD_RESTORE_ALL,
                       subnode=0)
            logger.info('Restore all successfully done.')
        elif subnode == 0:
            # Restore only axis 0
            self.write(reg=RESTORE_COCO_ALL,
                       data=PASSWORD_STORE_RESTORE_SUB_0,
                       subnode=0)
            logger.info('Restore subnode 0 successfully done.')
        elif subnode > 0 and subnode in RESTORE_MOCO_ALL_REGISTERS:
            # Restore axis
            self.write(reg=RESTORE_MOCO_ALL_REGISTERS[subnode],
                       data=PASSWORD_RESTORE_ALL,
                       subnode=subnode)
            logger.info('Restore subnode {} successfully done.'.format(subnode))
        else:
            raise ILError('Invalid subnode.')
        sleep(1.5)

    def is_alive(self):
        """Checks if the servo responds to a reading a register.

        Returns:
            bool: Return code with the result of the read.
        """
        _is_alive = True
        try:
            self.read(STATUS_WORD)
        except ILError as e:
            _is_alive = True
            logger.error(e)
        return _is_alive

    def _store_comm(self):
        """Store all servo current communications to the NVM."""
        r = lib.il_servo_store_comm(self._cffi_servo)
        raise_err(r)

    def _store_app(self):
        """Store all servo current application parameters to the NVM."""
        r = lib.il_servo_store_app(self._cffi_servo)
        raise_err(r)

    def replace_dictionary(self, dictionary):
        """Deletes and creates a new instance of the dictionary.

        Args:
            dictionary (str): Dictionary.

        """
        r = lib.il_servo_dict_load(self._cffi_servo, cstr(dictionary))
        if not hasattr(self, '_errors') or not self._errors:
            self._errors = self._get_all_errors(dictionary)
        raise_err(r)
        self.__dictionary = IPBDictionary(dictionary, self._cffi_servo)

    @staticmethod
    def __update_single_axis_dict(registers_category, registers, subnode):
        """Looks for matches through all the registers' subnodes with the
        given subnode and removes the ones that do not match. It also cleans
        up the registers leaving only paramount information.

        Args:
            registers_category (Element): Registers element containing all registers.
            registers (list): List of registers in the dictionary.
            subnode (int): Subnode to keep in the dictionary.

        Returns:

        """
        for register in registers:
            if subnode is not None and register.attrib['subnode'] != str(
                    subnode) and subnode >= 0 and register in registers_category:
                registers_category.remove(register)
            cleanup_register(register)

    @staticmethod
    def __update_multiaxis_dict(device, axes_category, list_axis, subnode):
        """Looks for matches through the subnode of each axis and
        removes all the axes that did not match the search. It also
        cleans up all the registers leaving only paramount information.

        Args:
            device (Element): Device element containing all the dictionary info.
            axes_category (Element): Axes element containing all the axis.
            list_axis (list): List of all the axis in the dictionary.
            subnode (int): Subnode to keep in the dictionary.

        """
        for axis in list_axis:
            registers_category = axis.find('./Registers')
            registers = registers_category.findall('./Register')
            if subnode is not None and axis.attrib['subnode'] == str(subnode):
                for register in registers:
                    cleanup_register(register)
                device.append(registers_category)
                device.remove(axes_category)
                break
            for register in registers:
                cleanup_register(register)

    def save_configuration(self, config_file, subnode=None):
        """Read all dictionary registers content and save it to a
        new dictionary.

        Args:
            config_file (str): Dictionary.
            subnode (int): Target subnode.

        """
        if subnode is not None and (not isinstance(subnode, int) or subnode < 0):
            raise ILError('Invalid subnode')
        prod_code, rev_number = get_drive_identification(self, subnode)

        r = lib.il_servo_dict_storage_read(self._cffi_servo)
        raise_err(r)

        self.dictionary.save(config_file)

        tree = ET.parse(config_file)
        xml_data = tree.getroot()

        body = xml_data.find('Body')
        device = xml_data.find('Body/Device')
        categories = xml_data.find('Body/Device/Categories')
        errors = xml_data.find('Body/Errors')

        if 'ProductCode' in device.attrib and prod_code is not None:
            device.attrib['ProductCode'] = str(prod_code)
        if 'RevisionNumber' in device.attrib and rev_number is not None:
            device.attrib['RevisionNumber'] = str(rev_number)

        registers_category = xml_data.find('Body/Device/Registers')
        if registers_category is None:
            # Multiaxis dictionary
            axes_category = xml_data.find('Body/Device/Axes')
            list_axis = xml_data.findall('Body/Device/Axes/Axis')
            self.__update_multiaxis_dict(device, axes_category, list_axis, subnode)
        else:
            # Single axis dictionary
            registers = xml_data.findall('Body/Device/Registers/Register')
            self.__update_single_axis_dict(registers_category, registers, subnode)

        device.remove(categories)
        body.remove(errors)

        image = xml_data.find('./DriveImage')
        if image is not None:
            xml_data.remove(image)

        xmlstr = minidom.parseString(ET.tostring(xml_data)).toprettyxml(
            indent="  ", newl='')

        config_file = io.open(config_file, "w", encoding='utf8')
        config_file.write(xmlstr)
        config_file.close()

    def load_configuration(self, config_file, subnode=None):
        """Load configuration from dictionary file to the servo drive.

        Args:
            config_file (str): Dictionary.
            subnode (int): Target subnode.

        """
        if not os.path.isfile(config_file):
            raise FileNotFoundError('Could not find {}.'.format(config_file))
        if subnode is not None and (not isinstance(subnode, int) or subnode < 0):
            raise ILError('Invalid subnode')
        if subnode is None:
            subnode = -1
        r = lib.il_servo_dict_storage_write(self._cffi_servo, cstr(config_file),
                                            subnode)
        if not hasattr(self, '_errors') or not self._errors:
            self._errors = self._get_all_errors(config_file)
        raise_err(r)

    def reload_errors(self, dictionary):
        """Force to reload all dictionary errors.

        Args:
            dictionary (str): Dictionary.

        """
        self._errors = self._get_all_errors(dictionary)

    def emcy_subscribe(self, cb):
        """Subscribe to emergency messages.

        Args:
            cb: Callback

        Returns:
            int: Assigned slot.

        """
        cb_handle = ffi.new_handle(cb)

        slot = lib.il_servo_emcy_subscribe(
            self._cffi_servo, lib._on_emcy_cb, cb_handle)
        if slot < 0:
            raise_err(slot)

        self.__observers_emergency_state[slot] = cb_handle

        return slot

    def emcy_unsubscribe(self, slot):
        """Unsubscribe from emergency messages.

        Args:
            slot (int): Assigned slot when subscribed.

        """
        lib.il_servo_emcy_unsubscribe(self._cffi_servo, slot)

        del self.__observers_emergency_state[slot]

    def subscribe_to_status(self, callback):
        """Subscribe to state changes.

        Args:
            callback: Callback

        """
        if callback in self.__observers_servo_state.values():
            logger.info('Callback already subscribed.')
            return

        cb_handle = ffi.new_handle(callback)

        slot = lib.il_servo_state_subscribe(
            self._cffi_servo, lib._on_state_change_cb, cb_handle)
        if slot < 0:
            raise_err(slot)

        self.__observers_servo_state[slot] = callback
        self.__handlers_servo_state[slot] = cb_handle

    def unsubscribe_from_status(self, callback):
        """Unsubscribe from state changes.

        Args:
            callback (function): Callback function.

        """
        if callback not in self.__observers_servo_state.values():
            logger.info('Callback not subscribed.')
            return
        for slot, cb in self.__observers_servo_state.items():
            if cb == callback:
                lib.il_servo_state_unsubscribe(self._cffi_servo, slot)
                del self.__observers_servo_state[slot]
                del self.__handlers_servo_state[slot]
                return

    def _state_subs_stop(self, stop):
        """Stop servo state subscriptions.

        Args:
            stop (int): start: 0, stop: 1.

        Raises:
            ILError: If the operation returns a negative error code.

        """
        r = lib.il_servo_state_subs_stop(self._cffi_servo, stop)

        if r < 0:
            raise ILError('Failed toggling servo state subscriptions.')

    def start_status_listener(self):
        """Start listening for servo status events (SERVO_STATE)."""
        self._state_subs_stop(0)

    def stop_status_listener(self):
        """Stop listening for servo status events (SERVO_STATE)."""
        self._state_subs_stop(1)

    def disturbance_write_data(self, channels, dtypes, data_arr):
        """Write disturbance data.

        Args:
            channels (int or list of int): Channel identifier.
            dtypes (int or list of int): Data type.
            data_arr (list or list of list): Data array.

        """
        if not isinstance(channels, list):
            channels = [channels]
        if not isinstance(dtypes, list):
            dtypes = [dtypes]
        if not isinstance(data_arr[0], list):
            data_arr = [data_arr]
        num_samples = len(data_arr[0])
        self.write(DIST_NUMBER_SAMPLES, num_samples, subnode=0)
        sample_size = 0
        for dtype_val in dtypes:
            sample_size += dtype_size(dtype_val)
        samples_for_write = DIST_FRAME_SIZE // sample_size
        number_writes = num_samples // samples_for_write
        rest_samples = num_samples % samples_for_write
        for i in range(number_writes):
            for index, channel in enumerate(channels):
                self.disturbance_channel_data(
                    channel,
                    dtypes[index],
                    data_arr[index][i * samples_for_write:(i + 1) * samples_for_write])
            self.disturbance_data_size = sample_size * samples_for_write
            self.write(DIST_DATA, sample_size * samples_for_write, False, 1, subnode=0)
        for index, channel in enumerate(channels):
            self.disturbance_channel_data(
                channel,
                dtypes[index],
                data_arr[index][number_writes * samples_for_write:num_samples])
        self.disturbance_data_size = rest_samples * sample_size
        self.write(DIST_DATA, rest_samples * sample_size, False, 1, subnode=0)

    def wait_reached(self, timeout):
        """Wait until the servo does a target reach.

        Args:
            timeout (int, float): Timeout (s).

        """
        r = lib.il_servo_wait_reached(self._cffi_servo, to_ms(timeout))
        raise_err(r)

    def units_update(self):
        """Update units scaling factors.

        Notes:
            This must be called if any encoder parameter, rated torque or
            pole pitch are changed, otherwise, the readings conversions
            will not be correct.

        """
        r = lib.il_servo_units_update(self._cffi_servo)
        raise_err(r)

    def units_factor(self, reg):
        """Obtain units scale factor for the given register.

        Args:
            reg (IPBRegister): Register.

        Returns:
            float: Scale factor for the given register.

        """
        return lib.il_servo_units_factor(self._cffi_servo, reg._reg)

    def monitoring_channel_data(self, channel, dtype):
        """Obtain processed monitoring data of a channel.

        Args:
            channel (int): Identity channel number.
            dtype (REG_DTYPE): Data type of the register to map.

        Returns:
            array: Monitoring data.

        """
        data_arr = []
        size = int(self.monitoring_data_size)
        bytes_per_block = self.monitoring_get_bytes_per_block()
        if dtype == REG_DTYPE.U16:
            data_arr = lib.il_net_monitoring_channel_u16(self._cffi_network, channel)
        elif dtype == REG_DTYPE.S16:
            data_arr = lib.il_net_monitoring_channel_s16(self._cffi_network, channel)
        elif dtype == REG_DTYPE.U32:
            data_arr = lib.il_net_monitoring_channel_u32(self._cffi_network, channel)
        elif dtype == REG_DTYPE.S32:
            data_arr = lib.il_net_monitoring_channel_s32(self._cffi_network, channel)
        elif dtype == REG_DTYPE.FLOAT:
            data_arr = lib.il_net_monitoring_channel_flt(self._cffi_network, channel)
        ret_arr = []
        for i in range(0, int(size / bytes_per_block)):
            ret_arr.append(data_arr[i])
        return ret_arr

    def monitoring_remove_all_mapped_registers(self):
        """Remove all monitoring mapped registers.

        Returns:
            int: Result code.

        """
        return lib.il_net_remove_all_mapped_registers(self._cffi_network)

    def monitoring_set_mapped_register(self, channel, address, subnode, dtype, size):
        """Set monitoring mapped register.

        Args:
            channel (int): Identity channel number.
            reg_idx (int): Register address to map.
            dtype (REG_DTYPE): Data type of the register to map.

        Returns:
            int: Result code.

        """
        return lib.il_net_set_mapped_register(self._cffi_network, channel,
                                              address, subnode, dtype, size)

    def monitoring_get_num_mapped_registers(self):
        """Obtain the number of mapped registers.

        Returns:
            int: Actual number of mapped registers.

        """
        return lib.il_net_num_mapped_registers_get(self._cffi_network)

    def monitoring_enable(self):
        """Enable monitoring process.

        Returns:
            int: Result code.

        """
        return lib.il_net_enable_monitoring(self._cffi_network)

    def monitoring_disable(self):
        """Disable monitoring process.

        Returns:
            int: Result code.

        """
        return lib.il_net_disable_monitoring(self._cffi_network)

    def disturbance_enable(self):
        """Enable disturbance process.

        Returns:
            int: Result code.

        """
        return lib.il_net_enable_disturbance(self._cffi_network)

    def disturbance_disable(self):
        """Disable disturbance process.

        Returns:
            int: Result code.

        """
        return lib.il_net_disable_disturbance(self._cffi_network)

    def monitoring_remove_data(self):
        """Remove monitoring data.

        Returns:
            int: Result code.

        """
        return lib.il_net_monitoring_remove_data(self._cffi_network)

    def disturbance_remove_data(self):
        """Remove disturbance data.

        Returns:
            int: Result code.

        """
        return lib.il_net_disturbance_remove_data(self._cffi_network)

    def monitoring_read_data(self):
        """Obtain processed monitoring data.

        Returns:
            array: Actual processed monitoring data.

        """
        return lib.il_net_read_monitoring_data(self._cffi_network)

    def monitoring_get_bytes_per_block(self):
        """Obtain Bytes x Block configured.

        Returns:
            int: Actual number of Bytes x Block configured.

        """
        return lib.il_net_monitornig_bytes_per_block_get(self._cffi_network)

    def disturbance_channel_data(self, channel, dtype, data_arr):
        """Send disturbance data.

        Args:
            channel (int): Identity channel number.
            dtype (REG_DTYPE): Data type of the register mapped.
            data_arr (array): Data that will be sent to the drive.

        Returns:
            int: Return code.

        """
        if dtype == REG_DTYPE.U16:
            lib.il_net_disturbance_data_u16_set(self._cffi_network, channel, data_arr)
        elif dtype == REG_DTYPE.S16:
            lib.il_net_disturbance_data_s16_set(self._cffi_network, channel, data_arr)
        elif dtype == REG_DTYPE.U32:
            lib.il_net_disturbance_data_u32_set(self._cffi_network, channel, data_arr)
        elif dtype == REG_DTYPE.S32:
            lib.il_net_disturbance_data_s32_set(self._cffi_network, channel, data_arr)
        elif dtype == REG_DTYPE.FLOAT:
            lib.il_net_disturbance_data_flt_set(self._cffi_network, channel, data_arr)
        return 0

    def disturbance_remove_all_mapped_registers(self):
        """Remove all disturbance mapped registers.

        Returns:
            int: Return code.

        """
        return lib.il_net_disturbance_remove_all_mapped_registers(self._cffi_network)

    def disturbance_set_mapped_register(self, channel, address, subnode, dtype, size):
        """Set disturbance mapped register.

        Args:
            channel (int): Identity channel number.
            address (int): Register address to map.
            dtype (REG_DTYPE): Data type of the register to map.

        Returns:
            int: Return code.

        """
        return lib.il_net_disturbance_set_mapped_register(self._cffi_network, channel,
                                                          address, subnode, dtype, size)

    def __read_coco_moco_register(self, register_coco, register_moco):
        """Reads the COCO register and if it does not exist,
        reads the MOCO register

        Args:
            register_coco (IPBRegister): COCO Register to be read.
            register_moco (IPBRegister: MOCO Register to be read.

        Returns:
            int: Read value of the register.

        """
        try:
            return self.read(register_coco, subnode=0)
        except ILError:
            pass

        try:
            return self.read(register_moco, subnode=1)
        except ILError:
            pass

    @property
    def dictionary(self):
        """Obtain dictionary of the servo."""
        return self.__dictionary

    @property
    def info(self):
        """dict: Servo information."""
        serial_number = self.__read_coco_moco_register(
            SERIAL_NUMBER_REGISTERS[0], SERIAL_NUMBER_REGISTERS[1])
        product_code = self.__read_coco_moco_register(
            PRODUCT_ID_REGISTERS[0], PRODUCT_ID_REGISTERS[1])
        revision_number = self.__read_coco_moco_register(
            REVISION_NUMBER_REGISTERS[0], REVISION_NUMBER_REGISTERS[1])
        sw_version = None
        hw_variant = 'A'

        return {
            'name': self.name,
            'serial_number': serial_number,
            'firmware_version': sw_version,
            'product_code': product_code,
            'revision_number': revision_number,
            'hw_variant': hw_variant
        }

    @property
    def units_torque(self):
        """SERVO_UNITS_TORQUE: Torque units."""
        return SERVO_UNITS_TORQUE(lib.il_servo_units_torque_get(self._cffi_servo))

    @units_torque.setter
    def units_torque(self, units):
        lib.il_servo_units_torque_set(self._cffi_servo, units.value)

    @property
    def units_pos(self):
        """SERVO_UNITS_POS: Position units."""
        return SERVO_UNITS_POS(lib.il_servo_units_pos_get(self._cffi_servo))

    @units_pos.setter
    def units_pos(self, units):
        lib.il_servo_units_pos_set(self._cffi_servo, units.value)

    @property
    def units_vel(self):
        """SERVO_UNITS_VEL: Velocity units."""
        return SERVO_UNITS_VEL(lib.il_servo_units_vel_get(self._cffi_servo))

    @units_vel.setter
    def units_vel(self, units):
        lib.il_servo_units_vel_set(self._cffi_servo, units.value)

    @property
    def units_acc(self):
        """SERVO_UNITS_ACC: Acceleration units."""
        return SERVO_UNITS_ACC(lib.il_servo_units_acc_get(self._cffi_servo))

    @units_acc.setter
    def units_acc(self, units):
        lib.il_servo_units_acc_set(self._cffi_servo, units.value)

    @property
    def mode(self):
        """Obtains Operation mode.

        Returns:
            SERVO_MODE: Current operation mode.

        """
        mode = ffi.new('il_servo_mode_t *')

        r = lib.il_servo_mode_get(self._cffi_servo, mode)
        raise_err(r)

        return SERVO_MODE(mode[0])

    @mode.setter
    def mode(self, mode):
        """Set Operation mode.

        Args:
            mode (SERVO_MODE): Operation mode.

        """
        r = lib.il_servo_mode_set(self._cffi_servo, mode.value)
        raise_err(r)

    @property
    def errors(self):
        """Obtain drive errors.

        Returns:
            dict: Current errors.

        """
        return self._errors

    @property
    def subnodes(self):
        """Obtain number of subnodes.

        Returns:
            int: Current number of subnodes.

        """
        return self.__dictionary.subnodes

    @property
    def ol_voltage(self):
        """Get open loop voltage.

        Returns:
            float: Open loop voltage (% relative to DC-bus, -1...1).

        """
        voltage = ffi.new('double *')
        r = lib.il_servo_ol_voltage_get(self._cffi_servo, voltage)
        raise_err(r)

        return voltage[0]

    @ol_voltage.setter
    def ol_voltage(self, voltage):
        """Set the open loop voltage (% relative to DC-bus, -1...1).

        Args:
            float: Open loop voltage.

        """
        r = lib.il_servo_ol_voltage_set(self._cffi_servo, voltage)
        raise_err(r)

    @property
    def ol_frequency(self):
        """Get open loop frequency.

        Returns:
            float: Open loop frequency (mHz).

        """
        frequency = ffi.new('double *')
        r = lib.il_servo_ol_frequency_get(self._cffi_servo, frequency)
        raise_err(r)

        return frequency[0]

    @ol_frequency.setter
    def ol_frequency(self, frequency):
        """Set the open loop frequency (mHz).

        Args:
            float: Open loop frequency.

        """
        r = lib.il_servo_ol_frequency_set(self._cffi_servo, frequency)
        raise_err(r)

    @property
    def torque(self):
        """Get actual torque.

        Returns:
            float: Actual torque.

        """
        torque = ffi.new('double *')
        r = lib.il_servo_torque_get(self._cffi_servo, torque)
        raise_err(r)

        return torque[0]

    @torque.setter
    def torque(self, torque):
        """Set the target torque.

        Args:
            float: Target torque.

        """
        r = lib.il_servo_torque_set(self._cffi_servo, torque)
        raise_err(r)

    @property
    def position(self):
        """Get actual position.

        Returns:
            float: Actual position.

        """
        position = ffi.new('double *')
        r = lib.il_servo_position_get(self._cffi_servo, position)
        raise_err(r)

        return position[0]

    @position.setter
    def position(self, pos):
        """Set the target position.

        Notes:
            Position can be either a single position, or a tuple/list
            containing in the first position the position, and in the
            second a dictionary with the following options:

                - immediate (bool): If True, the servo will go to the
                  position immediately, otherwise it will push the position
                  to the buffer. Defaults to True.
                - relative (bool): If True, the position will be taken as
                  relative, otherwise it will be taken as absolute.
                  Defaults to False.
                - sp_timeout (int, float): Set-point acknowledge
                  timeout (s).

        Args:
            pos (float): Target position.

        """
        immediate = 1
        relative = 0
        sp_timeout = lib.IL_SERVO_SP_TIMEOUT_DEF

        if isinstance(pos, (tuple, list)):
            if len(pos) != 2 or not isinstance(pos[1], dict):
                raise TypeError('Unexpected position')

            if 'immediate' in pos[1]:
                immediate = int(pos[1]['immediate'])

            if 'relative' in pos[1]:
                relative = int(pos[1]['relative'])

            if 'sp_timeout' in pos[1]:
                sp_timeout = to_ms(pos[1]['sp_timeout'])

            pos = pos[0]

        r = lib.il_servo_position_set(self._cffi_servo, pos, immediate, relative,
                                      sp_timeout)
        raise_err(r)

    @property
    def position_res(self):
        """Get position resolution.

        Returns:
            int: Position resolution (c/rev/s, c/ppitch/s).

        """
        res = ffi.new('uint32_t *')
        r = lib.il_servo_position_res_get(self._cffi_servo, res)
        raise_err(r)

        return res[0]

    @property
    def velocity(self):
        """Get actual velocity.

        Returns:
            float: Actual velocity.

        """
        velocity = ffi.new('double *')
        r = lib.il_servo_velocity_get(self._cffi_servo, velocity)
        raise_err(r)

        return velocity[0]

    @velocity.setter
    def velocity(self, velocity):
        """Set the target velocity.

        Args:
            velocity (float): Target velocity.

        """
        r = lib.il_servo_velocity_set(self._cffi_servo, velocity)
        raise_err(r)

    @property
    def velocity_res(self):
        """Get velocity resolution.

        Returns:
            int: Velocity resolution (c/rev, c/ppitch).

        """
        res = ffi.new('uint32_t *')
        r = lib.il_servo_velocity_res_get(self._cffi_servo, res)
        raise_err(r)

        return res[0]

    @property
    def monitoring_data(self):
        """Obtain monitoring data.

        Returns:
            array: Current monitoring data.

        """
        monitoring_data = lib.il_net_monitornig_data_get(self._cffi_network)
        size = int(self.monitoring_data_size / 2)
        ret_arr = []
        for i in range(0, size):
            ret_arr.append(monitoring_data[i])
        return ret_arr

    @property
    def monitoring_data_size(self):
        """Obtain monitoring data size.

        Returns:
            int: Current monitoring data size.

        """
        return lib.il_net_monitornig_data_size_get(self._cffi_network)

    @property
    def disturbance_data(self):
        """Obtain disturbance data.

        Returns:
            array: Current disturbance data.

        """
        disturbance_data = lib.il_net_disturbance_data_get(self._cffi_network)
        size = int(self.disturbance_data_size / 2)
        ret_arr = []
        for i in range(0, size):
            ret_arr.append(disturbance_data[i])
        return ret_arr

    @disturbance_data.setter
    def disturbance_data(self, value):
        """Set disturbance data.

        Args:
            value (array): Array with the disturbance to send.

        """
        disturbance_arr = value
        disturbance_arr = \
            np.pad(disturbance_arr,
                   (0, int(self.disturbance_data_size / 2) - len(value)),
                   'constant')
        lib.il_net_disturbance_data_set(self._cffi_network, disturbance_arr.tolist())

    @property
    def disturbance_data_size(self):
        """Obtain disturbance data size.

        Returns:
            int: Current disturbance data size.

        """
        return lib.il_net_disturbance_data_size_get(self._cffi_network)

    @disturbance_data_size.setter
    def disturbance_data_size(self, value):
        """Set disturbance data size.

        Args:
            value (int): Disturbance data size in bytes.

        """
        lib.il_net_disturbance_data_size_set(self._cffi_network, value)

    @property
    def extended_buffer(self):
        """Obtain extended buffer data.

        Returns:
            str: Current extended buffer data.

        """
        ext_buff = lib.il_net_extended_buffer_get(self._cffi_network)
        return pstr(ext_buff)
