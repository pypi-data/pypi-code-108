'''_1856.py

ISOTS162812008Results
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.iso_rating_results import _1855
from mastapy._internal.python_net import python_net_import

_ISOTS162812008_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.IsoRatingResults', 'ISOTS162812008Results')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOTS162812008Results',)


class ISOTS162812008Results(_1855.ISOResults):
    '''ISOTS162812008Results

    This is a mastapy class.
    '''

    TYPE = _ISOTS162812008_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISOTS162812008Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_for_the_basic_dynamic_load_rating_of_the_inner_ring_or_shaft_washer(self) -> 'float':
        '''float: 'LoadForTheBasicDynamicLoadRatingOfTheInnerRingOrShaftWasher' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadForTheBasicDynamicLoadRatingOfTheInnerRingOrShaftWasher

    @property
    def load_for_the_basic_dynamic_load_rating_of_the_outer_ring_or_housing_washer(self) -> 'float':
        '''float: 'LoadForTheBasicDynamicLoadRatingOfTheOuterRingOrHousingWasher' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadForTheBasicDynamicLoadRatingOfTheOuterRingOrHousingWasher

    @property
    def life_modification_factor_for_systems_approach(self) -> 'float':
        '''float: 'LifeModificationFactorForSystemsApproach' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeModificationFactorForSystemsApproach

    @property
    def basic_reference_rating_life_safety_factor(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeSafetyFactor

    @property
    def modified_reference_rating_life_safety_factor(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeSafetyFactor

    @property
    def basic_reference_rating_life_time(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeTime

    @property
    def modified_reference_rating_life_time(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeTime

    @property
    def basic_reference_rating_life_damage(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeDamage

    @property
    def basic_reference_rating_life_reliability(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeReliability

    @property
    def modified_reference_rating_life_reliability(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeReliability

    @property
    def modified_reference_rating_life_damage(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeDamage

    @property
    def basic_reference_rating_life_cycles(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeCycles

    @property
    def modified_reference_rating_life_cycles(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeCycles

    @property
    def basic_reference_rating_life_damage_rate(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeDamageRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeDamageRate

    @property
    def modified_reference_rating_life_damage_rate(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeDamageRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeDamageRate

    @property
    def dynamic_equivalent_reference_load(self) -> 'float':
        '''float: 'DynamicEquivalentReferenceLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicEquivalentReferenceLoad

    @property
    def dynamic_equivalent_load_dynamic_capacity_ratio(self) -> 'float':
        '''float: 'DynamicEquivalentLoadDynamicCapacityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicEquivalentLoadDynamicCapacityRatio

    @property
    def basic_reference_rating_life_unreliability(self) -> 'float':
        '''float: 'BasicReferenceRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicReferenceRatingLifeUnreliability

    @property
    def modified_reference_rating_life_unreliability(self) -> 'float':
        '''float: 'ModifiedReferenceRatingLifeUnreliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedReferenceRatingLifeUnreliability
