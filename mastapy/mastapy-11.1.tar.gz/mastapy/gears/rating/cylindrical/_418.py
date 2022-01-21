'''_418.py

CylindricalGearDutyCycleRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating import _325, _324
from mastapy.gears.rating.cylindrical import (
    _419, _420, _427, _423,
    _437
)
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalGearDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearDutyCycleRating',)


class CylindricalGearDutyCycleRating(_324.GearDutyCycleRating):
    '''CylindricalGearDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor_against_permanent_deformation(self) -> 'float':
        '''float: 'SafetyFactorAgainstPermanentDeformation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorAgainstPermanentDeformation

    @property
    def safety_factor_against_permanent_deformation_with_influence_of_rim(self) -> 'float':
        '''float: 'SafetyFactorAgainstPermanentDeformationWithInfluenceOfRim' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorAgainstPermanentDeformationWithInfluenceOfRim

    @property
    def highest_maximum_material_exposure(self) -> 'float':
        '''float: 'HighestMaximumMaterialExposure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HighestMaximumMaterialExposure

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

    @property
    def gear_set_design_duty_cycle(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_427.CylindricalGearSetDutyCycleRating)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def cylindrical_gear_set_design_duty_cycle(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'CylindricalGearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_427.CylindricalGearSetDutyCycleRating)(self.wrapped.CylindricalGearSetDesignDutyCycle) if self.wrapped.CylindricalGearSetDesignDutyCycle is not None else None

    @property
    def gear_ratings(self) -> 'List[_423.CylindricalGearRating]':
        '''List[CylindricalGearRating]: 'GearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearRatings, constructor.new(_423.CylindricalGearRating))
        return value

    @property
    def cylindrical_gear_ratings(self) -> 'List[_423.CylindricalGearRating]':
        '''List[CylindricalGearRating]: 'CylindricalGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearRatings, constructor.new(_423.CylindricalGearRating))
        return value

    @property
    def cylindrical_gear_mesh_ratings(self) -> 'List[_437.MeshRatingForReports]':
        '''List[MeshRatingForReports]: 'CylindricalGearMeshRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearMeshRatings, constructor.new(_437.MeshRatingForReports))
        return value
