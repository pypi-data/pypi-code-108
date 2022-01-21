'''_974.py

CylindricalGearDesignSettings
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1071
from mastapy.gears.gear_designs.cylindrical import (
    _999, _982, _1016, _1017
)
from mastapy.gears.micro_geometry import (
    _531, _533, _534, _536,
    _538, _541, _535, _537,
    _540
)
from mastapy.gears import _310, _300, _281
from mastapy.utility.units_and_measurements import _1400
from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_DESIGN_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearDesignSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearDesignSettings',)


class CylindricalGearDesignSettings(_1387.PerMachineSettings):
    '''CylindricalGearDesignSettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_DESIGN_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearDesignSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_steps_for_ltca_contact_surface(self) -> 'int':
        '''int: 'NumberOfStepsForLTCAContactSurface' is the original name of this property.'''

        return self.wrapped.NumberOfStepsForLTCAContactSurface

    @number_of_steps_for_ltca_contact_surface.setter
    def number_of_steps_for_ltca_contact_surface(self, value: 'int'):
        self.wrapped.NumberOfStepsForLTCAContactSurface = int(value) if value else 0

    @property
    def draw_micro_geometry_profile_chart_with_relief_on_horizontal_axis(self) -> 'bool':
        '''bool: 'DrawMicroGeometryProfileChartWithReliefOnHorizontalAxis' is the original name of this property.'''

        return self.wrapped.DrawMicroGeometryProfileChartWithReliefOnHorizontalAxis

    @draw_micro_geometry_profile_chart_with_relief_on_horizontal_axis.setter
    def draw_micro_geometry_profile_chart_with_relief_on_horizontal_axis(self, value: 'bool'):
        self.wrapped.DrawMicroGeometryProfileChartWithReliefOnHorizontalAxis = bool(value) if value else False

    @property
    def draw_micro_geometry_charts_with_face_width_axis_oriented_to_view_through_air(self) -> 'bool':
        '''bool: 'DrawMicroGeometryChartsWithFaceWidthAxisOrientedToViewThroughAir' is the original name of this property.'''

        return self.wrapped.DrawMicroGeometryChartsWithFaceWidthAxisOrientedToViewThroughAir

    @draw_micro_geometry_charts_with_face_width_axis_oriented_to_view_through_air.setter
    def draw_micro_geometry_charts_with_face_width_axis_oriented_to_view_through_air(self, value: 'bool'):
        self.wrapped.DrawMicroGeometryChartsWithFaceWidthAxisOrientedToViewThroughAir = bool(value) if value else False

    @property
    def add_flank_side_labels_to_micro_geometry_lead_tolerance_charts(self) -> 'bool':
        '''bool: 'AddFlankSideLabelsToMicroGeometryLeadToleranceCharts' is the original name of this property.'''

        return self.wrapped.AddFlankSideLabelsToMicroGeometryLeadToleranceCharts

    @add_flank_side_labels_to_micro_geometry_lead_tolerance_charts.setter
    def add_flank_side_labels_to_micro_geometry_lead_tolerance_charts(self, value: 'bool'):
        self.wrapped.AddFlankSideLabelsToMicroGeometryLeadToleranceCharts = bool(value) if value else False

    @property
    def crop_face_width_axis_of_micro_geometry_lead_tolerance_charts(self) -> 'bool':
        '''bool: 'CropFaceWidthAxisOfMicroGeometryLeadToleranceCharts' is the original name of this property.'''

        return self.wrapped.CropFaceWidthAxisOfMicroGeometryLeadToleranceCharts

    @crop_face_width_axis_of_micro_geometry_lead_tolerance_charts.setter
    def crop_face_width_axis_of_micro_geometry_lead_tolerance_charts(self, value: 'bool'):
        self.wrapped.CropFaceWidthAxisOfMicroGeometryLeadToleranceCharts = bool(value) if value else False

    @property
    def crop_profile_measurement_axis_of_micro_geometry_profile_tolerance_charts(self) -> 'bool':
        '''bool: 'CropProfileMeasurementAxisOfMicroGeometryProfileToleranceCharts' is the original name of this property.'''

        return self.wrapped.CropProfileMeasurementAxisOfMicroGeometryProfileToleranceCharts

    @crop_profile_measurement_axis_of_micro_geometry_profile_tolerance_charts.setter
    def crop_profile_measurement_axis_of_micro_geometry_profile_tolerance_charts(self, value: 'bool'):
        self.wrapped.CropProfileMeasurementAxisOfMicroGeometryProfileToleranceCharts = bool(value) if value else False

    @property
    def default_micro_geometry_lead_tolerance_chart_view(self) -> '_1071.MicroGeometryLeadToleranceChartView':
        '''MicroGeometryLeadToleranceChartView: 'DefaultMicroGeometryLeadToleranceChartView' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DefaultMicroGeometryLeadToleranceChartView)
        return constructor.new(_1071.MicroGeometryLeadToleranceChartView)(value) if value is not None else None

    @default_micro_geometry_lead_tolerance_chart_view.setter
    def default_micro_geometry_lead_tolerance_chart_view(self, value: '_1071.MicroGeometryLeadToleranceChartView'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DefaultMicroGeometryLeadToleranceChartView = value

    @property
    def default_scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts(self) -> '_999.DoubleAxisScaleAndRange':
        '''DoubleAxisScaleAndRange: 'DefaultScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DefaultScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts)
        return constructor.new(_999.DoubleAxisScaleAndRange)(value) if value is not None else None

    @default_scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts.setter
    def default_scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts(self, value: '_999.DoubleAxisScaleAndRange'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DefaultScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts = value

    @property
    def default_flank_side_with_zero_face_width(self) -> '_531.FlankSide':
        '''FlankSide: 'DefaultFlankSideWithZeroFaceWidth' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DefaultFlankSideWithZeroFaceWidth)
        return constructor.new(_531.FlankSide)(value) if value is not None else None

    @default_flank_side_with_zero_face_width.setter
    def default_flank_side_with_zero_face_width(self, value: '_531.FlankSide'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DefaultFlankSideWithZeroFaceWidth = value

    @property
    def cylindrical_gear_profile_measurement(self) -> '_982.CylindricalGearProfileMeasurementType':
        '''CylindricalGearProfileMeasurementType: 'CylindricalGearProfileMeasurement' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CylindricalGearProfileMeasurement)
        return constructor.new(_982.CylindricalGearProfileMeasurementType)(value) if value is not None else None

    @cylindrical_gear_profile_measurement.setter
    def cylindrical_gear_profile_measurement(self, value: '_982.CylindricalGearProfileMeasurementType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CylindricalGearProfileMeasurement = value

    @property
    def agma_quality_grade_type(self) -> '_310.QualityGradeTypes':
        '''QualityGradeTypes: 'AGMAQualityGradeType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AGMAQualityGradeType)
        return constructor.new(_310.QualityGradeTypes)(value) if value is not None else None

    @agma_quality_grade_type.setter
    def agma_quality_grade_type(self, value: '_310.QualityGradeTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AGMAQualityGradeType = value

    @property
    def tolerance_rounding_system(self) -> '_1400.MeasurementSystem':
        '''MeasurementSystem: 'ToleranceRoundingSystem' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ToleranceRoundingSystem)
        return constructor.new(_1400.MeasurementSystem)(value) if value is not None else None

    @tolerance_rounding_system.setter
    def tolerance_rounding_system(self, value: '_1400.MeasurementSystem'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ToleranceRoundingSystem = value

    @property
    def iso_tolerances_standard(self) -> 'overridable.Overridable_ISOToleranceStandard':
        '''overridable.Overridable_ISOToleranceStandard: 'ISOTolerancesStandard' is the original name of this property.'''

        value = overridable.Overridable_ISOToleranceStandard.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ISOTolerancesStandard, value) if self.wrapped.ISOTolerancesStandard is not None else None

    @iso_tolerances_standard.setter
    def iso_tolerances_standard(self, value: 'overridable.Overridable_ISOToleranceStandard.implicit_type()'):
        wrapper_type = overridable.Overridable_ISOToleranceStandard.wrapper_type()
        enclosed_type = overridable.Overridable_ISOToleranceStandard.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.ISOTolerancesStandard = value

    @property
    def agma_tolerances_standard(self) -> '_281.AGMAToleranceStandard':
        '''AGMAToleranceStandard: 'AGMATolerancesStandard' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AGMATolerancesStandard)
        return constructor.new(_281.AGMAToleranceStandard)(value) if value is not None else None

    @agma_tolerances_standard.setter
    def agma_tolerances_standard(self, value: '_281.AGMAToleranceStandard'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AGMATolerancesStandard = value

    @property
    def use_diametral_pitch(self) -> 'bool':
        '''bool: 'UseDiametralPitch' is the original name of this property.'''

        return self.wrapped.UseDiametralPitch

    @use_diametral_pitch.setter
    def use_diametral_pitch(self, value: 'bool'):
        self.wrapped.UseDiametralPitch = bool(value) if value else False

    @property
    def use_same_micro_geometry_on_both_flanks_by_default(self) -> 'bool':
        '''bool: 'UseSameMicroGeometryOnBothFlanksByDefault' is the original name of this property.'''

        return self.wrapped.UseSameMicroGeometryOnBothFlanksByDefault

    @use_same_micro_geometry_on_both_flanks_by_default.setter
    def use_same_micro_geometry_on_both_flanks_by_default(self, value: 'bool'):
        self.wrapped.UseSameMicroGeometryOnBothFlanksByDefault = bool(value) if value else False

    @property
    def micro_geometry_lead_relief_definition(self) -> '_1016.MicroGeometryConvention':
        '''MicroGeometryConvention: 'MicroGeometryLeadReliefDefinition' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MicroGeometryLeadReliefDefinition)
        return constructor.new(_1016.MicroGeometryConvention)(value) if value is not None else None

    @micro_geometry_lead_relief_definition.setter
    def micro_geometry_lead_relief_definition(self, value: '_1016.MicroGeometryConvention'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MicroGeometryLeadReliefDefinition = value

    @property
    def micro_geometry_profile_relief_definition(self) -> '_1017.MicroGeometryProfileConvention':
        '''MicroGeometryProfileConvention: 'MicroGeometryProfileReliefDefinition' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MicroGeometryProfileReliefDefinition)
        return constructor.new(_1017.MicroGeometryProfileConvention)(value) if value is not None else None

    @micro_geometry_profile_relief_definition.setter
    def micro_geometry_profile_relief_definition(self, value: '_1017.MicroGeometryProfileConvention'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MicroGeometryProfileReliefDefinition = value

    @property
    def enable_proportion_system_for_tip_alteration_coefficient(self) -> 'bool':
        '''bool: 'EnableProportionSystemForTipAlterationCoefficient' is the original name of this property.'''

        return self.wrapped.EnableProportionSystemForTipAlterationCoefficient

    @enable_proportion_system_for_tip_alteration_coefficient.setter
    def enable_proportion_system_for_tip_alteration_coefficient(self, value: 'bool'):
        self.wrapped.EnableProportionSystemForTipAlterationCoefficient = bool(value) if value else False

    @property
    def centre_tolerance_charts_at_maximum_fullness(self) -> 'bool':
        '''bool: 'CentreToleranceChartsAtMaximumFullness' is the original name of this property.'''

        return self.wrapped.CentreToleranceChartsAtMaximumFullness

    @centre_tolerance_charts_at_maximum_fullness.setter
    def centre_tolerance_charts_at_maximum_fullness(self, value: 'bool'):
        self.wrapped.CentreToleranceChartsAtMaximumFullness = bool(value) if value else False

    @property
    def shift_micro_geometry_lead_and_profile_modification_to_have_zero_maximum(self) -> 'bool':
        '''bool: 'ShiftMicroGeometryLeadAndProfileModificationToHaveZeroMaximum' is the original name of this property.'''

        return self.wrapped.ShiftMicroGeometryLeadAndProfileModificationToHaveZeroMaximum

    @shift_micro_geometry_lead_and_profile_modification_to_have_zero_maximum.setter
    def shift_micro_geometry_lead_and_profile_modification_to_have_zero_maximum(self, value: 'bool'):
        self.wrapped.ShiftMicroGeometryLeadAndProfileModificationToHaveZeroMaximum = bool(value) if value else False

    @property
    def number_of_points_for_2d_micro_geometry_plots(self) -> 'int':
        '''int: 'NumberOfPointsFor2DMicroGeometryPlots' is the original name of this property.'''

        return self.wrapped.NumberOfPointsFor2DMicroGeometryPlots

    @number_of_points_for_2d_micro_geometry_plots.setter
    def number_of_points_for_2d_micro_geometry_plots(self, value: 'int'):
        self.wrapped.NumberOfPointsFor2DMicroGeometryPlots = int(value) if value else 0

    @property
    def default_location_of_evaluation_lower_limit(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit: 'DefaultLocationOfEvaluationLowerLimit' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfEvaluationLowerLimit, value) if self.wrapped.DefaultLocationOfEvaluationLowerLimit is not None else None

    @default_location_of_evaluation_lower_limit.setter
    def default_location_of_evaluation_lower_limit(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationLowerLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfEvaluationLowerLimit = value

    @property
    def default_location_of_evaluation_upper_limit(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit: 'DefaultLocationOfEvaluationUpperLimit' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfEvaluationUpperLimit, value) if self.wrapped.DefaultLocationOfEvaluationUpperLimit is not None else None

    @default_location_of_evaluation_upper_limit.setter
    def default_location_of_evaluation_upper_limit(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfEvaluationUpperLimit.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfEvaluationUpperLimit = value

    @property
    def default_location_of_tip_relief_evaluation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation: 'DefaultLocationOfTipReliefEvaluation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfTipReliefEvaluation, value) if self.wrapped.DefaultLocationOfTipReliefEvaluation is not None else None

    @default_location_of_tip_relief_evaluation.setter
    def default_location_of_tip_relief_evaluation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfTipReliefEvaluation = value

    @property
    def main_profile_modification_ends_at_the_start_of_tip_relief_by_default(self) -> '_538.MainProfileReliefEndsAtTheStartOfTipReliefOption':
        '''MainProfileReliefEndsAtTheStartOfTipReliefOption: 'MainProfileModificationEndsAtTheStartOfTipReliefByDefault' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MainProfileModificationEndsAtTheStartOfTipReliefByDefault)
        return constructor.new(_538.MainProfileReliefEndsAtTheStartOfTipReliefOption)(value) if value is not None else None

    @main_profile_modification_ends_at_the_start_of_tip_relief_by_default.setter
    def main_profile_modification_ends_at_the_start_of_tip_relief_by_default(self, value: '_538.MainProfileReliefEndsAtTheStartOfTipReliefOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MainProfileModificationEndsAtTheStartOfTipReliefByDefault = value

    @property
    def default_location_of_tip_relief_start(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation: 'DefaultLocationOfTipReliefStart' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfTipReliefStart, value) if self.wrapped.DefaultLocationOfTipReliefStart is not None else None

    @default_location_of_tip_relief_start.setter
    def default_location_of_tip_relief_start(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfTipReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfTipReliefStart = value

    @property
    def measure_tip_reliefs_from_extrapolated_linear_relief_by_default(self) -> 'bool':
        '''bool: 'MeasureTipReliefsFromExtrapolatedLinearReliefByDefault' is the original name of this property.'''

        return self.wrapped.MeasureTipReliefsFromExtrapolatedLinearReliefByDefault

    @measure_tip_reliefs_from_extrapolated_linear_relief_by_default.setter
    def measure_tip_reliefs_from_extrapolated_linear_relief_by_default(self, value: 'bool'):
        self.wrapped.MeasureTipReliefsFromExtrapolatedLinearReliefByDefault = bool(value) if value else False

    @property
    def parabolic_tip_relief_starts_tangent_to_main_profile_relief_by_default(self) -> '_541.ParabolicTipReliefStartsTangentToMainProfileRelief':
        '''ParabolicTipReliefStartsTangentToMainProfileRelief: 'ParabolicTipReliefStartsTangentToMainProfileReliefByDefault' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ParabolicTipReliefStartsTangentToMainProfileReliefByDefault)
        return constructor.new(_541.ParabolicTipReliefStartsTangentToMainProfileRelief)(value) if value is not None else None

    @parabolic_tip_relief_starts_tangent_to_main_profile_relief_by_default.setter
    def parabolic_tip_relief_starts_tangent_to_main_profile_relief_by_default(self, value: '_541.ParabolicTipReliefStartsTangentToMainProfileRelief'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ParabolicTipReliefStartsTangentToMainProfileReliefByDefault = value

    @property
    def default_location_of_root_relief_evaluation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation: 'DefaultLocationOfRootReliefEvaluation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfRootReliefEvaluation, value) if self.wrapped.DefaultLocationOfRootReliefEvaluation is not None else None

    @default_location_of_root_relief_evaluation.setter
    def default_location_of_root_relief_evaluation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfRootReliefEvaluation = value

    @property
    def main_profile_modification_ends_at_the_start_of_root_relief_by_default(self) -> '_537.MainProfileReliefEndsAtTheStartOfRootReliefOption':
        '''MainProfileReliefEndsAtTheStartOfRootReliefOption: 'MainProfileModificationEndsAtTheStartOfRootReliefByDefault' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MainProfileModificationEndsAtTheStartOfRootReliefByDefault)
        return constructor.new(_537.MainProfileReliefEndsAtTheStartOfRootReliefOption)(value) if value is not None else None

    @main_profile_modification_ends_at_the_start_of_root_relief_by_default.setter
    def main_profile_modification_ends_at_the_start_of_root_relief_by_default(self, value: '_537.MainProfileReliefEndsAtTheStartOfRootReliefOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MainProfileModificationEndsAtTheStartOfRootReliefByDefault = value

    @property
    def default_location_of_root_relief_start(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation':
        '''enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation: 'DefaultLocationOfRootReliefStart' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DefaultLocationOfRootReliefStart, value) if self.wrapped.DefaultLocationOfRootReliefStart is not None else None

    @default_location_of_root_relief_start.setter
    def default_location_of_root_relief_start(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LocationOfRootReliefEvaluation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DefaultLocationOfRootReliefStart = value

    @property
    def measure_root_reliefs_from_extrapolated_linear_relief_by_default(self) -> 'bool':
        '''bool: 'MeasureRootReliefsFromExtrapolatedLinearReliefByDefault' is the original name of this property.'''

        return self.wrapped.MeasureRootReliefsFromExtrapolatedLinearReliefByDefault

    @measure_root_reliefs_from_extrapolated_linear_relief_by_default.setter
    def measure_root_reliefs_from_extrapolated_linear_relief_by_default(self, value: 'bool'):
        self.wrapped.MeasureRootReliefsFromExtrapolatedLinearReliefByDefault = bool(value) if value else False

    @property
    def parabolic_root_relief_starts_tangent_to_main_profile_relief_by_default(self) -> '_540.ParabolicRootReliefStartsTangentToMainProfileRelief':
        '''ParabolicRootReliefStartsTangentToMainProfileRelief: 'ParabolicRootReliefStartsTangentToMainProfileReliefByDefault' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ParabolicRootReliefStartsTangentToMainProfileReliefByDefault)
        return constructor.new(_540.ParabolicRootReliefStartsTangentToMainProfileRelief)(value) if value is not None else None

    @parabolic_root_relief_starts_tangent_to_main_profile_relief_by_default.setter
    def parabolic_root_relief_starts_tangent_to_main_profile_relief_by_default(self, value: '_540.ParabolicRootReliefStartsTangentToMainProfileRelief'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ParabolicRootReliefStartsTangentToMainProfileReliefByDefault = value
