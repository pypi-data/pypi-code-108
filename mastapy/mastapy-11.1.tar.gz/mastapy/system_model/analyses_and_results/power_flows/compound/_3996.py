'''_3996.py

SpecialisedAssemblyCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3866
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3898
from mastapy._internal.python_net import python_net_import

_SPECIALISED_ASSEMBLY_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SpecialisedAssemblyCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecialisedAssemblyCompoundPowerFlow',)


class SpecialisedAssemblyCompoundPowerFlow(_3898.AbstractAssemblyCompoundPowerFlow):
    '''SpecialisedAssemblyCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SPECIALISED_ASSEMBLY_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecialisedAssemblyCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3866.SpecialisedAssemblyPowerFlow]':
        '''List[SpecialisedAssemblyPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3866.SpecialisedAssemblyPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3866.SpecialisedAssemblyPowerFlow]':
        '''List[SpecialisedAssemblyPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3866.SpecialisedAssemblyPowerFlow))
        return value
