'''_3898.py

AbstractAssemblyCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3765
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3977
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ASSEMBLY_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'AbstractAssemblyCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAssemblyCompoundPowerFlow',)


class AbstractAssemblyCompoundPowerFlow(_3977.PartCompoundPowerFlow):
    '''AbstractAssemblyCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_ASSEMBLY_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAssemblyCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3765.AbstractAssemblyPowerFlow]':
        '''List[AbstractAssemblyPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3765.AbstractAssemblyPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3765.AbstractAssemblyPowerFlow]':
        '''List[AbstractAssemblyPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3765.AbstractAssemblyPowerFlow))
        return value
