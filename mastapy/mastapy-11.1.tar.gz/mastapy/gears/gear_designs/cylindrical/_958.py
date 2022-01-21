'''_958.py

CaseHardeningProperties
'''


from mastapy.gears.gear_designs.cylindrical import _1007, _1008
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CASE_HARDENING_PROPERTIES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CaseHardeningProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('CaseHardeningProperties',)


class CaseHardeningProperties(_0.APIBase):
    '''CaseHardeningProperties

    This is a mastapy class.
    '''

    TYPE = _CASE_HARDENING_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CaseHardeningProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hardness_profile_calculation_method(self) -> '_1007.HardnessProfileCalculationMethod':
        '''HardnessProfileCalculationMethod: 'HardnessProfileCalculationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.HardnessProfileCalculationMethod)
        return constructor.new(_1007.HardnessProfileCalculationMethod)(value) if value is not None else None

    @hardness_profile_calculation_method.setter
    def hardness_profile_calculation_method(self, value: '_1007.HardnessProfileCalculationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.HardnessProfileCalculationMethod = value

    @property
    def heat_treatment_type(self) -> '_1008.HeatTreatmentType':
        '''HeatTreatmentType: 'HeatTreatmentType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.HeatTreatmentType)
        return constructor.new(_1008.HeatTreatmentType)(value) if value is not None else None

    @property
    def total_case_depth(self) -> 'float':
        '''float: 'TotalCaseDepth' is the original name of this property.'''

        return self.wrapped.TotalCaseDepth

    @total_case_depth.setter
    def total_case_depth(self, value: 'float'):
        self.wrapped.TotalCaseDepth = float(value) if value else 0.0

    @property
    def depth_at_maximum_hardness(self) -> 'float':
        '''float: 'DepthAtMaximumHardness' is the original name of this property.'''

        return self.wrapped.DepthAtMaximumHardness

    @depth_at_maximum_hardness.setter
    def depth_at_maximum_hardness(self, value: 'float'):
        self.wrapped.DepthAtMaximumHardness = float(value) if value else 0.0

    @property
    def effective_case_depth(self) -> 'float':
        '''float: 'EffectiveCaseDepth' is the original name of this property.'''

        return self.wrapped.EffectiveCaseDepth

    @effective_case_depth.setter
    def effective_case_depth(self, value: 'float'):
        self.wrapped.EffectiveCaseDepth = float(value) if value else 0.0

    @property
    def vickers_hardness_hv_at_effective_case_depth(self) -> 'float':
        '''float: 'VickersHardnessHVAtEffectiveCaseDepth' is the original name of this property.'''

        return self.wrapped.VickersHardnessHVAtEffectiveCaseDepth

    @vickers_hardness_hv_at_effective_case_depth.setter
    def vickers_hardness_hv_at_effective_case_depth(self, value: 'float'):
        self.wrapped.VickersHardnessHVAtEffectiveCaseDepth = float(value) if value else 0.0
