#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#

import logging

import aenum
from typing import Optional
from abc import abstractmethod

logger = logging.getLogger(__name__)


# Use abstract base class instead of Mixin to inherit from `aenum.Enum` to make Sphinx
# detect inheritance correctly and create docs for derived enums, including such as
# these in `dev.supercube.constants`. With Mixin approach, module-level enum classes
# are not documented.
class StrEnumBase(aenum.Enum):
    """
    String representation-based equality and lookup.
    """

    def __eq__(self, other):
        return (self is other) or (other.__eq__(str(self)))

    # use only with aenum enums
    @classmethod
    def _missing_value_(cls, value):
        for member in cls:
            if member == value:
                return member

    def __str__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(str(self))


unique = aenum.unique


class ValueEnum(StrEnumBase):
    """
    Enum with string representation of values used as string representation, and with
    lookup and equality based on this representation.

    Attention: to avoid errors, best use together with `unique` enum decorator.
    """

    def __str__(self):
        return str(self.value)


class NameEnum(StrEnumBase):
    """
    Enum with names used as string representation, and with lookup and equality based on
    this representation.
    """

    # convenience: enables `[]` name-based lookup with enum instances themselves
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.name


class AutoNumberNameEnum(NameEnum, aenum.AutoNumberEnum):
    """
    Auto-numbered enum with names used as string representation, and with lookup and
    equality based on this representation.
    """

    pass


class RangeEnum(float, ValueEnum):
    """
    Range enumeration inherit from ValueEnum, find suitable voltage/current/resistance
    input range for devices such as multimeter and oscilloscope
    """

    @classmethod
    @abstractmethod
    def unit(cls) -> str:
        """
        Returns the Unit of the values in the enumeration.
        :return: the unit of the values in the enumeration in string format
        """
        pass  # pragma: no cover

    @classmethod
    def _missing_value_(cls, value):
        """
        Find suitable desired range value
        If the desired range value is not available, the next suitable range which is
        larger than the desired range value is selected

        :param value: is the desired range value
        :raises ValueError: when desired range value is larger than device maximum value
        :return: the desired range value according to the device setting
        """
        range_unit = cls.unit()
        attrs = sorted([member.value for member in cls])  # type: ignore
        chosen_range: Optional[RangeEnum] = None
        for attr in attrs:
            if value < attr:
                chosen_range = cls(attr)
                logger.warning(
                    f"Desired value ({value} {range_unit}) not possible."
                    f"Next larger range ({chosen_range.value} {range_unit}) "
                    f"selected."
                )
                break
        if chosen_range is None:
            msg = (
                f"Desired value ({value} {range_unit}) is over the max value "
                f"({max(cls).value} {range_unit})."
            )
            logger.error(msg)
            raise ValueError(msg)
        return chosen_range


class BoolEnum(NameEnum):
    """
    BoolEnum inherits from NameEnum and the type of the first value is
        enforced to be 'boolean'. For bool()-operation the __bool__ is redefined here.
    """

    def __new__(cls, *values, **kwargs):
        if "value" in cls.__dict__["_creating_init_"]:
            raise ValueError("Name 'value' is reserved by 'Enum' and cannot be used.")
        if not isinstance(values[0], bool):
            raise TypeError(
                f"{cls}: first value must be bool [{values[0]} is a {type(values[0])}]"
            )
        return object.__new__(cls)

    def __bool__(self):
        """
        If member has multiple values only the first value is returned.

        :return: Only the first value is returned. The type of this value is
            enforced to be boolean
        """
        if isinstance(self.value, bool):
            return self.value
        else:
            return self.value[0]
