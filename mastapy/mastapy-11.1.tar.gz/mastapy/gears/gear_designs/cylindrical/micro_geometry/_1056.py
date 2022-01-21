'''_1056.py

CylindricalGearProfileModificationAtFaceWidthPosition
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1055
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PROFILE_MODIFICATION_AT_FACE_WIDTH_POSITION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearProfileModificationAtFaceWidthPosition')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearProfileModificationAtFaceWidthPosition',)


class CylindricalGearProfileModificationAtFaceWidthPosition(_1055.CylindricalGearProfileModification):
    '''CylindricalGearProfileModificationAtFaceWidthPosition

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_PROFILE_MODIFICATION_AT_FACE_WIDTH_POSITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearProfileModificationAtFaceWidthPosition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_position_factor(self) -> 'float':
        '''float: 'FaceWidthPositionFactor' is the original name of this property.'''

        return self.wrapped.FaceWidthPositionFactor

    @face_width_position_factor.setter
    def face_width_position_factor(self, value: 'float'):
        self.wrapped.FaceWidthPositionFactor = float(value) if value else 0.0

    @property
    def face_width_position(self) -> 'float':
        '''float: 'FaceWidthPosition' is the original name of this property.'''

        return self.wrapped.FaceWidthPosition

    @face_width_position.setter
    def face_width_position(self, value: 'float'):
        self.wrapped.FaceWidthPosition = float(value) if value else 0.0
