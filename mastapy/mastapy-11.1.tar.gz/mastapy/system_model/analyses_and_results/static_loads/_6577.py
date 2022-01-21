'''_6577.py

CylindricalGearMeshLoadCase
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.python_net import python_net_import
from mastapy.gears.rating.cylindrical.iso6336 import _471
from mastapy.system_model.connections_and_sockets.gears import _2051
from mastapy.gears.materials import _558
from mastapy.system_model.analyses_and_results.static_loads import _6578, _6607

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'CylindricalGearMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshLoadCase',)


class CylindricalGearMeshLoadCase(_6607.GearMeshLoadCase):
    '''CylindricalGearMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_load_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FaceLoadFactorBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FaceLoadFactorBending) if self.wrapped.FaceLoadFactorBending is not None else None

    @face_load_factor_bending.setter
    def face_load_factor_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FaceLoadFactorBending = value

    @property
    def face_load_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FaceLoadFactorContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FaceLoadFactorContact) if self.wrapped.FaceLoadFactorContact is not None else None

    @face_load_factor_contact.setter
    def face_load_factor_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FaceLoadFactorContact = value

    @property
    def transverse_load_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TransverseLoadFactorContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TransverseLoadFactorContact) if self.wrapped.TransverseLoadFactorContact is not None else None

    @transverse_load_factor_contact.setter
    def transverse_load_factor_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TransverseLoadFactorContact = value

    @property
    def transverse_load_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TransverseLoadFactorBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TransverseLoadFactorBending) if self.wrapped.TransverseLoadFactorBending is not None else None

    @transverse_load_factor_bending.setter
    def transverse_load_factor_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TransverseLoadFactorBending = value

    @property
    def permissible_specific_lubricant_film_thickness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleSpecificLubricantFilmThickness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleSpecificLubricantFilmThickness) if self.wrapped.PermissibleSpecificLubricantFilmThickness is not None else None

    @permissible_specific_lubricant_film_thickness.setter
    def permissible_specific_lubricant_film_thickness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PermissibleSpecificLubricantFilmThickness = value

    @property
    def use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents(self) -> 'bool':
        '''bool: 'UseDesignISO14179Part1CoefficientOfFrictionConstantsAndExponents' is the original name of this property.'''

        return self.wrapped.UseDesignISO14179Part1CoefficientOfFrictionConstantsAndExponents

    @use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents.setter
    def use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents(self, value: 'bool'):
        self.wrapped.UseDesignISO14179Part1CoefficientOfFrictionConstantsAndExponents = bool(value) if value else False

    @property
    def iso14179_part_1_coefficient_of_friction_constants_and_exponents_database(self) -> 'str':
        '''str: 'ISO14179Part1CoefficientOfFrictionConstantsAndExponentsDatabase' is the original name of this property.'''

        return self.wrapped.ISO14179Part1CoefficientOfFrictionConstantsAndExponentsDatabase.SelectedItemName

    @iso14179_part_1_coefficient_of_friction_constants_and_exponents_database.setter
    def iso14179_part_1_coefficient_of_friction_constants_and_exponents_database(self, value: 'str'):
        self.wrapped.ISO14179Part1CoefficientOfFrictionConstantsAndExponentsDatabase.SetSelectedItem(str(value) if value else '')

    @property
    def user_specified_coefficient_of_friction(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'UserSpecifiedCoefficientOfFriction' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.UserSpecifiedCoefficientOfFriction) if self.wrapped.UserSpecifiedCoefficientOfFriction is not None else None

    @user_specified_coefficient_of_friction.setter
    def user_specified_coefficient_of_friction(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.UserSpecifiedCoefficientOfFriction = value

    @property
    def misalignment_due_to_manufacturing_tolerances(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MisalignmentDueToManufacturingTolerances' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MisalignmentDueToManufacturingTolerances) if self.wrapped.MisalignmentDueToManufacturingTolerances is not None else None

    @misalignment_due_to_manufacturing_tolerances.setter
    def misalignment_due_to_manufacturing_tolerances(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MisalignmentDueToManufacturingTolerances = value

    @property
    def misalignment(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Misalignment' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Misalignment) if self.wrapped.Misalignment is not None else None

    @misalignment.setter
    def misalignment(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Misalignment = value

    @property
    def override_misalignment_in_system_deflection_and_ltca(self) -> 'bool':
        '''bool: 'OverrideMisalignmentInSystemDeflectionAndLTCA' is the original name of this property.'''

        return self.wrapped.OverrideMisalignmentInSystemDeflectionAndLTCA

    @override_misalignment_in_system_deflection_and_ltca.setter
    def override_misalignment_in_system_deflection_and_ltca(self, value: 'bool'):
        self.wrapped.OverrideMisalignmentInSystemDeflectionAndLTCA = bool(value) if value else False

    @property
    def application_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ApplicationFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ApplicationFactor) if self.wrapped.ApplicationFactor is not None else None

    @application_factor.setter
    def application_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ApplicationFactor = value

    @property
    def dynamic_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicFactor) if self.wrapped.DynamicFactor is not None else None

    @dynamic_factor.setter
    def dynamic_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicFactor = value

    @property
    def change_in_centre_distance_due_to_housing_thermal_effects(self) -> 'float':
        '''float: 'ChangeInCentreDistanceDueToHousingThermalEffects' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInCentreDistanceDueToHousingThermalEffects

    @property
    def do_profile_modifications_compensate_for_the_deflections_at_actual_load(self) -> 'bool':
        '''bool: 'DoProfileModificationsCompensateForTheDeflectionsAtActualLoad' is the original name of this property.'''

        return self.wrapped.DoProfileModificationsCompensateForTheDeflectionsAtActualLoad

    @do_profile_modifications_compensate_for_the_deflections_at_actual_load.setter
    def do_profile_modifications_compensate_for_the_deflections_at_actual_load(self, value: 'bool'):
        self.wrapped.DoProfileModificationsCompensateForTheDeflectionsAtActualLoad = bool(value) if value else False

    @property
    def helical_gear_micro_geometry_option(self) -> 'overridable.Overridable_HelicalGearMicroGeometryOption':
        '''overridable.Overridable_HelicalGearMicroGeometryOption: 'HelicalGearMicroGeometryOption' is the original name of this property.'''

        value = overridable.Overridable_HelicalGearMicroGeometryOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.HelicalGearMicroGeometryOption, value) if self.wrapped.HelicalGearMicroGeometryOption is not None else None

    @helical_gear_micro_geometry_option.setter
    def helical_gear_micro_geometry_option(self, value: 'overridable.Overridable_HelicalGearMicroGeometryOption.implicit_type()'):
        wrapper_type = overridable.Overridable_HelicalGearMicroGeometryOption.wrapper_type()
        enclosed_type = overridable.Overridable_HelicalGearMicroGeometryOption.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.HelicalGearMicroGeometryOption = value

    @property
    def connection_design(self) -> '_2051.CylindricalGearMesh':
        '''CylindricalGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2051.CylindricalGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def iso14179_coefficient_of_friction_constants_and_exponents(self) -> '_558.ISOTR1417912001CoefficientOfFrictionConstants':
        '''ISOTR1417912001CoefficientOfFrictionConstants: 'ISO14179CoefficientOfFrictionConstantsAndExponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_558.ISOTR1417912001CoefficientOfFrictionConstants)(self.wrapped.ISO14179CoefficientOfFrictionConstantsAndExponents) if self.wrapped.ISO14179CoefficientOfFrictionConstantsAndExponents is not None else None

    @property
    def planetaries(self) -> 'List[CylindricalGearMeshLoadCase]':
        '''List[CylindricalGearMeshLoadCase]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(CylindricalGearMeshLoadCase))
        return value

    def get_harmonic_load_data_for_import(self) -> '_6578.CylindricalGearSetHarmonicLoadData':
        ''' 'GetHarmonicLoadDataForImport' is the original name of this method.

        Returns:
            mastapy.system_model.analyses_and_results.static_loads.CylindricalGearSetHarmonicLoadData
        '''

        method_result = self.wrapped.GetHarmonicLoadDataForImport()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
