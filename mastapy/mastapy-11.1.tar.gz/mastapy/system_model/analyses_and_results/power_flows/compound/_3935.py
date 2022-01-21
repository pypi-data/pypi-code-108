'''_3935.py

CouplingCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3804
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3996
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CouplingCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundPowerFlow',)


class CouplingCompoundPowerFlow(_3996.SpecialisedAssemblyCompoundPowerFlow):
    '''CouplingCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3804.CouplingPowerFlow]':
        '''List[CouplingPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3804.CouplingPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3804.CouplingPowerFlow]':
        '''List[CouplingPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3804.CouplingPowerFlow))
        return value
