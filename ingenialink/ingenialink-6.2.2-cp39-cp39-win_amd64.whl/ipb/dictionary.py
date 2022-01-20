import collections

from .._ingenialink import ffi, lib
from ingenialink.utils._utils import cstr, pstr, raise_null, raise_err

from ingenialink.ipb.register import LabelsDictionary, ipb_register_from_cffi
from ..dictionary import Dictionary, Categories
from ..constants import SINGLE_AXIS_MINIMUM_SUBNODES

import xml.etree.ElementTree as ET


class IPBSubCategories:
    """Sub-categories.

    Args:
        dict_ (CData): Ingenia dictionary instance.
        cat_id (str): Category ID.

    """

    def __init__(self, dict_, cat_id):
        self._dict = dict_
        self._cat_id = cat_id

        self._load_scat_ids()

    def _load_scat_ids(self):
        """Load sub-category IDs from dictionary."""
        scat_ids = lib.il_dict_scat_ids_get(self._dict, cstr(self._cat_id))

        self._scat_ids = []
        i = 0
        scat_id = scat_ids[0]
        while scat_id != ffi.NULL:
            self._scat_ids.append(pstr(scat_id))
            i += 1
            scat_id = scat_ids[i]

        lib.il_dict_scat_ids_destroy(scat_ids)

    def labels(self, scat_id):
        """Obtain labels for a certain sub-category identifiers.

        Returns:
            dict: Labels dictionary.

        """
        labels_p = ffi.new('il_dict_labels_t **')
        r = lib.il_dict_scat_get(self._dict, cstr(self._cat_id), cstr(scat_id),
                                 labels_p)
        raise_err(r)

        return LabelsDictionary._from_labels(labels_p[0])

    @property
    def subcategory_ids(self):
        """Obtain all sub-category identifiers.

        Returns:
            list: Sub-category identifiers.

        """
        return self._scat_ids


class IPBErrors:
    """Errors for the IPB dictionary.

    Args:
        dict_ (str): Path to the Ingenia dictionary.

    """
    def __init__(self, dict_):
        self._dict = dict_
        self._errors = {}   # { cat_id : label }

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


class IPBCategories(Categories):
    """IPB Categories for the dictionary.

    Args:
        ipb_dictionary (IPBDictionary): Ingenia dictionary instance.

    """

    def __init__(self, ipb_dictionary):
        super(IPBCategories, self).__init__(ipb_dictionary)
        self.__ipb_dictionary = ipb_dictionary
        self._load_cat_ids()

    def _load_cat_ids(self):
        """Load category IDs from dictionary."""
        cat_ids = lib.il_dict_cat_ids_get(self.__ipb_dictionary._cffi_dictionary)

        self._cat_ids = []
        i = 0
        cat_id = cat_ids[0]
        while cat_id != ffi.NULL:
            self._cat_ids.append(pstr(cat_id))
            i += 1
            cat_id = cat_ids[i]

        lib.il_dict_cat_ids_destroy(cat_ids)

    def labels(self, category_id):
        """Obtain labels for a certain category ID.

        Returns:
            dict: Labels dictionary.

        """
        labels_p = ffi.new('il_dict_labels_t **')
        r = lib.il_dict_cat_get(self.__ipb_dictionary._cffi_dictionary,
                                cstr(category_id), labels_p)
        raise_err(r)

        return LabelsDictionary._from_labels(labels_p[0])

    def subcategories(self, cat_id):
        """Obtain all sub-categories.

        Returns:
            IPBSubCategories: Sub-categories.

        """
        return IPBSubCategories(self.__ipb_dictionary._cffi_dictionary, cat_id)

    @property
    def category_ids(self):
        """Obtain all Category Identifiers.

        Returns:
            list: Category IDs.

        """
        return self._cat_ids


class IPBRegistersDictionary(collections.Mapping):
    """Registers dictionary.

    Args:
        dict_ (CData): Ingenia dictionary instance.

    """

    def __init__(self, dict_, subnode):
        self._dict = dict_
        self._subnode = subnode

        self._load_reg_ids()

    def _load_reg_ids(self):
        """Load register IDs from dictionary."""
        self._ids = []
        ids = lib.il_dict_reg_ids_get(self._dict, self._subnode)

        i = 0
        _id = ids[0]
        while _id != ffi.NULL:
            self._ids.append(pstr(_id))
            i += 1
            _id = ids[i]

        lib.il_dict_reg_ids_destroy(ids)

    def __getitem__(self, _id):
        reg_p = ffi.new('il_reg_t **')
        r = lib.il_dict_reg_get(self._dict, cstr(_id), reg_p, self._subnode)
        if r < 0:
            raise KeyError(_id)

        return ipb_register_from_cffi(reg_p[0])

    def __len__(self):
        return len(self._ids)

    def __iter__(self):
        return iter(self._ids)


class IPBDictionary(Dictionary):
    """IPB Ingenia Dictionary.

    Args:
        dictionary_path (str): Dictionary file name.
        cffi_servo (CData): CFFI instance of the current Servo.

    Raises:
        ILCreationError: If the dictionary could not be created.

    """
    def __init__(self, dictionary_path, cffi_servo):
        super(IPBDictionary, self).__init__(dictionary_path)
        self._cffi_dictionary = lib.il_servo_dict_get(cffi_servo)

        self.version = pstr(lib.il_dict_version_get(self._cffi_dictionary))
        self.subnodes = SINGLE_AXIS_MINIMUM_SUBNODES
        self.__get_subnode()

        self.__regs = []
        for subnode in range(self.subnodes):
            register = IPBRegistersDictionary(self._cffi_dictionary, subnode)
            self.__regs.append(register)
        self.categories = IPBCategories(self)
        self.errors = IPBErrors(self.path)
        self.__read_device_info()

    def __read_device_info(self):
        tree = ET.parse(self.path)
        root = tree.getroot()

        device = root.find('./Body/Device')

        self.firmware_version = device.attrib.get('firmwareVersion')
        product_code = device.attrib.get('ProductCode')
        if product_code is not None and product_code.isdecimal():
            self.product_code = int(product_code)
        self.part_number = device.attrib.get('PartNumber')
        revision_number = device.attrib.get('RevisionNumber')
        if revision_number is not None and revision_number.isdecimal():
            self.revision_number = int(revision_number)
        self.interface = device.attrib.get('Interface')

    def save(self, filename):
        """Save dictionary.

        Args:
            filename (str): Output file name/path.

        """
        r = lib.il_dict_save(self._cffi_dictionary, cstr(filename))
        raise_err(r)

    def __get_subnode(self):
        with open(self.path, 'r', encoding='utf-8') as xml_file:
            tree = ET.parse(xml_file)
        root = tree.getroot()

        if root.findall('./Body/Device/Axes/'):
            self.subnodes = len(root.findall('./Body/Device/Axes/Axis'))

    def registers(self, subnode):
        """Obtain all the registers of a subnode.

        Args:
            subnode (int): Subnode.

        Returns:
            array: List of registers.

        """
        if subnode < self.subnodes:
            return self.__regs[subnode]
