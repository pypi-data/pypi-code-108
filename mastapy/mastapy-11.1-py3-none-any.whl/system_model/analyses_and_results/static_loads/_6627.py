'''_6627.py

InnerDiameterReference
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_INNER_DIAMETER_REFERENCE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'InnerDiameterReference')


__docformat__ = 'restructuredtext en'
__all__ = ('InnerDiameterReference',)


class InnerDiameterReference(Enum):
    '''InnerDiameterReference

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _INNER_DIAMETER_REFERENCE

    __hash__ = None

    FLUX = 0
    MASTA = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


InnerDiameterReference.__setattr__ = __enum_setattr
InnerDiameterReference.__delattr__ = __enum_delattr
