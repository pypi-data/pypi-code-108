'''_1727.py

ISO14179Settings
'''


from mastapy.bearings.bearing_results.rolling import _1815
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.math_utility.measured_data import _1367, _1368
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_ISO14179_SETTINGS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'ISO14179Settings')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO14179Settings',)


class ISO14179Settings(_1597.NamedDatabaseItem):
    '''ISO14179Settings

    This is a mastapy class.
    '''

    TYPE = _ISO14179_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO14179Settings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def isotr141792001f1_specification_method(self) -> '_1815.PowerRatingF1EstimationMethod':
        '''PowerRatingF1EstimationMethod: 'ISOTR141792001F1SpecificationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ISOTR141792001F1SpecificationMethod)
        return constructor.new(_1815.PowerRatingF1EstimationMethod)(value) if value is not None else None

    @isotr141792001f1_specification_method.setter
    def isotr141792001f1_specification_method(self, value: '_1815.PowerRatingF1EstimationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ISOTR141792001F1SpecificationMethod = value

    @property
    def user_specified_f1_for_isotr141792001(self) -> 'float':
        '''float: 'UserSpecifiedF1ForISOTR141792001' is the original name of this property.'''

        return self.wrapped.UserSpecifiedF1ForISOTR141792001

    @user_specified_f1_for_isotr141792001.setter
    def user_specified_f1_for_isotr141792001(self, value: 'float'):
        self.wrapped.UserSpecifiedF1ForISOTR141792001 = float(value) if value else 0.0

    @property
    def power_rating_f1_one_dimensional_lookup_table(self) -> '_1367.OnedimensionalFunctionLookupTable':
        '''OnedimensionalFunctionLookupTable: 'PowerRatingF1OneDimensionalLookupTable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1367.OnedimensionalFunctionLookupTable)(self.wrapped.PowerRatingF1OneDimensionalLookupTable) if self.wrapped.PowerRatingF1OneDimensionalLookupTable is not None else None

    @property
    def power_rating_f1_two_dimensional_lookup_table(self) -> '_1368.TwodimensionalFunctionLookupTable':
        '''TwodimensionalFunctionLookupTable: 'PowerRatingF1TwoDimensionalLookupTable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1368.TwodimensionalFunctionLookupTable)(self.wrapped.PowerRatingF1TwoDimensionalLookupTable) if self.wrapped.PowerRatingF1TwoDimensionalLookupTable is not None else None

    @property
    def power_rating_f1_scaling_factor_one_dimensional_lookup_table(self) -> '_1367.OnedimensionalFunctionLookupTable':
        '''OnedimensionalFunctionLookupTable: 'PowerRatingF1ScalingFactorOneDimensionalLookupTable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1367.OnedimensionalFunctionLookupTable)(self.wrapped.PowerRatingF1ScalingFactorOneDimensionalLookupTable) if self.wrapped.PowerRatingF1ScalingFactorOneDimensionalLookupTable is not None else None

    @property
    def power_rating_f0_scaling_factor_one_dimensional_lookup_table(self) -> '_1367.OnedimensionalFunctionLookupTable':
        '''OnedimensionalFunctionLookupTable: 'PowerRatingF0ScalingFactorOneDimensionalLookupTable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1367.OnedimensionalFunctionLookupTable)(self.wrapped.PowerRatingF0ScalingFactorOneDimensionalLookupTable) if self.wrapped.PowerRatingF0ScalingFactorOneDimensionalLookupTable is not None else None
