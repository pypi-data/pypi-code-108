'''_255.py

TransmissionApplications
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TRANSMISSION_APPLICATIONS = python_net_import('SMT.MastaAPI.Materials', 'TransmissionApplications')


__docformat__ = 'restructuredtext en'
__all__ = ('TransmissionApplications',)


class TransmissionApplications(Enum):
    '''TransmissionApplications

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TRANSMISSION_APPLICATIONS

    __hash__ = None

    GENERAL_INDUSTRIAL = 0
    AUTOMOTIVE = 1
    AIRCRAFT = 2
    MARINE = 3
    WIND_TURBINE = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TransmissionApplications.__setattr__ = __enum_setattr
TransmissionApplications.__delattr__ = __enum_delattr
