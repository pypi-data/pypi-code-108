'''_6579.py

CylindricalGearSetLoadCase
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _285
from mastapy._internal.implicit import overridable
from mastapy.materials.efficiency import _262
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.analyses_and_results.static_loads import (
    _6659, _6575, _6577, _6578,
    _6610
)
from mastapy.system_model.part_model.gears import _2266, _2282
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1057
from mastapy.gears.gear_designs.cylindrical import _1014
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'CylindricalGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetLoadCase',)


class CylindricalGearSetLoadCase(_6610.GearSetLoadCase):
    '''CylindricalGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def override_micro_geometry(self) -> 'bool':
        '''bool: 'OverrideMicroGeometry' is the original name of this property.'''

        return self.wrapped.OverrideMicroGeometry

    @override_micro_geometry.setter
    def override_micro_geometry(self, value: 'bool'):
        self.wrapped.OverrideMicroGeometry = bool(value) if value else False

    @property
    def coefficient_of_friction_calculation_method(self) -> '_285.CoefficientOfFrictionCalculationMethod':
        '''CoefficientOfFrictionCalculationMethod: 'CoefficientOfFrictionCalculationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CoefficientOfFrictionCalculationMethod)
        return constructor.new(_285.CoefficientOfFrictionCalculationMethod)(value) if value is not None else None

    @coefficient_of_friction_calculation_method.setter
    def coefficient_of_friction_calculation_method(self, value: '_285.CoefficientOfFrictionCalculationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CoefficientOfFrictionCalculationMethod = value

    @property
    def efficiency_rating_method(self) -> 'overridable.Overridable_EfficiencyRatingMethod':
        '''overridable.Overridable_EfficiencyRatingMethod: 'EfficiencyRatingMethod' is the original name of this property.'''

        value = overridable.Overridable_EfficiencyRatingMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.EfficiencyRatingMethod, value) if self.wrapped.EfficiencyRatingMethod is not None else None

    @efficiency_rating_method.setter
    def efficiency_rating_method(self, value: 'overridable.Overridable_EfficiencyRatingMethod.implicit_type()'):
        wrapper_type = overridable.Overridable_EfficiencyRatingMethod.wrapper_type()
        enclosed_type = overridable.Overridable_EfficiencyRatingMethod.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.EfficiencyRatingMethod = value

    @property
    def use_design_coefficient_of_friction_calculation_method(self) -> 'bool':
        '''bool: 'UseDesignCoefficientOfFrictionCalculationMethod' is the original name of this property.'''

        return self.wrapped.UseDesignCoefficientOfFrictionCalculationMethod

    @use_design_coefficient_of_friction_calculation_method.setter
    def use_design_coefficient_of_friction_calculation_method(self, value: 'bool'):
        self.wrapped.UseDesignCoefficientOfFrictionCalculationMethod = bool(value) if value else False

    @property
    def use_design_default_ltca_settings(self) -> 'bool':
        '''bool: 'UseDesignDefaultLTCASettings' is the original name of this property.'''

        return self.wrapped.UseDesignDefaultLTCASettings

    @use_design_default_ltca_settings.setter
    def use_design_default_ltca_settings(self, value: 'bool'):
        self.wrapped.UseDesignDefaultLTCASettings = bool(value) if value else False

    @property
    def reset_micro_geometry(self) -> '_6659.ResetMicroGeometryOptions':
        '''ResetMicroGeometryOptions: 'ResetMicroGeometry' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ResetMicroGeometry)
        return constructor.new(_6659.ResetMicroGeometryOptions)(value) if value is not None else None

    @reset_micro_geometry.setter
    def reset_micro_geometry(self, value: '_6659.ResetMicroGeometryOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ResetMicroGeometry = value

    @property
    def boost_pressure(self) -> 'float':
        '''float: 'BoostPressure' is the original name of this property.'''

        return self.wrapped.BoostPressure

    @boost_pressure.setter
    def boost_pressure(self, value: 'float'):
        self.wrapped.BoostPressure = float(value) if value else 0.0

    @property
    def dynamic_load_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicLoadFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicLoadFactor) if self.wrapped.DynamicLoadFactor is not None else None

    @dynamic_load_factor.setter
    def dynamic_load_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicLoadFactor = value

    @property
    def assembly_design(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to CylindricalGearSet. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def overridden_micro_geometry(self) -> '_1057.CylindricalGearSetMicroGeometry':
        '''CylindricalGearSetMicroGeometry: 'OverriddenMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1057.CylindricalGearSetMicroGeometry)(self.wrapped.OverriddenMicroGeometry) if self.wrapped.OverriddenMicroGeometry is not None else None

    @property
    def ltca(self) -> '_1014.LTCALoadCaseModifiableSettings':
        '''LTCALoadCaseModifiableSettings: 'LTCA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1014.LTCALoadCaseModifiableSettings)(self.wrapped.LTCA) if self.wrapped.LTCA is not None else None

    @property
    def gears(self) -> 'List[_6575.CylindricalGearLoadCase]':
        '''List[CylindricalGearLoadCase]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_6575.CylindricalGearLoadCase))
        return value

    @property
    def cylindrical_gears_load_case(self) -> 'List[_6575.CylindricalGearLoadCase]':
        '''List[CylindricalGearLoadCase]: 'CylindricalGearsLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearsLoadCase, constructor.new(_6575.CylindricalGearLoadCase))
        return value

    @property
    def cylindrical_meshes_load_case(self) -> 'List[_6577.CylindricalGearMeshLoadCase]':
        '''List[CylindricalGearMeshLoadCase]: 'CylindricalMeshesLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshesLoadCase, constructor.new(_6577.CylindricalGearMeshLoadCase))
        return value

    def get_harmonic_load_data_for_import(self) -> '_6578.CylindricalGearSetHarmonicLoadData':
        ''' 'GetHarmonicLoadDataForImport' is the original name of this method.

        Returns:
            mastapy.system_model.analyses_and_results.static_loads.CylindricalGearSetHarmonicLoadData
        '''

        method_result = self.wrapped.GetHarmonicLoadDataForImport()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
