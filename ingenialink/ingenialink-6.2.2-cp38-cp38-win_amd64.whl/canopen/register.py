from .._ingenialink import lib

from ingenialink.utils._utils import *
from ingenialink.register import Register, REG_DTYPE, REG_ACCESS, REG_PHY, dtypes_ranges


class CanopenRegister(Register):
    """CANopen Register.

        Args:
            identifier (str): Identifier.
            units (str): Units.
            cyclic (str): Cyclic typed register.
            idx (int): Index of the register.
            subidx (int): Subindex of the register.
            dtype (REG_DTYPE): Data type.
            access (REG_ACCESS): Access type.
            phy (REG_PHY, optional): Physical units.
            subnode (int): Subnode.
            storage (any, optional): Storage.
            reg_range (tuple, optional): Range (min, max).
            labels (dict, optional): Register labels.
            enums (list): Enumeration registers.
            enums_count (int): Number of enumeration registers.
            cat_id (str, optional): Category ID.
            scat_id (str, optional): Sub-category ID.
            internal_use (int, optional): Internal use.

        Raises:
            TypeError: If any of the parameters has invalid type.
            ILValueError: If the register is invalid.
            ILAccessError: Register with wrong access type.

        """

    def __init__(self, identifier, units, cyclic, idx, subidx, dtype,
                 access, phy=REG_PHY.NONE, subnode=1, storage=None,
                 reg_range=(None, None), labels=None, enums=None, enums_count=0,
                 cat_id=None, scat_id=None, internal_use=0):
        if labels is None:
            labels = {}
        if enums is None:
            enums = []
        super(CanopenRegister, self).__init__(
            identifier, units, cyclic, dtype, access, phy, subnode,
            storage, reg_range, labels, enums, enums_count, cat_id,
            scat_id, internal_use)
        if not isinstance(dtype, REG_DTYPE):
            raise_err(lib.IL_EINVAL, 'Invalid data type')

        if not isinstance(access, REG_ACCESS):
            raise_err(lib.IL_EACCESS, 'Invalid access type')

        if not isinstance(phy, REG_PHY):
            raise_err(lib.IL_EINVAL, 'Invalid physical units type')

        self.__idx = idx
        self.__subidx = subidx

        if dtype in dtypes_ranges:
            if dtype == REG_DTYPE.FLOAT:
                if storage:
                    self._storage = float(storage)
                aux_range = (
                    float(reg_range[0]) if reg_range[0] else dtypes_ranges[dtype]["min"],
                    float(reg_range[1]) if reg_range[1] else dtypes_ranges[dtype]["max"],
                )
            else:
                if storage:
                    self._storage = int(storage)
                aux_range = (
                    int(reg_range[0]) if reg_range[0] else dtypes_ranges[dtype]["min"],
                    int(reg_range[1]) if reg_range[1] else dtypes_ranges[dtype]["max"],
                )
            self._range = aux_range
        else:
            self._storage_valid = 0

        aux_enums = []
        for enum in enums:
            for key, value in enum.items():
                dictionary = {
                    'label': value,
                    'value': int(key)
                }
                aux_enums.append(dictionary)

        self._enums = aux_enums

    @property
    def idx(self):
        """int: Register index."""
        return self.__idx

    @property
    def subidx(self):
        """int: Register subindex."""
        return self.__subidx

    @property
    def storage(self):
        """any: Defines if the register needs to be stored."""
        if not self.storage_valid:
            return None

        if self.dtype in [REG_DTYPE.S8, REG_DTYPE.U8, REG_DTYPE.S16,
                          REG_DTYPE.U16, REG_DTYPE.S32, REG_DTYPE.U32,
                          REG_DTYPE.S64, REG_DTYPE.U64, REG_DTYPE.FLOAT]:
            return self._storage
        else:
            return None

    @storage.setter
    def storage(self, value):
        """any: Defines if the register needs to be stored."""
        self._storage = value

    @property
    def storage_valid(self):
        return self._storage_valid

    @storage_valid.setter
    def storage_valid(self, value):
        """bool: Defines if the register storage is valid."""
        self._storage_valid = value

    @property
    def range(self):
        """tuple: Containing the minimum and the maximum values of the register."""
        if self._range:
            return self._range[0], self._range[1]
        return None

    @property
    def enums(self):
        """dict: Containing all the enums for the register."""
        if not hasattr(self, '_enums'):
            self._enums = []
            for i in range(0, self.enums_count):
                aux_dict = {
                    'label': pstr(self._enums[i].label),
                    'value': self._enums[i].value
                }
                self._enums.append(aux_dict)
        return self._enums
