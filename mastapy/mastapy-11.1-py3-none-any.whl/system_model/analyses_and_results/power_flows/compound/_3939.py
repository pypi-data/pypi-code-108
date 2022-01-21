'''_3939.py

CVTCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3806
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3908
from mastapy._internal.python_net import python_net_import

_CVT_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CVTCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTCompoundPowerFlow',)


class CVTCompoundPowerFlow(_3908.BeltDriveCompoundPowerFlow):
    '''CVTCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CVT_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3806.CVTPowerFlow]':
        '''List[CVTPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3806.CVTPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3806.CVTPowerFlow]':
        '''List[CVTPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3806.CVTPowerFlow))
        return value
