'''_1909.py

RollerBearing
'''


from typing import List

from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.bearings import _1648
from mastapy.bearings.roller_bearing_profiles import _1683, _1693
from mastapy.bearings.bearing_designs.rolling import _1912
from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'RollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearing',)


class RollerBearing(_1912.RollingBearing):
    '''RollerBearing

    This is a mastapy class.
    '''

    TYPE = _ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def element_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementDiameter) if self.wrapped.ElementDiameter is not None else None

    @element_diameter.setter
    def element_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementDiameter = value

    @property
    def roller_length(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RollerLength' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RollerLength) if self.wrapped.RollerLength is not None else None

    @roller_length.setter
    def roller_length(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RollerLength = value

    @property
    def effective_roller_length(self) -> 'float':
        '''float: 'EffectiveRollerLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveRollerLength

    @property
    def corner_radii(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CornerRadii' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CornerRadii) if self.wrapped.CornerRadii is not None else None

    @corner_radii.setter
    def corner_radii(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CornerRadii = value

    @property
    def roller_profile(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes: 'RollerProfile' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.RollerProfile, value) if self.wrapped.RollerProfile is not None else None

    @roller_profile.setter
    def roller_profile(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RollerBearingProfileTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.RollerProfile = value

    @property
    def kl(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'KL' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.KL) if self.wrapped.KL is not None else None

    @kl.setter
    def kl(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.KL = value

    @property
    def roller_profile_set(self) -> '_1683.ProfileSet':
        '''ProfileSet: 'RollerProfileSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1683.ProfileSet)(self.wrapped.RollerProfileSet) if self.wrapped.RollerProfileSet is not None else None

    @property
    def outer_race_profile_set(self) -> '_1683.ProfileSet':
        '''ProfileSet: 'OuterRaceProfileSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1683.ProfileSet)(self.wrapped.OuterRaceProfileSet) if self.wrapped.OuterRaceProfileSet is not None else None

    @property
    def inner_race_profile_set(self) -> '_1683.ProfileSet':
        '''ProfileSet: 'InnerRaceProfileSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1683.ProfileSet)(self.wrapped.InnerRaceProfileSet) if self.wrapped.InnerRaceProfileSet is not None else None

    @property
    def inner_race_and_roller_profiles(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'InnerRaceAndRollerProfiles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InnerRaceAndRollerProfiles, constructor.new(_1693.RollerRaceProfilePoint))
        return value

    @property
    def outer_race_and_roller_profiles(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'OuterRaceAndRollerProfiles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OuterRaceAndRollerProfiles, constructor.new(_1693.RollerRaceProfilePoint))
        return value

    @property
    def inner_race_and_roller_profiles_for_first_row(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'InnerRaceAndRollerProfilesForFirstRow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InnerRaceAndRollerProfilesForFirstRow, constructor.new(_1693.RollerRaceProfilePoint))
        return value

    @property
    def outer_race_and_roller_profiles_for_first_row(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'OuterRaceAndRollerProfilesForFirstRow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OuterRaceAndRollerProfilesForFirstRow, constructor.new(_1693.RollerRaceProfilePoint))
        return value

    @property
    def inner_race_and_roller_profiles_for_second_row(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'InnerRaceAndRollerProfilesForSecondRow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InnerRaceAndRollerProfilesForSecondRow, constructor.new(_1693.RollerRaceProfilePoint))
        return value

    @property
    def outer_race_and_roller_profiles_for_second_row(self) -> 'List[_1693.RollerRaceProfilePoint]':
        '''List[RollerRaceProfilePoint]: 'OuterRaceAndRollerProfilesForSecondRow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OuterRaceAndRollerProfilesForSecondRow, constructor.new(_1693.RollerRaceProfilePoint))
        return value
