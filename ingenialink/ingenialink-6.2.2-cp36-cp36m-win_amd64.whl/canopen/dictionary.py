import xml.etree.ElementTree as ET
from ..dictionary import Dictionary
from ..constants import SINGLE_AXIS_MINIMUM_SUBNODES
from .register import CanopenRegister, REG_ACCESS, REG_DTYPE
from ingenialink.utils._utils import *
from .._ingenialink import lib


class CanopenCategories:
    """Contains all categories from a CANopen Dictionary.

    Args:
        dict_ (str): Path to the Ingenia dictionary.

    """

    def __init__(self, dict_):
        self._dict = dict_
        self._cat_ids = []
        self._categories = {}  # { cat_id : label }

        self.load_cat_ids()

    def load_cat_ids(self):
        """Load category IDs from dictionary."""
        with open(self._dict, 'r', encoding='utf-8') as xml_file:
            tree = ET.parse(xml_file)
        root = tree.getroot()

        for element in root.findall('./Body/Device/Categories/Category'):
            self._cat_ids.append(element.attrib['id'])
            self._categories[element.attrib['id']] = {
                'en_US': element.find('./Labels/Label').text
            }

    @property
    def category_ids(self):
        """list: Category IDs."""
        return self._cat_ids

    def labels(self, cat_id):
        """Obtain labels for a certain category ID.

        Returns:
            dict: Labels dictionary.

        """
        return self._categories[cat_id]


class CanopenErrors:
    """Errors for the CANopen dictionary.

    Args:
        dict_ (str): Path to the Ingenia dictionary.

    """

    def __init__(self, dict_):
        self._dict = dict_
        self._errors = {}  # { cat_id : label }

        self.load_errors()

    def load_errors(self):
        """Load errors from dictionary."""
        with open(self._dict, 'r', encoding='utf-8') as xml_file:
            tree = ET.parse(xml_file)
        root = tree.getroot()

        for element in root.findall('./Body/Errors/Error'):
            label = element.find('./Labels/Label')
            self._errors[int(element.attrib['id'], 16)] = [
                element.attrib['id'],
                element.attrib['affected_module'],
                element.attrib['error_type'].capitalize(),
                label.text
            ]

    @property
    def errors(self):
        """dict: Errors dictionary."""
        return self._errors


class CanopenDictionary(Dictionary):
    """Contains all registers and information of a CANopen dictionary.

    Args:
        dictionary_path (str): Path to the Ingenia dictionary.

    """

    def __init__(self, dictionary_path):
        super(CanopenDictionary, self).__init__(dictionary_path)
        self.version = '1'
        self.categories = None
        self.subnodes = SINGLE_AXIS_MINIMUM_SUBNODES
        self.__registers = []
        self.errors = None

        self.read_dictionary()

    def read_dictionary(self):
        """Reads the dictionary file and initializes all its components."""
        with open(self.path, 'r', encoding='utf-8') as xml_file:
            tree = ET.parse(xml_file)
        root = tree.getroot()

        device = root.find('./Body/Device')

        # Subnodes
        if root.findall('./Body/Device/Axes/'):
            self.subnodes = len(root.findall('./Body/Device/Axes/Axis'))

        for _ in range(self.subnodes):
            self.__registers.append({})

        # Categories
        self.categories = CanopenCategories(self.path)

        # Errors
        self.errors = CanopenErrors(self.path)

        # Version
        version_node = root.find('.Header/Version')
        if version_node is not None:
            self.version = version_node.text

        self.firmware_version = device.attrib.get('firmwareVersion')
        product_code = device.attrib.get('ProductCode')
        if product_code is not None and product_code.isdecimal():
            self.product_code = int(product_code)
        self.part_number = device.attrib.get('PartNumber')
        revision_number = device.attrib.get('RevisionNumber')
        if revision_number is not None and revision_number.isdecimal():
            self.revision_number = int(revision_number)
        self.interface = device.attrib.get('Interface')

        if root.findall('./Body/Device/Axes/'):
            # For each axis
            for axis in root.findall('./Body/Device/Axes/Axis'):
                for register in axis.findall('./Registers/Register'):
                    self.read_register(register)
        else:
            for register in root.findall('./Body/Device/Registers/Register'):
                self.read_register(register)

        # Closing xml file
        xml_file.close()

    def read_register(self, register):
        """Reads a register from the dictionary and creates a Register instance.

        Args:
            register (Element): Register instance from the dictionary.

        """
        try:
            # Identifier
            identifier = register.attrib['id']

            # Units
            units = register.attrib['units']

            # Cyclic
            cyclic = register.attrib[
                'cyclic'] if 'cyclic' in register.attrib else "CONFIG"
            idx = int(register.attrib['address'][:6], 16)
            subidx = int("0x" + register.attrib['address'][-2:], 16)

            # Data type
            dtype = register.attrib['dtype']
            if dtype == "float":
                dtype = REG_DTYPE.FLOAT
            elif dtype == "s8":
                dtype = REG_DTYPE.S8
            elif dtype == "u8":
                dtype = REG_DTYPE.U8
            elif dtype == "u16":
                dtype = REG_DTYPE.U16
            elif dtype == "s16":
                dtype = REG_DTYPE.S16
            elif dtype == "s32":
                dtype = REG_DTYPE.S32
            elif dtype == "u32":
                dtype = REG_DTYPE.U32
            elif dtype == "str":
                dtype = REG_DTYPE.STR
            else:
                raise_err(lib.IL_EINVAL, 'Invalid data type')

            # Access
            access = register.attrib['access']
            if access == "r":
                access = REG_ACCESS.RO
            elif access == "w":
                access = REG_ACCESS.WO
            elif access == "rw":
                access = REG_ACCESS.RW
            else:
                raise_err(lib.IL_EACCESS, 'Invalid access type')

            # Subnode
            subnode = int(
                register.attrib['subnode']) if 'subnode' in register.attrib else 1

            # Storage
            storage = register.attrib[
                'storage'] if 'storage' in register.attrib else None
            cat_id = register.attrib['cat_id'] if 'cat_id' in register.attrib else None
            if 'internal_use' in register.attrib:
                internal_use = register.attrib['internal_use']
            else:
                internal_use = 0

            # Labels
            labels_elem = register.findall('./Labels/Label')
            labels = {label.attrib['lang']: label.text for label in labels_elem}

            # Range
            range_elem = register.find('./Range')
            reg_range = (None, None)
            if range_elem is not None:
                range_min = range_elem.attrib['min']
                range_max = range_elem.attrib['max']
                reg_range = (range_min, range_max)

            # Enumerations
            enums_elem = register.findall('./Enumerations/Enum')
            enums = [{enum.attrib['value']: enum.text} for enum in enums_elem]

            reg = CanopenRegister(identifier, units, cyclic, idx, subidx, dtype,
                                  access, subnode=subnode,
                                  storage=storage, reg_range=reg_range,
                                  labels=labels, enums=enums,
                                  enums_count=len(enums), cat_id=cat_id,
                                  internal_use=internal_use)
            self.__registers[int(subnode)][identifier] = reg
        except Exception as e:
            pass

    def registers(self, subnode):
        """Gets the register dictionary to the targeted subnode.

        Args:
            subnode (int): Identifier for the subnode.

        Returns:
            dict: Dictionary of all the registers for a subnode.

        """
        return self.__registers[subnode]
