'''_2638.py

DutyCycleEfficiencyResults
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2512
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DUTY_CYCLE_EFFICIENCY_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'DutyCycleEfficiencyResults')


__docformat__ = 'restructuredtext en'
__all__ = ('DutyCycleEfficiencyResults',)


class DutyCycleEfficiencyResults(_0.APIBase):
    '''DutyCycleEfficiencyResults

    This is a mastapy class.
    '''

    TYPE = _DUTY_CYCLE_EFFICIENCY_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DutyCycleEfficiencyResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def energy_input(self) -> 'float':
        '''float: 'EnergyInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyInput

    @property
    def energy_lost(self) -> 'float':
        '''float: 'EnergyLost' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyLost

    @property
    def energy_output(self) -> 'float':
        '''float: 'EnergyOutput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyOutput

    @property
    def efficiency(self) -> 'float':
        '''float: 'Efficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Efficiency

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def load_case_overall_efficiency_result(self) -> 'List[_2512.LoadCaseOverallEfficiencyResult]':
        '''List[LoadCaseOverallEfficiencyResult]: 'LoadCaseOverallEfficiencyResult' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseOverallEfficiencyResult, constructor.new(_2512.LoadCaseOverallEfficiencyResult))
        return value
