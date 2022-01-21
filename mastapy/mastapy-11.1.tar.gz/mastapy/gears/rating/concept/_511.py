'''_511.py

ConceptGearRating
'''


from mastapy.gears.rating import _325, _327
from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _419, _420
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.concept import _1123
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Concept', 'ConceptGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearRating',)


class ConceptGearRating(_327.GearRating):
    '''ConceptGearRating

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def concave_flank_rating(self) -> '_325.GearFlankRating':
        '''GearFlankRating: 'ConcaveFlankRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _325.GearFlankRating.TYPE not in self.wrapped.ConcaveFlankRating.__class__.__mro__:
            raise CastException('Failed to cast concave_flank_rating to GearFlankRating. Expected: {}.'.format(self.wrapped.ConcaveFlankRating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConcaveFlankRating.__class__)(self.wrapped.ConcaveFlankRating) if self.wrapped.ConcaveFlankRating is not None else None

    @property
    def convex_flank_rating(self) -> '_325.GearFlankRating':
        '''GearFlankRating: 'ConvexFlankRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _325.GearFlankRating.TYPE not in self.wrapped.ConvexFlankRating.__class__.__mro__:
            raise CastException('Failed to cast convex_flank_rating to GearFlankRating. Expected: {}.'.format(self.wrapped.ConvexFlankRating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConvexFlankRating.__class__)(self.wrapped.ConvexFlankRating) if self.wrapped.ConvexFlankRating is not None else None

    @property
    def concept_gear(self) -> '_1123.ConceptGearDesign':
        '''ConceptGearDesign: 'ConceptGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1123.ConceptGearDesign)(self.wrapped.ConceptGear) if self.wrapped.ConceptGear is not None else None
