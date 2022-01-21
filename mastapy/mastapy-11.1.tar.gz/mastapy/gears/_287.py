'''_287.py

ContactRatioDataSource
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONTACT_RATIO_DATA_SOURCE = python_net_import('SMT.MastaAPI.Gears', 'ContactRatioDataSource')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactRatioDataSource',)


class ContactRatioDataSource(Enum):
    '''ContactRatioDataSource

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONTACT_RATIO_DATA_SOURCE

    __hash__ = None

    DESIGN = 0
    OPERATING = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ContactRatioDataSource.__setattr__ = __enum_setattr
ContactRatioDataSource.__delattr__ = __enum_delattr
