'''_2266.py

CylindricalGearSet
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.python_net import python_net_import
from mastapy.gears import _288
from mastapy.gears.gear_designs.cylindrical import _984, _995
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.gears.supercharger_rotor_set import _2303
from mastapy.system_model.part_model.gears import _2265, _2272
from mastapy.system_model.connections_and_sockets.gears import _2051

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSet',)


class CylindricalGearSet(_2272.GearSet):
    '''CylindricalGearSet

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_normal_module(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumNormalModule' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumNormalModule) if self.wrapped.MaximumNormalModule is not None else None

    @maximum_normal_module.setter
    def maximum_normal_module(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumNormalModule = value

    @property
    def minimum_normal_module(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumNormalModule' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumNormalModule) if self.wrapped.MinimumNormalModule is not None else None

    @minimum_normal_module.setter
    def minimum_normal_module(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumNormalModule = value

    @property
    def maximum_helix_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumHelixAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumHelixAngle) if self.wrapped.MaximumHelixAngle is not None else None

    @maximum_helix_angle.setter
    def maximum_helix_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumHelixAngle = value

    @property
    def is_supercharger_rotor_set(self) -> 'bool':
        '''bool: 'IsSuperchargerRotorSet' is the original name of this property.'''

        return self.wrapped.IsSuperchargerRotorSet

    @is_supercharger_rotor_set.setter
    def is_supercharger_rotor_set(self, value: 'bool'):
        self.wrapped.IsSuperchargerRotorSet = bool(value) if value else False

    @property
    def supercharger_rotor_set_database(self) -> 'str':
        '''str: 'SuperchargerRotorSetDatabase' is the original name of this property.'''

        return self.wrapped.SuperchargerRotorSetDatabase.SelectedItemName

    @supercharger_rotor_set_database.setter
    def supercharger_rotor_set_database(self, value: 'str'):
        self.wrapped.SuperchargerRotorSetDatabase.SetSelectedItem(str(value) if value else '')

    @property
    def axial_contact_ratio_requirement(self) -> 'overridable.Overridable_ContactRatioRequirements':
        '''overridable.Overridable_ContactRatioRequirements: 'AxialContactRatioRequirement' is the original name of this property.'''

        value = overridable.Overridable_ContactRatioRequirements.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.AxialContactRatioRequirement, value) if self.wrapped.AxialContactRatioRequirement is not None else None

    @axial_contact_ratio_requirement.setter
    def axial_contact_ratio_requirement(self, value: 'overridable.Overridable_ContactRatioRequirements.implicit_type()'):
        wrapper_type = overridable.Overridable_ContactRatioRequirements.wrapper_type()
        enclosed_type = overridable.Overridable_ContactRatioRequirements.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.AxialContactRatioRequirement = value

    @property
    def transverse_contact_ratio_requirement(self) -> 'overridable.Overridable_ContactRatioRequirements':
        '''overridable.Overridable_ContactRatioRequirements: 'TransverseContactRatioRequirement' is the original name of this property.'''

        value = overridable.Overridable_ContactRatioRequirements.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.TransverseContactRatioRequirement, value) if self.wrapped.TransverseContactRatioRequirement is not None else None

    @transverse_contact_ratio_requirement.setter
    def transverse_contact_ratio_requirement(self, value: 'overridable.Overridable_ContactRatioRequirements.implicit_type()'):
        wrapper_type = overridable.Overridable_ContactRatioRequirements.wrapper_type()
        enclosed_type = overridable.Overridable_ContactRatioRequirements.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.TransverseContactRatioRequirement = value

    @property
    def maximum_acceptable_axial_contact_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumAcceptableAxialContactRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumAcceptableAxialContactRatio) if self.wrapped.MaximumAcceptableAxialContactRatio is not None else None

    @maximum_acceptable_axial_contact_ratio.setter
    def maximum_acceptable_axial_contact_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumAcceptableAxialContactRatio = value

    @property
    def minimum_acceptable_axial_contact_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumAcceptableAxialContactRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumAcceptableAxialContactRatio) if self.wrapped.MinimumAcceptableAxialContactRatio is not None else None

    @minimum_acceptable_axial_contact_ratio.setter
    def minimum_acceptable_axial_contact_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumAcceptableAxialContactRatio = value

    @property
    def maximum_acceptable_axial_contact_ratio_above_integer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumAcceptableAxialContactRatioAboveInteger' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumAcceptableAxialContactRatioAboveInteger) if self.wrapped.MaximumAcceptableAxialContactRatioAboveInteger is not None else None

    @maximum_acceptable_axial_contact_ratio_above_integer.setter
    def maximum_acceptable_axial_contact_ratio_above_integer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumAcceptableAxialContactRatioAboveInteger = value

    @property
    def minimum_acceptable_axial_contact_ratio_below_integer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumAcceptableAxialContactRatioBelowInteger' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumAcceptableAxialContactRatioBelowInteger) if self.wrapped.MinimumAcceptableAxialContactRatioBelowInteger is not None else None

    @minimum_acceptable_axial_contact_ratio_below_integer.setter
    def minimum_acceptable_axial_contact_ratio_below_integer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumAcceptableAxialContactRatioBelowInteger = value

    @property
    def maximum_acceptable_transverse_contact_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumAcceptableTransverseContactRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumAcceptableTransverseContactRatio) if self.wrapped.MaximumAcceptableTransverseContactRatio is not None else None

    @maximum_acceptable_transverse_contact_ratio.setter
    def maximum_acceptable_transverse_contact_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumAcceptableTransverseContactRatio = value

    @property
    def minimum_acceptable_transverse_contact_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumAcceptableTransverseContactRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumAcceptableTransverseContactRatio) if self.wrapped.MinimumAcceptableTransverseContactRatio is not None else None

    @minimum_acceptable_transverse_contact_ratio.setter
    def minimum_acceptable_transverse_contact_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumAcceptableTransverseContactRatio = value

    @property
    def maximum_acceptable_transverse_contact_ratio_above_integer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumAcceptableTransverseContactRatioAboveInteger' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumAcceptableTransverseContactRatioAboveInteger) if self.wrapped.MaximumAcceptableTransverseContactRatioAboveInteger is not None else None

    @maximum_acceptable_transverse_contact_ratio_above_integer.setter
    def maximum_acceptable_transverse_contact_ratio_above_integer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumAcceptableTransverseContactRatioAboveInteger = value

    @property
    def minimum_acceptable_transverse_contact_ratio_below_integer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumAcceptableTransverseContactRatioBelowInteger' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumAcceptableTransverseContactRatioBelowInteger) if self.wrapped.MinimumAcceptableTransverseContactRatioBelowInteger is not None else None

    @minimum_acceptable_transverse_contact_ratio_below_integer.setter
    def minimum_acceptable_transverse_contact_ratio_below_integer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumAcceptableTransverseContactRatioBelowInteger = value

    @property
    def active_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def cylindrical_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'CylindricalGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.CylindricalGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_set_design to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.CylindricalGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearSetDesign.__class__)(self.wrapped.CylindricalGearSetDesign) if self.wrapped.CylindricalGearSetDesign is not None else None

    @property
    def supercharger_rotor_set(self) -> '_2303.SuperchargerRotorSet':
        '''SuperchargerRotorSet: 'SuperchargerRotorSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2303.SuperchargerRotorSet)(self.wrapped.SuperchargerRotorSet) if self.wrapped.SuperchargerRotorSet is not None else None

    @property
    def cylindrical_gears(self) -> 'List[_2265.CylindricalGear]':
        '''List[CylindricalGear]: 'CylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGears, constructor.new(_2265.CylindricalGear))
        return value

    @property
    def cylindrical_meshes(self) -> 'List[_2051.CylindricalGearMesh]':
        '''List[CylindricalGearMesh]: 'CylindricalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshes, constructor.new(_2051.CylindricalGearMesh))
        return value

    @property
    def gear_set_designs(self) -> 'List[_984.CylindricalGearSetDesign]':
        '''List[CylindricalGearSetDesign]: 'GearSetDesigns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSetDesigns, constructor.new(_984.CylindricalGearSetDesign))
        return value
