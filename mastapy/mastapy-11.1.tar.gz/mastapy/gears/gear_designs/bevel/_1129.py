'''_1129.py

BevelGearSetDesign
'''


from mastapy.gears.gear_designs.conical import _1098
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.math_utility import _1318
from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.bevel import _1137, _1138, _1136
from mastapy.gears import _313
from mastapy.gears.gear_designs.agma_gleason_conical import _1142
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'BevelGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetDesign',)


class BevelGearSetDesign(_1142.AGMAGleasonConicalGearSetDesign):
    '''BevelGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def backlash_distribution_rule(self) -> '_1098.BacklashDistributionRule':
        '''BacklashDistributionRule: 'BacklashDistributionRule' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.BacklashDistributionRule)
        return constructor.new(_1098.BacklashDistributionRule)(value) if value is not None else None

    @backlash_distribution_rule.setter
    def backlash_distribution_rule(self, value: '_1098.BacklashDistributionRule'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.BacklashDistributionRule = value

    @property
    def backlash_used_for_tooth_thickness_calculation(self) -> '_1318.MaxMinMean':
        '''MaxMinMean: 'BacklashUsedForToothThicknessCalculation' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.BacklashUsedForToothThicknessCalculation)
        return constructor.new(_1318.MaxMinMean)(value) if value is not None else None

    @backlash_used_for_tooth_thickness_calculation.setter
    def backlash_used_for_tooth_thickness_calculation(self, value: '_1318.MaxMinMean'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.BacklashUsedForToothThicknessCalculation = value

    @property
    def ideal_circular_thickness_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'IdealCircularThicknessFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.IdealCircularThicknessFactor) if self.wrapped.IdealCircularThicknessFactor is not None else None

    @ideal_circular_thickness_factor.setter
    def ideal_circular_thickness_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.IdealCircularThicknessFactor = value

    @property
    def strength_factor(self) -> 'float':
        '''float: 'StrengthFactor' is the original name of this property.'''

        return self.wrapped.StrengthFactor

    @strength_factor.setter
    def strength_factor(self, value: 'float'):
        self.wrapped.StrengthFactor = float(value) if value else 0.0

    @property
    def circular_thickness_factor(self) -> 'float':
        '''float: 'CircularThicknessFactor' is the original name of this property.'''

        return self.wrapped.CircularThicknessFactor

    @circular_thickness_factor.setter
    def circular_thickness_factor(self, value: 'float'):
        self.wrapped.CircularThicknessFactor = float(value) if value else 0.0

    @property
    def ideal_pinion_outer_transverse_circular_thickness(self) -> 'float':
        '''float: 'IdealPinionOuterTransverseCircularThickness' is the original name of this property.'''

        return self.wrapped.IdealPinionOuterTransverseCircularThickness

    @ideal_pinion_outer_transverse_circular_thickness.setter
    def ideal_pinion_outer_transverse_circular_thickness(self, value: 'float'):
        self.wrapped.IdealPinionOuterTransverseCircularThickness = float(value) if value else 0.0

    @property
    def ideal_pinion_mean_transverse_circular_thickness(self) -> 'float':
        '''float: 'IdealPinionMeanTransverseCircularThickness' is the original name of this property.'''

        return self.wrapped.IdealPinionMeanTransverseCircularThickness

    @ideal_pinion_mean_transverse_circular_thickness.setter
    def ideal_pinion_mean_transverse_circular_thickness(self, value: 'float'):
        self.wrapped.IdealPinionMeanTransverseCircularThickness = float(value) if value else 0.0

    @property
    def ideal_wheel_mean_slot_width(self) -> 'float':
        '''float: 'IdealWheelMeanSlotWidth' is the original name of this property.'''

        return self.wrapped.IdealWheelMeanSlotWidth

    @ideal_wheel_mean_slot_width.setter
    def ideal_wheel_mean_slot_width(self, value: 'float'):
        self.wrapped.IdealWheelMeanSlotWidth = float(value) if value else 0.0

    @property
    def ideal_wheel_finish_cutter_point_width(self) -> 'float':
        '''float: 'IdealWheelFinishCutterPointWidth' is the original name of this property.'''

        return self.wrapped.IdealWheelFinishCutterPointWidth

    @ideal_wheel_finish_cutter_point_width.setter
    def ideal_wheel_finish_cutter_point_width(self, value: 'float'):
        self.wrapped.IdealWheelFinishCutterPointWidth = float(value) if value else 0.0

    @property
    def wheel_finish_cutter_point_width(self) -> 'float':
        '''float: 'WheelFinishCutterPointWidth' is the original name of this property.'''

        return self.wrapped.WheelFinishCutterPointWidth

    @wheel_finish_cutter_point_width.setter
    def wheel_finish_cutter_point_width(self, value: 'float'):
        self.wrapped.WheelFinishCutterPointWidth = float(value) if value else 0.0

    @property
    def tooth_thickness_specification_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ToothThicknessSpecificationMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_ToothThicknessSpecificationMethod: 'ToothThicknessSpecificationMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ToothThicknessSpecificationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ToothThicknessSpecificationMethod, value) if self.wrapped.ToothThicknessSpecificationMethod is not None else None

    @tooth_thickness_specification_method.setter
    def tooth_thickness_specification_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ToothThicknessSpecificationMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ToothThicknessSpecificationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ToothThicknessSpecificationMethod = value

    @property
    def round_cutter_specifications(self) -> '_1138.WheelFinishCutterPointWidthRestrictionMethod':
        '''WheelFinishCutterPointWidthRestrictionMethod: 'RoundCutterSpecifications' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.RoundCutterSpecifications)
        return constructor.new(_1138.WheelFinishCutterPointWidthRestrictionMethod)(value) if value is not None else None

    @round_cutter_specifications.setter
    def round_cutter_specifications(self, value: '_1138.WheelFinishCutterPointWidthRestrictionMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.RoundCutterSpecifications = value

    @property
    def pressure_angle(self) -> 'float':
        '''float: 'PressureAngle' is the original name of this property.'''

        return self.wrapped.PressureAngle

    @pressure_angle.setter
    def pressure_angle(self, value: 'float'):
        self.wrapped.PressureAngle = float(value) if value else 0.0

    @property
    def allowable_scoring_index(self) -> 'float':
        '''float: 'AllowableScoringIndex' is the original name of this property.'''

        return self.wrapped.AllowableScoringIndex

    @allowable_scoring_index.setter
    def allowable_scoring_index(self, value: 'float'):
        self.wrapped.AllowableScoringIndex = float(value) if value else 0.0

    @property
    def factor_of_safety_for_scoring(self) -> 'float':
        '''float: 'FactorOfSafetyForScoring' is the original name of this property.'''

        return self.wrapped.FactorOfSafetyForScoring

    @factor_of_safety_for_scoring.setter
    def factor_of_safety_for_scoring(self, value: 'float'):
        self.wrapped.FactorOfSafetyForScoring = float(value) if value else 0.0

    @property
    def tooth_taper_root_line_tilt_method(self) -> '_313.SpiralBevelRootLineTilt':
        '''SpiralBevelRootLineTilt: 'ToothTaperRootLineTiltMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ToothTaperRootLineTiltMethod)
        return constructor.new(_313.SpiralBevelRootLineTilt)(value) if value is not None else None

    @tooth_taper_root_line_tilt_method.setter
    def tooth_taper_root_line_tilt_method(self, value: '_313.SpiralBevelRootLineTilt'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ToothTaperRootLineTiltMethod = value

    @property
    def minimum_number_of_teeth_for_recommended_tooth_proportions(self) -> 'int':
        '''int: 'MinimumNumberOfTeethForRecommendedToothProportions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumNumberOfTeethForRecommendedToothProportions

    @property
    def diametral_pitch(self) -> 'float':
        '''float: 'DiametralPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DiametralPitch

    @property
    def mean_circular_pitch(self) -> 'float':
        '''float: 'MeanCircularPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCircularPitch

    @property
    def mean_diametral_pitch(self) -> 'float':
        '''float: 'MeanDiametralPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanDiametralPitch

    @property
    def wheel_inner_spiral_angle(self) -> 'float':
        '''float: 'WheelInnerSpiralAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInnerSpiralAngle

    @property
    def tooth_proportions_input_method(self) -> '_1136.ToothProportionsInputMethod':
        '''ToothProportionsInputMethod: 'ToothProportionsInputMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ToothProportionsInputMethod)
        return constructor.new(_1136.ToothProportionsInputMethod)(value) if value is not None else None

    @tooth_proportions_input_method.setter
    def tooth_proportions_input_method(self, value: '_1136.ToothProportionsInputMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ToothProportionsInputMethod = value

    @property
    def use_recommended_tooth_proportions(self) -> 'bool':
        '''bool: 'UseRecommendedToothProportions' is the original name of this property.'''

        return self.wrapped.UseRecommendedToothProportions

    @use_recommended_tooth_proportions.setter
    def use_recommended_tooth_proportions(self, value: 'bool'):
        self.wrapped.UseRecommendedToothProportions = bool(value) if value else False

    @property
    def whole_depth_factor(self) -> 'float':
        '''float: 'WholeDepthFactor' is the original name of this property.'''

        return self.wrapped.WholeDepthFactor

    @whole_depth_factor.setter
    def whole_depth_factor(self, value: 'float'):
        self.wrapped.WholeDepthFactor = float(value) if value else 0.0

    @property
    def working_depth_factor(self) -> 'float':
        '''float: 'WorkingDepthFactor' is the original name of this property.'''

        return self.wrapped.WorkingDepthFactor

    @working_depth_factor.setter
    def working_depth_factor(self, value: 'float'):
        self.wrapped.WorkingDepthFactor = float(value) if value else 0.0

    @property
    def wheel_addendum_factor(self) -> 'float':
        '''float: 'WheelAddendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAddendumFactor

    @property
    def wheel_addendum_multiplier(self) -> 'float':
        '''float: 'WheelAddendumMultiplier' is the original name of this property.'''

        return self.wrapped.WheelAddendumMultiplier

    @wheel_addendum_multiplier.setter
    def wheel_addendum_multiplier(self, value: 'float'):
        self.wrapped.WheelAddendumMultiplier = float(value) if value else 0.0

    @property
    def mean_depth_factor(self) -> 'float':
        '''float: 'MeanDepthFactor' is the original name of this property.'''

        return self.wrapped.MeanDepthFactor

    @mean_depth_factor.setter
    def mean_depth_factor(self, value: 'float'):
        self.wrapped.MeanDepthFactor = float(value) if value else 0.0

    @property
    def mean_clearance_factor(self) -> 'float':
        '''float: 'MeanClearanceFactor' is the original name of this property.'''

        return self.wrapped.MeanClearanceFactor

    @mean_clearance_factor.setter
    def mean_clearance_factor(self, value: 'float'):
        self.wrapped.MeanClearanceFactor = float(value) if value else 0.0

    @property
    def mean_addendum_factor(self) -> 'float':
        '''float: 'MeanAddendumFactor' is the original name of this property.'''

        return self.wrapped.MeanAddendumFactor

    @mean_addendum_factor.setter
    def mean_addendum_factor(self, value: 'float'):
        self.wrapped.MeanAddendumFactor = float(value) if value else 0.0

    @property
    def specified_pinion_dedendum_angle(self) -> 'float':
        '''float: 'SpecifiedPinionDedendumAngle' is the original name of this property.'''

        return self.wrapped.SpecifiedPinionDedendumAngle

    @specified_pinion_dedendum_angle.setter
    def specified_pinion_dedendum_angle(self, value: 'float'):
        self.wrapped.SpecifiedPinionDedendumAngle = float(value) if value else 0.0

    @property
    def specified_wheel_dedendum_angle(self) -> 'float':
        '''float: 'SpecifiedWheelDedendumAngle' is the original name of this property.'''

        return self.wrapped.SpecifiedWheelDedendumAngle

    @specified_wheel_dedendum_angle.setter
    def specified_wheel_dedendum_angle(self, value: 'float'):
        self.wrapped.SpecifiedWheelDedendumAngle = float(value) if value else 0.0

    @property
    def profile_shift_coefficient(self) -> 'float':
        '''float: 'ProfileShiftCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileShiftCoefficient

    @property
    def basic_crown_gear_addendum_factor(self) -> 'float':
        '''float: 'BasicCrownGearAddendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicCrownGearAddendumFactor

    @property
    def basic_crown_gear_dedendum_factor(self) -> 'float':
        '''float: 'BasicCrownGearDedendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicCrownGearDedendumFactor

    @property
    def thickness_modification_coefficient_theoretical(self) -> 'float':
        '''float: 'ThicknessModificationCoefficientTheoretical' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThicknessModificationCoefficientTheoretical

    @property
    def outer_wheel_addendum(self) -> 'float':
        '''float: 'OuterWheelAddendum' is the original name of this property.'''

        return self.wrapped.OuterWheelAddendum

    @outer_wheel_addendum.setter
    def outer_wheel_addendum(self, value: 'float'):
        self.wrapped.OuterWheelAddendum = float(value) if value else 0.0

    @property
    def clearance(self) -> 'float':
        '''float: 'Clearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Clearance

    @property
    def outer_whole_depth(self) -> 'float':
        '''float: 'OuterWholeDepth' is the original name of this property.'''

        return self.wrapped.OuterWholeDepth

    @outer_whole_depth.setter
    def outer_whole_depth(self, value: 'float'):
        self.wrapped.OuterWholeDepth = float(value) if value else 0.0

    @property
    def outer_working_depth(self) -> 'float':
        '''float: 'OuterWorkingDepth' is the original name of this property.'''

        return self.wrapped.OuterWorkingDepth

    @outer_working_depth.setter
    def outer_working_depth(self, value: 'float'):
        self.wrapped.OuterWorkingDepth = float(value) if value else 0.0

    @property
    def mean_working_depth(self) -> 'float':
        '''float: 'MeanWorkingDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanWorkingDepth

    @property
    def mean_whole_depth(self) -> 'float':
        '''float: 'MeanWholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanWholeDepth

    @property
    def transverse_circular_thickness_factor(self) -> 'float':
        '''float: 'TransverseCircularThicknessFactor' is the original name of this property.'''

        return self.wrapped.TransverseCircularThicknessFactor

    @transverse_circular_thickness_factor.setter
    def transverse_circular_thickness_factor(self, value: 'float'):
        self.wrapped.TransverseCircularThicknessFactor = float(value) if value else 0.0

    @property
    def mean_spiral_angle(self) -> 'float':
        '''float: 'MeanSpiralAngle' is the original name of this property.'''

        return self.wrapped.MeanSpiralAngle

    @mean_spiral_angle.setter
    def mean_spiral_angle(self, value: 'float'):
        self.wrapped.MeanSpiralAngle = float(value) if value else 0.0
