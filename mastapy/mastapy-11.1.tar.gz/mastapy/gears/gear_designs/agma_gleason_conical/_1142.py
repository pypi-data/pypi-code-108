'''_1142.py

AGMAGleasonConicalGearSetDesign
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.gears.gear_designs.bevel import _1126
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.gears import _314, _311
from mastapy.gears.gear_designs.conical import _1112, _1103
from mastapy.gleason_smt_link import _273
from mastapy.gears.gear_designs.agma_gleason_conical import _1141
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.AGMAGleasonConical', 'AGMAGleasonConicalGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearSetDesign',)


class AGMAGleasonConicalGearSetDesign(_1103.ConicalGearSetDesign):
    '''AGMAGleasonConicalGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def design_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_AGMAGleasonConicalGearGeometryMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_AGMAGleasonConicalGearGeometryMethods: 'DesignMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_AGMAGleasonConicalGearGeometryMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DesignMethod, value) if self.wrapped.DesignMethod is not None else None

    @design_method.setter
    def design_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_AGMAGleasonConicalGearGeometryMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_AGMAGleasonConicalGearGeometryMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DesignMethod = value

    @property
    def input_module(self) -> 'bool':
        '''bool: 'InputModule' is the original name of this property.'''

        return self.wrapped.InputModule

    @input_module.setter
    def input_module(self, value: 'bool'):
        self.wrapped.InputModule = bool(value) if value else False

    @property
    def mean_normal_module(self) -> 'float':
        '''float: 'MeanNormalModule' is the original name of this property.'''

        return self.wrapped.MeanNormalModule

    @mean_normal_module.setter
    def mean_normal_module(self, value: 'float'):
        self.wrapped.MeanNormalModule = float(value) if value else 0.0

    @property
    def tooth_taper(self) -> '_314.SpiralBevelToothTaper':
        '''SpiralBevelToothTaper: 'ToothTaper' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ToothTaper)
        return constructor.new(_314.SpiralBevelToothTaper)(value) if value is not None else None

    @tooth_taper.setter
    def tooth_taper(self, value: '_314.SpiralBevelToothTaper'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ToothTaper = value

    @property
    def reliability_requirement_gleason(self) -> '_1112.GleasonSafetyRequirements':
        '''GleasonSafetyRequirements: 'ReliabilityRequirementGleason' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ReliabilityRequirementGleason)
        return constructor.new(_1112.GleasonSafetyRequirements)(value) if value is not None else None

    @reliability_requirement_gleason.setter
    def reliability_requirement_gleason(self, value: '_1112.GleasonSafetyRequirements'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ReliabilityRequirementGleason = value

    @property
    def reliability_requirement_agma(self) -> '_311.SafetyRequirementsAGMA':
        '''SafetyRequirementsAGMA: 'ReliabilityRequirementAGMA' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ReliabilityRequirementAGMA)
        return constructor.new(_311.SafetyRequirementsAGMA)(value) if value is not None else None

    @reliability_requirement_agma.setter
    def reliability_requirement_agma(self, value: '_311.SafetyRequirementsAGMA'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ReliabilityRequirementAGMA = value

    @property
    def gleason_minimum_factor_of_safety_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'GleasonMinimumFactorOfSafetyContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.GleasonMinimumFactorOfSafetyContact) if self.wrapped.GleasonMinimumFactorOfSafetyContact is not None else None

    @gleason_minimum_factor_of_safety_contact.setter
    def gleason_minimum_factor_of_safety_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.GleasonMinimumFactorOfSafetyContact = value

    @property
    def gleason_minimum_factor_of_safety_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'GleasonMinimumFactorOfSafetyBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.GleasonMinimumFactorOfSafetyBending) if self.wrapped.GleasonMinimumFactorOfSafetyBending is not None else None

    @gleason_minimum_factor_of_safety_bending.setter
    def gleason_minimum_factor_of_safety_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.GleasonMinimumFactorOfSafetyBending = value

    @property
    def reliability_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReliabilityFactorContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReliabilityFactorContact) if self.wrapped.ReliabilityFactorContact is not None else None

    @reliability_factor_contact.setter
    def reliability_factor_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ReliabilityFactorContact = value

    @property
    def reliability_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReliabilityFactorBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReliabilityFactorBending) if self.wrapped.ReliabilityFactorBending is not None else None

    @reliability_factor_bending.setter
    def reliability_factor_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ReliabilityFactorBending = value

    @property
    def number_of_blade_groups(self) -> 'float':
        '''float: 'NumberOfBladeGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfBladeGroups

    @property
    def number_of_crown_gear_teeth(self) -> 'float':
        '''float: 'NumberOfCrownGearTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCrownGearTeeth

    @property
    def crown_gear_to_cutter_centre_distance(self) -> 'float':
        '''float: 'CrownGearToCutterCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrownGearToCutterCentreDistance

    @property
    def wheel_involute_cone_distance(self) -> 'float':
        '''float: 'WheelInvoluteConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInvoluteConeDistance

    @property
    def wheel_involute_to_outer_cone_distance_ratio(self) -> 'float':
        '''float: 'WheelInvoluteToOuterConeDistanceRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInvoluteToOuterConeDistanceRatio

    @property
    def wheel_involute_to_mean_cone_distance_ratio(self) -> 'float':
        '''float: 'WheelInvoluteToMeanConeDistanceRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInvoluteToMeanConeDistanceRatio

    @property
    def epicycloid_base_circle_radius(self) -> 'float':
        '''float: 'EpicycloidBaseCircleRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EpicycloidBaseCircleRadius

    @property
    def manufacturing_method(self) -> '_273.CutterMethod':
        '''CutterMethod: 'ManufacturingMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ManufacturingMethod)
        return constructor.new(_273.CutterMethod)(value) if value is not None else None

    @manufacturing_method.setter
    def manufacturing_method(self, value: '_273.CutterMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ManufacturingMethod = value

    @property
    def required_minimum_topland_to_module_factor(self) -> 'float':
        '''float: 'RequiredMinimumToplandToModuleFactor' is the original name of this property.'''

        return self.wrapped.RequiredMinimumToplandToModuleFactor

    @required_minimum_topland_to_module_factor.setter
    def required_minimum_topland_to_module_factor(self, value: 'float'):
        self.wrapped.RequiredMinimumToplandToModuleFactor = float(value) if value else 0.0

    @property
    def pitch_limit_pressure_angle(self) -> 'float':
        '''float: 'PitchLimitPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchLimitPressureAngle

    @property
    def pinion_offset_angle_in_root_plane(self) -> 'float':
        '''float: 'PinionOffsetAngleInRootPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionOffsetAngleInRootPlane

    @property
    def conical_meshes(self) -> 'List[_1141.AGMAGleasonConicalGearMeshDesign]':
        '''List[AGMAGleasonConicalGearMeshDesign]: 'ConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConicalMeshes, constructor.new(_1141.AGMAGleasonConicalGearMeshDesign))
        return value

    @property
    def meshes(self) -> 'List[_1141.AGMAGleasonConicalGearMeshDesign]':
        '''List[AGMAGleasonConicalGearMeshDesign]: 'Meshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Meshes, constructor.new(_1141.AGMAGleasonConicalGearMeshDesign))
        return value

    def store_ki_mo_skip_file(self):
        ''' 'StoreKIMoSKIPFile' is the original name of this method.'''

        self.wrapped.StoreKIMoSKIPFile()

    def export_ki_mo_skip_file(self):
        ''' 'ExportKIMoSKIPFile' is the original name of this method.'''

        self.wrapped.ExportKIMoSKIPFile()

    def ki_mo_sxml_data(self):
        ''' 'KIMoSXMLData' is the original name of this method.'''

        self.wrapped.KIMoSXMLData()

    def gleason_gemsxml_data(self):
        ''' 'GleasonGEMSXMLData' is the original name of this method.'''

        self.wrapped.GleasonGEMSXMLData()
