'''_300.py

ISOToleranceStandard
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ISO_TOLERANCE_STANDARD = python_net_import('SMT.MastaAPI.Gears', 'ISOToleranceStandard')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOToleranceStandard',)


class ISOToleranceStandard(Enum):
    '''ISOToleranceStandard

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ISO_TOLERANCE_STANDARD

    __hash__ = None

    ISO_132811995EISO_132821997E = 0
    ISO_132812013EISO_132821997E = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ISOToleranceStandard.__setattr__ = __enum_setattr
ISOToleranceStandard.__delattr__ = __enum_delattr
