'''_324.py

GearDutyCycleRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating import (
    _328, _325, _327, _320
)
from mastapy.gears.rating.worm import _341
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.face import _415
from mastapy.gears.rating.cylindrical import _427, _419, _420
from mastapy.gears.rating.conical import _501
from mastapy.gears.rating.concept import _512
from mastapy._internal.python_net import python_net_import

_GEAR_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating', 'GearDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GearDutyCycleRating',)


class GearDutyCycleRating(_320.AbstractGearRating):
    '''GearDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _GEAR_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def damage_bending(self) -> 'float':
        '''float: 'DamageBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageBending

    @property
    def damage_contact(self) -> 'float':
        '''float: 'DamageContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageContact

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress

    @property
    def maximum_bending_stress(self) -> 'float':
        '''float: 'MaximumBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumBendingStress

    @property
    def gear_set_design_duty_cycle(self) -> '_328.GearSetDutyCycleRating':
        '''GearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _328.GearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to GearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def gear_set_design_duty_cycle_of_type_worm_gear_set_duty_cycle_rating(self) -> '_341.WormGearSetDutyCycleRating':
        '''WormGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _341.WormGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to WormGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def gear_set_design_duty_cycle_of_type_face_gear_set_duty_cycle_rating(self) -> '_415.FaceGearSetDutyCycleRating':
        '''FaceGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _415.FaceGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to FaceGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def gear_set_design_duty_cycle_of_type_cylindrical_gear_set_duty_cycle_rating(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _427.CylindricalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to CylindricalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def gear_set_design_duty_cycle_of_type_conical_gear_set_duty_cycle_rating(self) -> '_501.ConicalGearSetDutyCycleRating':
        '''ConicalGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _501.ConicalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to ConicalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

    @property
    def gear_set_design_duty_cycle_of_type_concept_gear_set_duty_cycle_rating(self) -> '_512.ConceptGearSetDutyCycleRating':
        '''ConceptGearSetDutyCycleRating: 'GearSetDesignDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _512.ConceptGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDesignDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast gear_set_design_duty_cycle to ConceptGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDesignDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDesignDutyCycle.__class__)(self.wrapped.GearSetDesignDutyCycle) if self.wrapped.GearSetDesignDutyCycle is not None else None

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
    def gear_ratings(self) -> 'List[_327.GearRating]':
        '''List[GearRating]: 'GearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearRatings, constructor.new(_327.GearRating))
        return value
