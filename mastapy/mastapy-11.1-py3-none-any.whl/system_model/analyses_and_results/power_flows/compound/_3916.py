'''_3916.py

BevelGearSetCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3783
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3904
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'BevelGearSetCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetCompoundPowerFlow',)


class BevelGearSetCompoundPowerFlow(_3904.AGMAGleasonConicalGearSetCompoundPowerFlow):
    '''BevelGearSetCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3783.BevelGearSetPowerFlow]':
        '''List[BevelGearSetPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3783.BevelGearSetPowerFlow))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3783.BevelGearSetPowerFlow]':
        '''List[BevelGearSetPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3783.BevelGearSetPowerFlow))
        return value
