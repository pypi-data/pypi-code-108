'''_1636.py

BearingModel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_MODEL = python_net_import('SMT.MastaAPI.Bearings', 'BearingModel')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingModel',)


class BearingModel(Enum):
    '''BearingModel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_MODEL

    __hash__ = None

    CONCEPT_BEARING = 0
    AXIAL_CLEARANCE_BEARING = 1
    RADIAL_CLEARANCE_BEARING = 2
    ROLLING_BEARING = 3
    PLAIN_JOURNAL_BEARING = 4
    TILTING_PAD_THRUST_BEARING = 5
    TILTING_PAD_JOURNAL_BEARING = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingModel.__setattr__ = __enum_setattr
BearingModel.__delattr__ = __enum_delattr
