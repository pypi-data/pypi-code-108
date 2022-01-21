'''_12.py

FkmSnCurveModel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FKM_SN_CURVE_MODEL = python_net_import('SMT.MastaAPI.Shafts', 'FkmSnCurveModel')


__docformat__ = 'restructuredtext en'
__all__ = ('FkmSnCurveModel',)


class FkmSnCurveModel(Enum):
    '''FkmSnCurveModel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FKM_SN_CURVE_MODEL

    __hash__ = None

    MODEL_I = 0
    MODEL_II = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FkmSnCurveModel.__setattr__ = __enum_setattr
FkmSnCurveModel.__delattr__ = __enum_delattr
