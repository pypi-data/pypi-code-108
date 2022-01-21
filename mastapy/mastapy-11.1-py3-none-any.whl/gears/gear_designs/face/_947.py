'''_947.py

FaceGearDiameterFaceWidthSpecificationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FACE_GEAR_DIAMETER_FACE_WIDTH_SPECIFICATION_METHOD = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Face', 'FaceGearDiameterFaceWidthSpecificationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearDiameterFaceWidthSpecificationMethod',)


class FaceGearDiameterFaceWidthSpecificationMethod(Enum):
    '''FaceGearDiameterFaceWidthSpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FACE_GEAR_DIAMETER_FACE_WIDTH_SPECIFICATION_METHOD

    __hash__ = None

    FACE_WIDTH_AND_FACE_WIDTH_OFFSET = 0
    INNER_AND_OUTER_DIAMETER = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FaceGearDiameterFaceWidthSpecificationMethod.__setattr__ = __enum_setattr
FaceGearDiameterFaceWidthSpecificationMethod.__delattr__ = __enum_delattr
