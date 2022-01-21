'''_5164.py

GearMeshStiffnessModel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_GEAR_MESH_STIFFNESS_MODEL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'GearMeshStiffnessModel')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshStiffnessModel',)


class GearMeshStiffnessModel(Enum):
    '''GearMeshStiffnessModel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _GEAR_MESH_STIFFNESS_MODEL

    __hash__ = None

    LOAD_CASE_SETTING = 0
    SIMPLE_STIFFNESS = 1
    BASIC_LTCA = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


GearMeshStiffnessModel.__setattr__ = __enum_setattr
GearMeshStiffnessModel.__delattr__ = __enum_delattr
