'''_340.py

WormGearRating
'''


from mastapy.gears.gear_designs.worm import _914, _913, _917
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating import _325, _327
from mastapy.gears.rating.cylindrical import _419, _420
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Worm', 'WormGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearRating',)


class WormGearRating(_327.GearRating):
    '''WormGearRating

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def worm_gear(self) -> '_914.WormGearDesign':
        '''WormGearDesign: 'WormGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _914.WormGearDesign.TYPE not in self.wrapped.WormGear.__class__.__mro__:
            raise CastException('Failed to cast worm_gear to WormGearDesign. Expected: {}.'.format(self.wrapped.WormGear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.WormGear.__class__)(self.wrapped.WormGear) if self.wrapped.WormGear is not None else None

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
