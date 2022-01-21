'''_1713.py

LoadedRollingBearingDutyCycle
'''


from mastapy._internal import constructor
from mastapy.utility.property import (
    _1609, _1608, _1606, _1607
)
from mastapy.bearings import _1634
from mastapy.bearings.bearing_results.rolling import _1811
from mastapy.bearings.bearing_results import _1710
from mastapy._internal.python_net import python_net_import

_LOADED_ROLLING_BEARING_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedRollingBearingDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedRollingBearingDutyCycle',)


class LoadedRollingBearingDutyCycle(_1710.LoadedNonLinearBearingDutyCycleResults):
    '''LoadedRollingBearingDutyCycle

    This is a mastapy class.
    '''

    TYPE = _LOADED_ROLLING_BEARING_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedRollingBearingDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_lubricating_film_thickness(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThickness

    @property
    def minimum_lubricating_film_thickness_inner(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessInner

    @property
    def minimum_lambda_ratio(self) -> 'float':
        '''float: 'MinimumLambdaRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLambdaRatio

    @property
    def lambda_ratio_outer(self) -> 'float':
        '''float: 'LambdaRatioOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LambdaRatioOuter

    @property
    def lambda_ratio_inner(self) -> 'float':
        '''float: 'LambdaRatioInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LambdaRatioInner

    @property
    def minimum_lubricating_film_thickness_outer(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessOuter

    @property
    def iso2812007_basic_rating_life_time(self) -> 'float':
        '''float: 'ISO2812007BasicRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007BasicRatingLifeTime

    @property
    def iso2812007_basic_rating_life_reliability(self) -> 'float':
        '''float: 'ISO2812007BasicRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007BasicRatingLifeReliability

    @property
    def iso2812007_basic_rating_life_unreliability(self) -> 'float':
        '''float: 'ISO2812007BasicRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007BasicRatingLifeUnreliability

    @property
    def iso2812007_modified_rating_life_reliability(self) -> 'float':
        '''float: 'ISO2812007ModifiedRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007ModifiedRatingLifeReliability

    @property
    def iso2812007_modified_rating_life_unreliability(self) -> 'float':
        '''float: 'ISO2812007ModifiedRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007ModifiedRatingLifeUnreliability

    @property
    def isots162812008_basic_reference_rating_life_reliability(self) -> 'float':
        '''float: 'ISOTS162812008BasicReferenceRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008BasicReferenceRatingLifeReliability

    @property
    def isots162812008_basic_reference_rating_life_unreliability(self) -> 'float':
        '''float: 'ISOTS162812008BasicReferenceRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008BasicReferenceRatingLifeUnreliability

    @property
    def isots162812008_modified_reference_rating_life_reliability(self) -> 'float':
        '''float: 'ISOTS162812008ModifiedReferenceRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008ModifiedReferenceRatingLifeReliability

    @property
    def isots162812008_modified_reference_rating_life_unreliability(self) -> 'float':
        '''float: 'ISOTS162812008ModifiedReferenceRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008ModifiedReferenceRatingLifeUnreliability

    @property
    def skf_bearing_rating_life_reliability(self) -> 'float':
        '''float: 'SKFBearingRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SKFBearingRatingLifeReliability

    @property
    def skf_bearing_rating_life_unreliability(self) -> 'float':
        '''float: 'SKFBearingRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SKFBearingRatingLifeUnreliability

    @property
    def ansiabma_basic_rating_life_reliability(self) -> 'float':
        '''float: 'ANSIABMABasicRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMABasicRatingLifeReliability

    @property
    def ansiabma_basic_rating_life_unreliability(self) -> 'float':
        '''float: 'ANSIABMABasicRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMABasicRatingLifeUnreliability

    @property
    def ansiabma_adjusted_rating_life_reliability(self) -> 'float':
        '''float: 'ANSIABMAAdjustedRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMAAdjustedRatingLifeReliability

    @property
    def ansiabma_adjusted_rating_life_unreliability(self) -> 'float':
        '''float: 'ANSIABMAAdjustedRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMAAdjustedRatingLifeUnreliability

    @property
    def iso2812007_modified_rating_life_time(self) -> 'float':
        '''float: 'ISO2812007ModifiedRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007ModifiedRatingLifeTime

    @property
    def isots162812008_basic_reference_rating_life_time(self) -> 'float':
        '''float: 'ISOTS162812008BasicReferenceRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008BasicReferenceRatingLifeTime

    @property
    def isots162812008_modified_reference_rating_life_time(self) -> 'float':
        '''float: 'ISOTS162812008ModifiedReferenceRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008ModifiedReferenceRatingLifeTime

    @property
    def skf_bearing_rating_life_time(self) -> 'float':
        '''float: 'SKFBearingRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SKFBearingRatingLifeTime

    @property
    def ansiabma_basic_rating_life_time(self) -> 'float':
        '''float: 'ANSIABMABasicRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMABasicRatingLifeTime

    @property
    def ansiabma_adjusted_rating_life_time(self) -> 'float':
        '''float: 'ANSIABMAAdjustedRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMAAdjustedRatingLifeTime

    @property
    def iso2812007_basic_rating_life_damage(self) -> 'float':
        '''float: 'ISO2812007BasicRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007BasicRatingLifeDamage

    @property
    def iso2812007_modified_rating_life_damage(self) -> 'float':
        '''float: 'ISO2812007ModifiedRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007ModifiedRatingLifeDamage

    @property
    def isots162812008_modified_reference_rating_life_damage(self) -> 'float':
        '''float: 'ISOTS162812008ModifiedReferenceRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008ModifiedReferenceRatingLifeDamage

    @property
    def isots162812008_basic_reference_rating_life_damage(self) -> 'float':
        '''float: 'ISOTS162812008BasicReferenceRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008BasicReferenceRatingLifeDamage

    @property
    def skf_bearing_rating_life_damage(self) -> 'float':
        '''float: 'SKFBearingRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SKFBearingRatingLifeDamage

    @property
    def ansiabma_basic_rating_life_damage(self) -> 'float':
        '''float: 'ANSIABMABasicRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMABasicRatingLifeDamage

    @property
    def ansiabma_adjusted_rating_life_damage(self) -> 'float':
        '''float: 'ANSIABMAAdjustedRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMAAdjustedRatingLifeDamage

    @property
    def maximum_element_normal_stress(self) -> 'float':
        '''float: 'MaximumElementNormalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumElementNormalStress

    @property
    def iso762006_recommended_maximum_element_normal_stress(self) -> 'float':
        '''float: 'ISO762006RecommendedMaximumElementNormalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO762006RecommendedMaximumElementNormalStress

    @property
    def iso2812007_dynamic_equivalent_load(self) -> 'float':
        '''float: 'ISO2812007DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007DynamicEquivalentLoad

    @property
    def isots162812008_dynamic_equivalent_load(self) -> 'float':
        '''float: 'ISOTS162812008DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008DynamicEquivalentLoad

    @property
    def ansiabma_dynamic_equivalent_load(self) -> 'float':
        '''float: 'ANSIABMADynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMADynamicEquivalentLoad

    @property
    def iso2812007_basic_rating_life_safety_factor(self) -> 'float':
        '''float: 'ISO2812007BasicRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007BasicRatingLifeSafetyFactor

    @property
    def iso2812007_modified_rating_life_safety_factor(self) -> 'float':
        '''float: 'ISO2812007ModifiedRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO2812007ModifiedRatingLifeSafetyFactor

    @property
    def isots162812008_basic_reference_rating_life_safety_factor(self) -> 'float':
        '''float: 'ISOTS162812008BasicReferenceRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008BasicReferenceRatingLifeSafetyFactor

    @property
    def isots162812008_modified_reference_rating_life_safety_factor(self) -> 'float':
        '''float: 'ISOTS162812008ModifiedReferenceRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISOTS162812008ModifiedReferenceRatingLifeSafetyFactor

    @property
    def ansiabma_basic_rating_life_safety_factor(self) -> 'float':
        '''float: 'ANSIABMABasicRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMABasicRatingLifeSafetyFactor

    @property
    def ansiabma_adjusted_rating_life_safety_factor(self) -> 'float':
        '''float: 'ANSIABMAAdjustedRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ANSIABMAAdjustedRatingLifeSafetyFactor

    @property
    def worst_iso762006_safety_factor_static_equivalent_load_capacity_ratio(self) -> 'float':
        '''float: 'WorstISO762006SafetyFactorStaticEquivalentLoadCapacityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstISO762006SafetyFactorStaticEquivalentLoadCapacityRatio

    @property
    def worst_ansiabma_static_safety_factor(self) -> 'float':
        '''float: 'WorstANSIABMAStaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstANSIABMAStaticSafetyFactor

    @property
    def static_equivalent_load_capacity_ratio_limit(self) -> 'float':
        '''float: 'StaticEquivalentLoadCapacityRatioLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticEquivalentLoadCapacityRatioLimit

    @property
    def maximum_element_normal_stress_inner_summary(self) -> '_1609.DutyCyclePropertySummaryStress[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryStress[BearingLoadCaseResultsLightweight]: 'MaximumElementNormalStressInnerSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1609.DutyCyclePropertySummaryStress)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.MaximumElementNormalStressInnerSummary) if self.wrapped.MaximumElementNormalStressInnerSummary is not None else None

    @property
    def maximum_element_normal_stress_outer_summary(self) -> '_1609.DutyCyclePropertySummaryStress[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryStress[BearingLoadCaseResultsLightweight]: 'MaximumElementNormalStressOuterSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1609.DutyCyclePropertySummaryStress)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.MaximumElementNormalStressOuterSummary) if self.wrapped.MaximumElementNormalStressOuterSummary is not None else None

    @property
    def maximum_element_normal_stress_summary(self) -> '_1609.DutyCyclePropertySummaryStress[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryStress[BearingLoadCaseResultsLightweight]: 'MaximumElementNormalStressSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1609.DutyCyclePropertySummaryStress)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.MaximumElementNormalStressSummary) if self.wrapped.MaximumElementNormalStressSummary is not None else None

    @property
    def misalignment_summary(self) -> '_1608.DutyCyclePropertySummarySmallAngle[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummarySmallAngle[BearingLoadCaseResultsLightweight]: 'MisalignmentSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1608.DutyCyclePropertySummarySmallAngle)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.MisalignmentSummary) if self.wrapped.MisalignmentSummary is not None else None

    @property
    def iso2812007_dynamic_equivalent_load_summary(self) -> '_1606.DutyCyclePropertySummaryForce[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryForce[BearingLoadCaseResultsLightweight]: 'ISO2812007DynamicEquivalentLoadSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1606.DutyCyclePropertySummaryForce)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.ISO2812007DynamicEquivalentLoadSummary) if self.wrapped.ISO2812007DynamicEquivalentLoadSummary is not None else None

    @property
    def isots162812008_dynamic_equivalent_load_summary(self) -> '_1606.DutyCyclePropertySummaryForce[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryForce[BearingLoadCaseResultsLightweight]: 'ISOTS162812008DynamicEquivalentLoadSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1606.DutyCyclePropertySummaryForce)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.ISOTS162812008DynamicEquivalentLoadSummary) if self.wrapped.ISOTS162812008DynamicEquivalentLoadSummary is not None else None

    @property
    def ansiabma_dynamic_equivalent_load_summary(self) -> '_1606.DutyCyclePropertySummaryForce[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryForce[BearingLoadCaseResultsLightweight]: 'ANSIABMADynamicEquivalentLoadSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1606.DutyCyclePropertySummaryForce)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.ANSIABMADynamicEquivalentLoadSummary) if self.wrapped.ANSIABMADynamicEquivalentLoadSummary is not None else None

    @property
    def maximum_truncation_summary(self) -> '_1607.DutyCyclePropertySummaryPercentage[_1634.BearingLoadCaseResultsLightweight]':
        '''DutyCyclePropertySummaryPercentage[BearingLoadCaseResultsLightweight]: 'MaximumTruncationSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1607.DutyCyclePropertySummaryPercentage)[_1634.BearingLoadCaseResultsLightweight](self.wrapped.MaximumTruncationSummary) if self.wrapped.MaximumTruncationSummary is not None else None

    @property
    def maximum_static_contact_stress_duty_cycle(self) -> '_1811.MaximumStaticContactStressDutyCycle':
        '''MaximumStaticContactStressDutyCycle: 'MaximumStaticContactStressDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1811.MaximumStaticContactStressDutyCycle)(self.wrapped.MaximumStaticContactStressDutyCycle) if self.wrapped.MaximumStaticContactStressDutyCycle is not None else None
