'''_520.py

GleasonSpiralBevelMeshSingleFlankRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating.bevel.standards import _519, _522
from mastapy._internal.python_net import python_net_import

_GLEASON_SPIRAL_BEVEL_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel.Standards', 'GleasonSpiralBevelMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GleasonSpiralBevelMeshSingleFlankRating',)


class GleasonSpiralBevelMeshSingleFlankRating(_522.SpiralBevelMeshSingleFlankRating):
    '''GleasonSpiralBevelMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _GLEASON_SPIRAL_BEVEL_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GleasonSpiralBevelMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def allowable_scoring_index(self) -> 'float':
        '''float: 'AllowableScoringIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableScoringIndex

    @property
    def safety_factor_scoring(self) -> 'float':
        '''float: 'SafetyFactorScoring' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorScoring

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def temperature_rise_at_critical_point_of_contact(self) -> 'float':
        '''float: 'TemperatureRiseAtCriticalPointOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TemperatureRiseAtCriticalPointOfContact

    @property
    def scoring_factor(self) -> 'float':
        '''float: 'ScoringFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScoringFactor

    @property
    def contact_ellipse_width_instantaneous(self) -> 'float':
        '''float: 'ContactEllipseWidthInstantaneous' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactEllipseWidthInstantaneous

    @property
    def assumed_maximum_pinion_torque(self) -> 'float':
        '''float: 'AssumedMaximumPinionTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssumedMaximumPinionTorque

    @property
    def geometry_factor_g(self) -> 'float':
        '''float: 'GeometryFactorG' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorG

    @property
    def thermal_factor(self) -> 'float':
        '''float: 'ThermalFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalFactor

    @property
    def load_factor_scoring(self) -> 'float':
        '''float: 'LoadFactorScoring' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadFactorScoring

    @property
    def gear_single_flank_ratings(self) -> 'List[_519.GleasonSpiralBevelGearSingleFlankRating]':
        '''List[GleasonSpiralBevelGearSingleFlankRating]: 'GearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSingleFlankRatings, constructor.new(_519.GleasonSpiralBevelGearSingleFlankRating))
        return value

    @property
    def gleason_bevel_gear_single_flank_ratings(self) -> 'List[_519.GleasonSpiralBevelGearSingleFlankRating]':
        '''List[GleasonSpiralBevelGearSingleFlankRating]: 'GleasonBevelGearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GleasonBevelGearSingleFlankRatings, constructor.new(_519.GleasonSpiralBevelGearSingleFlankRating))
        return value
