'''_288.py

ContactRatioRequirements
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONTACT_RATIO_REQUIREMENTS = python_net_import('SMT.MastaAPI.Gears', 'ContactRatioRequirements')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactRatioRequirements',)


class ContactRatioRequirements(Enum):
    '''ContactRatioRequirements

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONTACT_RATIO_REQUIREMENTS

    __hash__ = None

    MAXIMISE = 0
    CLOSE_TO_INTEGER = 1
    IGNORE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ContactRatioRequirements.__setattr__ = __enum_setattr
ContactRatioRequirements.__delattr__ = __enum_delattr
