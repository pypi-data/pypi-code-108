'''_237.py

LubricationDetail
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.materials import (
    _222, _245, _244, _227,
    _216, _234, _231, _233,
    _236, _235, _232, _211,
    _230
)
from mastapy.math_utility import _1333
from mastapy._internal.implicit import enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_LUBRICATION_DETAIL = python_net_import('SMT.MastaAPI.Materials', 'LubricationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('LubricationDetail',)


class LubricationDetail(_1597.NamedDatabaseItem):
    '''LubricationDetail

    This is a mastapy class.
    '''

    TYPE = _LUBRICATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LubricationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def scuffing_failure_load_stage(self) -> 'int':
        '''int: 'ScuffingFailureLoadStage' is the original name of this property.'''

        return self.wrapped.ScuffingFailureLoadStage

    @scuffing_failure_load_stage.setter
    def scuffing_failure_load_stage(self, value: 'int'):
        self.wrapped.ScuffingFailureLoadStage = int(value) if value else 0

    @property
    def micropitting_failure_load_stage(self) -> 'int':
        '''int: 'MicropittingFailureLoadStage' is the original name of this property.'''

        return self.wrapped.MicropittingFailureLoadStage

    @micropitting_failure_load_stage.setter
    def micropitting_failure_load_stage(self, value: 'int'):
        self.wrapped.MicropittingFailureLoadStage = int(value) if value else 0

    @property
    def micropitting_failure_load_stage_test_temperature(self) -> 'float':
        '''float: 'MicropittingFailureLoadStageTestTemperature' is the original name of this property.'''

        return self.wrapped.MicropittingFailureLoadStageTestTemperature

    @micropitting_failure_load_stage_test_temperature.setter
    def micropitting_failure_load_stage_test_temperature(self, value: 'float'):
        self.wrapped.MicropittingFailureLoadStageTestTemperature = float(value) if value else 0.0

    @property
    def kinematic_viscosity_of_the_lubricant_at_40_degrees_c(self) -> 'float':
        '''float: 'KinematicViscosityOfTheLubricantAt40DegreesC' is the original name of this property.'''

        return self.wrapped.KinematicViscosityOfTheLubricantAt40DegreesC

    @kinematic_viscosity_of_the_lubricant_at_40_degrees_c.setter
    def kinematic_viscosity_of_the_lubricant_at_40_degrees_c(self, value: 'float'):
        self.wrapped.KinematicViscosityOfTheLubricantAt40DegreesC = float(value) if value else 0.0

    @property
    def kinematic_viscosity_of_the_lubricant_at_100_degrees_c(self) -> 'float':
        '''float: 'KinematicViscosityOfTheLubricantAt100DegreesC' is the original name of this property.'''

        return self.wrapped.KinematicViscosityOfTheLubricantAt100DegreesC

    @kinematic_viscosity_of_the_lubricant_at_100_degrees_c.setter
    def kinematic_viscosity_of_the_lubricant_at_100_degrees_c(self, value: 'float'):
        self.wrapped.KinematicViscosityOfTheLubricantAt100DegreesC = float(value) if value else 0.0

    @property
    def density_specification_method(self) -> '_222.DensitySpecificationMethod':
        '''DensitySpecificationMethod: 'DensitySpecificationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DensitySpecificationMethod)
        return constructor.new(_222.DensitySpecificationMethod)(value) if value is not None else None

    @density_specification_method.setter
    def density_specification_method(self, value: '_222.DensitySpecificationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DensitySpecificationMethod = value

    @property
    def temperature_at_which_density_is_specified(self) -> 'float':
        '''float: 'TemperatureAtWhichDensityIsSpecified' is the original name of this property.'''

        return self.wrapped.TemperatureAtWhichDensityIsSpecified

    @temperature_at_which_density_is_specified.setter
    def temperature_at_which_density_is_specified(self, value: 'float'):
        self.wrapped.TemperatureAtWhichDensityIsSpecified = float(value) if value else 0.0

    @property
    def density(self) -> 'float':
        '''float: 'Density' is the original name of this property.'''

        return self.wrapped.Density

    @density.setter
    def density(self, value: 'float'):
        self.wrapped.Density = float(value) if value else 0.0

    @property
    def density_vs_temperature(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'DensityVsTemperature' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.DensityVsTemperature) if self.wrapped.DensityVsTemperature is not None else None

    @density_vs_temperature.setter
    def density_vs_temperature(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.DensityVsTemperature = value

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.'''

        return self.wrapped.Mass

    @mass.setter
    def mass(self, value: 'float'):
        self.wrapped.Mass = float(value) if value else 0.0

    @property
    def volume(self) -> 'float':
        '''float: 'Volume' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Volume

    @property
    def kinematic_viscosity_at_38c(self) -> 'float':
        '''float: 'KinematicViscosityAt38C' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.KinematicViscosityAt38C

    @property
    def dynamic_viscosity_at_38c(self) -> 'float':
        '''float: 'DynamicViscosityAt38C' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicViscosityAt38C

    @property
    def dynamic_viscosity_of_the_lubricant_at_40_degrees_c(self) -> 'float':
        '''float: 'DynamicViscosityOfTheLubricantAt40DegreesC' is the original name of this property.'''

        return self.wrapped.DynamicViscosityOfTheLubricantAt40DegreesC

    @dynamic_viscosity_of_the_lubricant_at_40_degrees_c.setter
    def dynamic_viscosity_of_the_lubricant_at_40_degrees_c(self, value: 'float'):
        self.wrapped.DynamicViscosityOfTheLubricantAt40DegreesC = float(value) if value else 0.0

    @property
    def dynamic_viscosity_of_the_lubricant_at_100_degrees_c(self) -> 'float':
        '''float: 'DynamicViscosityOfTheLubricantAt100DegreesC' is the original name of this property.'''

        return self.wrapped.DynamicViscosityOfTheLubricantAt100DegreesC

    @dynamic_viscosity_of_the_lubricant_at_100_degrees_c.setter
    def dynamic_viscosity_of_the_lubricant_at_100_degrees_c(self, value: 'float'):
        self.wrapped.DynamicViscosityOfTheLubricantAt100DegreesC = float(value) if value else 0.0

    @property
    def specified_parameter_k(self) -> 'float':
        '''float: 'SpecifiedParameterK' is the original name of this property.'''

        return self.wrapped.SpecifiedParameterK

    @specified_parameter_k.setter
    def specified_parameter_k(self, value: 'float'):
        self.wrapped.SpecifiedParameterK = float(value) if value else 0.0

    @property
    def specified_parameter_s(self) -> 'float':
        '''float: 'SpecifiedParameterS' is the original name of this property.'''

        return self.wrapped.SpecifiedParameterS

    @specified_parameter_s.setter
    def specified_parameter_s(self, value: 'float'):
        self.wrapped.SpecifiedParameterS = float(value) if value else 0.0

    @property
    def pressure_viscosity_coefficient_method(self) -> '_245.PressureViscosityCoefficientMethod':
        '''PressureViscosityCoefficientMethod: 'PressureViscosityCoefficientMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PressureViscosityCoefficientMethod)
        return constructor.new(_245.PressureViscosityCoefficientMethod)(value) if value is not None else None

    @pressure_viscosity_coefficient_method.setter
    def pressure_viscosity_coefficient_method(self, value: '_245.PressureViscosityCoefficientMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PressureViscosityCoefficientMethod = value

    @property
    def pressure_viscosity_coefficient(self) -> 'float':
        '''float: 'PressureViscosityCoefficient' is the original name of this property.'''

        return self.wrapped.PressureViscosityCoefficient

    @pressure_viscosity_coefficient.setter
    def pressure_viscosity_coefficient(self, value: 'float'):
        self.wrapped.PressureViscosityCoefficient = float(value) if value else 0.0

    @property
    def temperature_at_which_pressure_viscosity_coefficient_is_specified(self) -> 'float':
        '''float: 'TemperatureAtWhichPressureViscosityCoefficientIsSpecified' is the original name of this property.'''

        return self.wrapped.TemperatureAtWhichPressureViscosityCoefficientIsSpecified

    @temperature_at_which_pressure_viscosity_coefficient_is_specified.setter
    def temperature_at_which_pressure_viscosity_coefficient_is_specified(self, value: 'float'):
        self.wrapped.TemperatureAtWhichPressureViscosityCoefficientIsSpecified = float(value) if value else 0.0

    @property
    def specific_heat_capacity(self) -> 'float':
        '''float: 'SpecificHeatCapacity' is the original name of this property.'''

        return self.wrapped.SpecificHeatCapacity

    @specific_heat_capacity.setter
    def specific_heat_capacity(self, value: 'float'):
        self.wrapped.SpecificHeatCapacity = float(value) if value else 0.0

    @property
    def lubricant_shear_modulus(self) -> 'float':
        '''float: 'LubricantShearModulus' is the original name of this property.'''

        return self.wrapped.LubricantShearModulus

    @lubricant_shear_modulus.setter
    def lubricant_shear_modulus(self, value: 'float'):
        self.wrapped.LubricantShearModulus = float(value) if value else 0.0

    @property
    def oil_filtration_and_contamination(self) -> '_244.OilFiltrationOptions':
        '''OilFiltrationOptions: 'OilFiltrationAndContamination' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.OilFiltrationAndContamination)
        return constructor.new(_244.OilFiltrationOptions)(value) if value is not None else None

    @oil_filtration_and_contamination.setter
    def oil_filtration_and_contamination(self, value: '_244.OilFiltrationOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.OilFiltrationAndContamination = value

    @property
    def grease_contamination_level(self) -> '_227.GreaseContaminationOptions':
        '''GreaseContaminationOptions: 'GreaseContaminationLevel' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.GreaseContaminationLevel)
        return constructor.new(_227.GreaseContaminationOptions)(value) if value is not None else None

    @grease_contamination_level.setter
    def grease_contamination_level(self, value: '_227.GreaseContaminationOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.GreaseContaminationLevel = value

    @property
    def ep_additives_proven_with_severe_contamination(self) -> 'bool':
        '''bool: 'EPAdditivesProvenWithSevereContamination' is the original name of this property.'''

        return self.wrapped.EPAdditivesProvenWithSevereContamination

    @ep_additives_proven_with_severe_contamination.setter
    def ep_additives_proven_with_severe_contamination(self, value: 'bool'):
        self.wrapped.EPAdditivesProvenWithSevereContamination = bool(value) if value else False

    @property
    def ep_and_aw_additives_present(self) -> 'bool':
        '''bool: 'EPAndAWAdditivesPresent' is the original name of this property.'''

        return self.wrapped.EPAndAWAdditivesPresent

    @ep_and_aw_additives_present.setter
    def ep_and_aw_additives_present(self, value: 'bool'):
        self.wrapped.EPAndAWAdditivesPresent = bool(value) if value else False

    @property
    def system_includes_oil_pump(self) -> 'bool':
        '''bool: 'SystemIncludesOilPump' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SystemIncludesOilPump

    @property
    def feed_flow_rate(self) -> 'float':
        '''float: 'FeedFlowRate' is the original name of this property.'''

        return self.wrapped.FeedFlowRate

    @feed_flow_rate.setter
    def feed_flow_rate(self, value: 'float'):
        self.wrapped.FeedFlowRate = float(value) if value else 0.0

    @property
    def feed_pressure(self) -> 'float':
        '''float: 'FeedPressure' is the original name of this property.'''

        return self.wrapped.FeedPressure

    @feed_pressure.setter
    def feed_pressure(self, value: 'float'):
        self.wrapped.FeedPressure = float(value) if value else 0.0

    @property
    def air_flow_velocity(self) -> 'float':
        '''float: 'AirFlowVelocity' is the original name of this property.'''

        return self.wrapped.AirFlowVelocity

    @air_flow_velocity.setter
    def air_flow_velocity(self, value: 'float'):
        self.wrapped.AirFlowVelocity = float(value) if value else 0.0

    @property
    def heat_transfer_coefficient(self) -> 'float':
        '''float: 'HeatTransferCoefficient' is the original name of this property.'''

        return self.wrapped.HeatTransferCoefficient

    @heat_transfer_coefficient.setter
    def heat_transfer_coefficient(self, value: 'float'):
        self.wrapped.HeatTransferCoefficient = float(value) if value else 0.0

    @property
    def specify_heat_transfer_coefficient(self) -> 'bool':
        '''bool: 'SpecifyHeatTransferCoefficient' is the original name of this property.'''

        return self.wrapped.SpecifyHeatTransferCoefficient

    @specify_heat_transfer_coefficient.setter
    def specify_heat_transfer_coefficient(self, value: 'bool'):
        self.wrapped.SpecifyHeatTransferCoefficient = bool(value) if value else False

    @property
    def oil_to_air_heat_transfer_area(self) -> 'float':
        '''float: 'OilToAirHeatTransferArea' is the original name of this property.'''

        return self.wrapped.OilToAirHeatTransferArea

    @oil_to_air_heat_transfer_area.setter
    def oil_to_air_heat_transfer_area(self, value: 'float'):
        self.wrapped.OilToAirHeatTransferArea = float(value) if value else 0.0

    @property
    def lubricant_type_supply(self) -> '_216.BearingLubricationCondition':
        '''BearingLubricationCondition: 'LubricantTypeSupply' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LubricantTypeSupply)
        return constructor.new(_216.BearingLubricationCondition)(value) if value is not None else None

    @lubricant_type_supply.setter
    def lubricant_type_supply(self, value: '_216.BearingLubricationCondition'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LubricantTypeSupply = value

    @property
    def factor_for_newly_greased_bearings(self) -> 'float':
        '''float: 'FactorForNewlyGreasedBearings' is the original name of this property.'''

        return self.wrapped.FactorForNewlyGreasedBearings

    @factor_for_newly_greased_bearings.setter
    def factor_for_newly_greased_bearings(self, value: 'float'):
        self.wrapped.FactorForNewlyGreasedBearings = float(value) if value else 0.0

    @property
    def lubricant_viscosity_classification(self) -> '_234.LubricantViscosityClassification':
        '''LubricantViscosityClassification: 'LubricantViscosityClassification' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LubricantViscosityClassification)
        return constructor.new(_234.LubricantViscosityClassification)(value) if value is not None else None

    @lubricant_viscosity_classification.setter
    def lubricant_viscosity_classification(self, value: '_234.LubricantViscosityClassification'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LubricantViscosityClassification = value

    @property
    def lubricant_definition(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LubricantDefinition':
        '''enum_with_selected_value.EnumWithSelectedValue_LubricantDefinition: 'LubricantDefinition' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LubricantDefinition.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LubricantDefinition, value) if self.wrapped.LubricantDefinition is not None else None

    @lubricant_definition.setter
    def lubricant_definition(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LubricantDefinition.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LubricantDefinition.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LubricantDefinition = value

    @property
    def lubricant_grade_agma(self) -> '_233.LubricantViscosityClassAGMA':
        '''LubricantViscosityClassAGMA: 'LubricantGradeAGMA' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LubricantGradeAGMA)
        return constructor.new(_233.LubricantViscosityClassAGMA)(value) if value is not None else None

    @lubricant_grade_agma.setter
    def lubricant_grade_agma(self, value: '_233.LubricantViscosityClassAGMA'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LubricantGradeAGMA = value

    @property
    def lubricant_grade_sae(self) -> '_236.LubricantViscosityClassSAE':
        '''LubricantViscosityClassSAE: 'LubricantGradeSAE' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LubricantGradeSAE)
        return constructor.new(_236.LubricantViscosityClassSAE)(value) if value is not None else None

    @lubricant_grade_sae.setter
    def lubricant_grade_sae(self, value: '_236.LubricantViscosityClassSAE'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LubricantGradeSAE = value

    @property
    def lubricant_grade_iso(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LubricantViscosityClassISO':
        '''enum_with_selected_value.EnumWithSelectedValue_LubricantViscosityClassISO: 'LubricantGradeISO' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LubricantViscosityClassISO.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.LubricantGradeISO, value) if self.wrapped.LubricantGradeISO is not None else None

    @lubricant_grade_iso.setter
    def lubricant_grade_iso(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LubricantViscosityClassISO.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LubricantViscosityClassISO.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.LubricantGradeISO = value

    @property
    def delivery(self) -> '_232.LubricantDelivery':
        '''LubricantDelivery: 'Delivery' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Delivery)
        return constructor.new(_232.LubricantDelivery)(value) if value is not None else None

    @property
    def agma925a03_lubricant_type(self) -> '_211.AGMALubricantType':
        '''AGMALubricantType: 'AGMA925A03LubricantType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AGMA925A03LubricantType)
        return constructor.new(_211.AGMALubricantType)(value) if value is not None else None

    @agma925a03_lubricant_type.setter
    def agma925a03_lubricant_type(self, value: '_211.AGMALubricantType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AGMA925A03LubricantType = value

    @property
    def iso_lubricant_type(self) -> '_230.ISOLubricantType':
        '''ISOLubricantType: 'ISOLubricantType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ISOLubricantType)
        return constructor.new(_230.ISOLubricantType)(value) if value is not None else None

    @iso_lubricant_type.setter
    def iso_lubricant_type(self, value: '_230.ISOLubricantType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ISOLubricantType = value

    @property
    def use_user_specified_contamination_factor(self) -> 'bool':
        '''bool: 'UseUserSpecifiedContaminationFactor' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedContaminationFactor

    @use_user_specified_contamination_factor.setter
    def use_user_specified_contamination_factor(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedContaminationFactor = bool(value) if value else False

    @property
    def user_specified_contamination_factor(self) -> 'float':
        '''float: 'UserSpecifiedContaminationFactor' is the original name of this property.'''

        return self.wrapped.UserSpecifiedContaminationFactor

    @user_specified_contamination_factor.setter
    def user_specified_contamination_factor(self, value: 'float'):
        self.wrapped.UserSpecifiedContaminationFactor = float(value) if value else 0.0
