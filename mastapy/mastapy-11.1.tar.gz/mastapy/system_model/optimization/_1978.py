'''_1978.py

MicroGeometryOptimisationTarget
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_OPTIMISATION_TARGET = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'MicroGeometryOptimisationTarget')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryOptimisationTarget',)


class MicroGeometryOptimisationTarget(Enum):
    '''MicroGeometryOptimisationTarget

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICRO_GEOMETRY_OPTIMISATION_TARGET

    __hash__ = None

    TRANSMISSION_ERROR = 0
    CONTACT_STRESS = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicroGeometryOptimisationTarget.__setattr__ = __enum_setattr
MicroGeometryOptimisationTarget.__delattr__ = __enum_delattr
