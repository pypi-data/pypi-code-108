'''_411.py

FaceGearDutyCycleRating
'''


from mastapy.gears.rating import _325, _324
from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _419, _420
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Face', 'FaceGearDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearDutyCycleRating',)


class FaceGearDutyCycleRating(_324.GearDutyCycleRating):
    '''FaceGearDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def left_flank_rating(self) -> '_325.GearFlankRating':
        '''GearFlankRating: 'LeftFlankRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _325.GearFlankRating.TYPE not in self.wrapped.LeftFlankRating.__class__.__mro__:
            raise CastException('Failed to cast left_flank_rating to GearFlankRating. Expected: {}.'.format(self.wrapped.LeftFlankRating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlankRating.__class__)(self.wrapped.LeftFlankRating) if self.wrapped.LeftFlankRating is not None else None

    @property
    def right_flank_rating(self) -> '_325.GearFlankRating':
        '''GearFlankRating: 'RightFlankRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _325.GearFlankRating.TYPE not in self.wrapped.RightFlankRating.__class__.__mro__:
            raise CastException('Failed to cast right_flank_rating to GearFlankRating. Expected: {}.'.format(self.wrapped.RightFlankRating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlankRating.__class__)(self.wrapped.RightFlankRating) if self.wrapped.RightFlankRating is not None else None
