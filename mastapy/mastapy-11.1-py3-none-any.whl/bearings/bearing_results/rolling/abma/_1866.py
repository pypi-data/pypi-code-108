'''_1866.py

ANSIABMAResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.iso_rating_results import _1855
from mastapy._internal.python_net import python_net_import

_ANSIABMA_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.ABMA', 'ANSIABMAResults')


__docformat__ = 'restructuredtext en'
__all__ = ('ANSIABMAResults',)


class ANSIABMAResults(_1855.ISOResults):
    '''ANSIABMAResults

    This is a mastapy class.
    '''

    TYPE = _ANSIABMA_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ANSIABMAResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def static_safety_factor(self) -> 'float':
        '''float: 'StaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactor

    @property
    def bearing_life_adjustment_factor_for_special_bearing_properties(self) -> 'float':
        '''float: 'BearingLifeAdjustmentFactorForSpecialBearingProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BearingLifeAdjustmentFactorForSpecialBearingProperties

    @property
    def bearing_life_adjustment_factor_for_operating_conditions(self) -> 'float':
        '''float: 'BearingLifeAdjustmentFactorForOperatingConditions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BearingLifeAdjustmentFactorForOperatingConditions

    @property
    def basic_rating_life_reliability(self) -> 'float':
        '''float: 'BasicRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeReliability

    @property
    def adjusted_rating_life_reliability(self) -> 'float':
        '''float: 'AdjustedRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeReliability

    @property
    def adjusted_rating_life_time(self) -> 'float':
        '''float: 'AdjustedRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeTime

    @property
    def basic_rating_life_safety_factor(self) -> 'float':
        '''float: 'BasicRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeSafetyFactor

    @property
    def basic_rating_life_time(self) -> 'float':
        '''float: 'BasicRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeTime

    @property
    def adjusted_rating_life_safety_factor(self) -> 'float':
        '''float: 'AdjustedRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeSafetyFactor

    @property
    def basic_rating_life_cycles(self) -> 'float':
        '''float: 'BasicRatingLifeCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeCycles

    @property
    def adjusted_rating_life_cycles(self) -> 'float':
        '''float: 'AdjustedRatingLifeCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeCycles

    @property
    def dynamic_equivalent_load(self) -> 'float':
        '''float: 'DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicEquivalentLoad

    @property
    def dynamic_radial_load_factor(self) -> 'float':
        '''float: 'DynamicRadialLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicRadialLoadFactor

    @property
    def dynamic_axial_load_factor(self) -> 'float':
        '''float: 'DynamicAxialLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicAxialLoadFactor

    @property
    def e_limiting_value_for_dynamic_equivalent_load(self) -> 'float':
        '''float: 'ELimitingValueForDynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ELimitingValueForDynamicEquivalentLoad

    @property
    def axial_to_radial_load_ratio(self) -> 'float':
        '''float: 'AxialToRadialLoadRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialToRadialLoadRatio

    @property
    def basic_rating_life_damage_rate(self) -> 'float':
        '''float: 'BasicRatingLifeDamageRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeDamageRate

    @property
    def adjusted_rating_life_damage_rate(self) -> 'float':
        '''float: 'AdjustedRatingLifeDamageRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeDamageRate

    @property
    def basic_rating_life_damage(self) -> 'float':
        '''float: 'BasicRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeDamage

    @property
    def adjusted_rating_life_damage(self) -> 'float':
        '''float: 'AdjustedRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeDamage

    @property
    def basic_rating_life_unreliability(self) -> 'float':
        '''float: 'BasicRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRatingLifeUnreliability

    @property
    def adjusted_rating_life_unreliability(self) -> 'float':
        '''float: 'AdjustedRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedRatingLifeUnreliability
