'''_6621.py

HarmonicLoadDataType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HARMONIC_LOAD_DATA_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'HarmonicLoadDataType')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicLoadDataType',)


class HarmonicLoadDataType(Enum):
    '''HarmonicLoadDataType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HARMONIC_LOAD_DATA_TYPE

    __hash__ = None

    TE = 0
    MISALIGNMENT = 1
    ROTOR_TORQUE_RIPPLE = 2
    SPEED_INDEPENDENT_FORCE = 3
    SPEED_DEPENDENT_FORCE = 4
    STATOR_TEETH_RADIAL_LOADS = 5
    STATOR_TEETH_TANGENTIAL_LOADS = 6
    ROTOR_XFORCES = 7
    ROTOR_YFORCES = 8
    ROTOR_ZFORCES = 9
    ROTOR_XMOMENT = 10
    ROTOR_YMOMENT = 11
    STATOR_TEETH_AXIAL_LOADS = 12


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HarmonicLoadDataType.__setattr__ = __enum_setattr
HarmonicLoadDataType.__delattr__ = __enum_delattr
