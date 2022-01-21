'''_1076.py

ProfileSlopeReliefWithDeviation
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1075
from mastapy._internal.python_net import python_net_import

_PROFILE_SLOPE_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'ProfileSlopeReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfileSlopeReliefWithDeviation',)


class ProfileSlopeReliefWithDeviation(_1075.ProfileReliefWithDeviation):
    '''ProfileSlopeReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _PROFILE_SLOPE_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProfileSlopeReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth
