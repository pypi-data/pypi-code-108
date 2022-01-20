from enum import Enum

from .._ingenialink import ffi, lib
from ingenialink.utils._utils import *
from ..register import Register, REG_DTYPE, REG_ACCESS, REG_PHY, dtypes_ranges

import collections


def get_enums(enums, enums_count):
    """Obtain enumerations list of the register.

    Returns:
        array: Enumerations of the register.

    """
    aux_enums = []
    for i in range(enums_count):
        aux_dict = {
            'label': pstr(enums[i].label),
            'value': enums[i].value
        }
        aux_enums.append(aux_dict)
    return aux_enums


def get_range(reg_range, dtype):
    """Obtains register range.

    Returns:
        tuple: Register range (min, max), None if undefined.

    """

    if dtype == REG_DTYPE.S8:
        return reg_range.min.s8, reg_range.max.s8
    elif dtype == REG_DTYPE.U8:
        return reg_range.min.u8, reg_range.max.u8
    if dtype == REG_DTYPE.S16:
        return reg_range.min.s16, reg_range.max.s16
    elif dtype == REG_DTYPE.U16:
        return reg_range.min.u16, reg_range.max.u16
    if dtype == REG_DTYPE.S32:
        return reg_range.min.s32, reg_range.max.s32
    elif dtype == REG_DTYPE.U32:
        return reg_range.min.u32, reg_range.max.u32
    if dtype == REG_DTYPE.S64:
        return reg_range.min.s64, reg_range.max.s64
    elif dtype == REG_DTYPE.U64:
        return reg_range.min.u64, reg_range.max.u64
    elif dtype == REG_DTYPE.FLOAT:
        return reg_range.min.flt, reg_range.max.flt

    return None


def get_storage(storage, storage_valid, dtype):
    """Obtain register storage.

    Returns:
         int: Register storage.

    """
    if not storage_valid:
        return None

    if dtype == REG_DTYPE.S8:
        return storage.s8
    elif dtype == REG_DTYPE.U8:
        return storage.u8
    if dtype == REG_DTYPE.S16:
        return storage.s16
    elif dtype == REG_DTYPE.U16:
        return storage.u16
    if dtype == REG_DTYPE.S32:
        return storage.s32
    elif dtype == REG_DTYPE.U32:
        return storage.u32
    if dtype == REG_DTYPE.S64:
        return storage.s64
    elif dtype == REG_DTYPE.U64:
        return storage.u64
    elif dtype == REG_DTYPE.FLOAT:
        return storage.flt
    else:
        return None


def ipb_register_from_cffi(cffi_register):
    """Creates an IPBRegister instance from a CFFI register instance.

    Args:
        cffi_register (CData): CFFI instance of the register.

    Returns:
        IPBRegister: Instance of the newly created register.
    """
    units = None
    cyclic = None
    labels = None
    cat_id = None
    scat_id = None

    identifier = pstr(cffi_register.identifier)
    dtype = REG_DTYPE(cffi_register.dtype)
    access = REG_ACCESS(cffi_register.access)
    phy = REG_PHY(cffi_register.phy)
    address = cffi_register.address
    subnode = cffi_register.subnode
    storage = get_storage(cffi_register.storage, cffi_register.storage_valid, dtype)
    reg_range = get_range(cffi_register.range, dtype)
    enums_count = cffi_register.enums_count
    enums = get_enums(cffi_register.enums, enums_count)
    internal_use = cffi_register.internal_use

    if cffi_register.units != ffi.NULL:
        units = pstr(cffi_register.units)
    if cffi_register.cyclic != ffi.NULL:
        cyclic = pstr(cffi_register.cyclic)
    if cffi_register.cat_id != ffi.NULL:
        cat_id = pstr(cffi_register.cat_id)
    if cffi_register.scat_id != ffi.NULL:
        scat_id = pstr(cffi_register.scat_id)
    if cffi_register.labels != ffi.NULL:
        labels = LabelsDictionary._from_labels(cffi_register.labels)

    return IPBRegister(identifier, units, cyclic, dtype, access,
                       address, phy, subnode, storage, reg_range,
                       labels, enums, enums_count, cat_id, scat_id,
                       internal_use, cffi_register)


class IPBRegister(Register):
    """IPB Register.

    Args:
        identifier (str): Identifier.
        units (str): Units.
        cyclic (str): Cyclic typed register.
        dtype (REG_DTYPE): Data type.
        access (REG_ACCESS): Access type.
        address (int): Address.
        phy (REG_PHY, optional): Physical units.
        subnode (int): Subnode
        storage (any, optional): Storage.
        reg_range (tuple, optional): Range (min, max).
        labels (dict, optional): Register labels.
        enums (dict, optional): Enumeration values.
        cat_id (str, optional): Category ID.
        scat_id (str, optional): Sub-category ID.
        internal_use (int, optional): Internal use.

    Raises:
        TypeError: If any of the parameters has invalid type.

    """

    def __init__(self, identifier, units, cyclic, dtype, access, address,
                 phy=REG_PHY.NONE, subnode=1, storage=None, reg_range=None,
                 labels=None, enums=None, enums_count=0, cat_id=None, scat_id=None,
                 internal_use=0, c_reg=None):
        if labels is None:
            labels = {}
        if enums is None:
            enums = []
        super(IPBRegister, self).__init__(
            identifier, units, cyclic, dtype, access, phy, subnode, storage,
            reg_range, labels, enums, enums_count, cat_id, scat_id, internal_use)

        if not isinstance(dtype, REG_DTYPE):
            raise TypeError('Invalid data type')
        if not isinstance(access, REG_ACCESS):
            raise TypeError('Invalid access type')
        if not isinstance(phy, REG_PHY):
            raise TypeError('Invalid physical units type')
        if not cat_id and scat_id:
            raise ValueError('Sub-category requires a parent category')

        self._address = address
        self._labels = LabelsDictionary(labels)
        self.__update_range(dtype)
        if c_reg is None:
            self._reg = self.__create_c_reg()
        else:
            self._reg = c_reg

    def __repr__(self):
        """Obtain register object.

        Returns:
            str: Register information.

        """
        if self.cat_id:
            cat_info = self.cat_id
            if self.scat_id:
                cat_info += ' + ' + self.scat_id
        else:
            cat_info = 'Uncategorized'

        if self.storage and self.storage_valid:
            storage_info = self.storage
        else:
            storage_info = 'No storage'

        return '<Register: {}, {}, {}, {}, 0x{:08x}, {}{}, {}, {}, [], {},' \
               'ST: {}, [{}], {}>'.format(
                self.identifier,
                self.units,
                self.subnode,
                self.cyclic,
                self.address,
                self.dtype,
                ' ∊ ' + str(self.range) if self.range else '',
                self.access,
                self.phy,
                self.enums,
                self.enums_count,
                storage_info,
                cat_info,
                self.internal_use)

    def __create_c_reg(self):
        _reg = ffi.new('il_reg_t *')

        _reg.identifier = ffi.new("char[]", cstr(self.identifier))
        _reg.units = ffi.new("char[]", cstr(self.units))
        _reg.address = self.address
        _reg.subnode = self.subnode
        _reg.cyclic = ffi.new("char[]", cstr(self.cyclic))
        _reg.dtype = self.dtype.value
        _reg.access = self.access.value
        _reg.phy = self.phy.value
        _reg.internal_use = self.internal_use

        _reg.storage_valid = 0 if not self.storage else 1

        dtype_attr = {
            REG_DTYPE.U8: "u8",
            REG_DTYPE.S8: "s8",
            REG_DTYPE.U16: "u16",
            REG_DTYPE.S16: "s16",
            REG_DTYPE.U32: "u32",
            REG_DTYPE.S32: "s32",
            REG_DTYPE.U64: "u64",
            REG_DTYPE.S64: "s64",
            REG_DTYPE.FLOAT: "flt"
        }
        if self.dtype in REG_DTYPE and self.dtype in dtype_attr:
            attr_name = dtype_attr[self.dtype]
            if self.storage:
                if self.dtype == REG_DTYPE.FLOAT:
                    setattr(_reg.storage, attr_name, float(self.storage))
                else:
                    setattr(_reg.storage, attr_name, int(self.storage))
            setattr(_reg.range.min, attr_name, self.range[0])
            setattr(_reg.range.max, attr_name, self.range[1])
        else:
            _reg.storage_valid = 0

        _reg.labels = self._labels._labels
        _reg.enums_count = self.enums_count

        _reg.cat_id = ffi.NULL if not self.cat_id else cstr(self.cat_id)

        _reg.scat_id = ffi.NULL if not self.scat_id else cstr(self.scat_id)

        return _reg

    def __update_range(self, dtype):
        if dtype not in dtypes_ranges:
            return
        aux_range = (
            self.range[0] if self.range[0] is not None else dtypes_ranges[dtype]["min"],
            self.range[1] if self.range[1] is not None else dtypes_ranges[dtype]["max"],
        )
        self._range = aux_range

    @property
    def address(self):
        """int: Obtain register address."""
        return self._address


class LabelsDictionary(collections.MutableMapping):
    """Labels dictionary.

    Args:
        labels (dict, optional): Labels.

    Raises:
        ILCreationError: If the dictionary could not be created.

    """

    def __init__(self, labels=None):
        if labels is None:
            labels = {}
        _labels = lib.il_dict_labels_create()
        raise_null(_labels)

        self._labels = ffi.gc(_labels, lib.il_dict_labels_destroy)

        for lang, content in labels.items():
            lib.il_dict_labels_set(self._labels, cstr(lang), cstr(content))

        self._load_langs()

    @classmethod
    def _from_labels(cls, _labels):
        """Create a new class instance from an existing labels dictionary."""
        inst = cls.__new__(cls)
        inst._labels = _labels

        inst._load_langs()

        return inst

    def _load_langs(self):
        """Load languages from dictionary (cache)."""
        langs = lib.il_dict_labels_langs_get(self._labels)

        self._langs = []
        i = 0
        lang = langs[0]
        while lang != ffi.NULL:
            self._langs.append(pstr(lang))
            i += 1
            lang = langs[i]

        lib.il_dict_labels_langs_destroy(langs)

    def __getitem__(self, lang):
        content_p = ffi.new('char **')
        r = lib.il_dict_labels_get(self._labels, cstr(lang), content_p)
        raise_err(r)

        return pstr(content_p[0])

    def __setitem__(self, lang, content):
        lib.il_dict_labels_set(self._labels, cstr(lang), cstr(content))
        self._langs.append(lang)

    def __delitem__(self, lang):
        lib.il_dict_labels_del(self._labels, cstr(lang))
        self._langs.remove(lang)

    def __len__(self):
        return len(self._langs)

    def __iter__(self):
        return iter(self._langs)
