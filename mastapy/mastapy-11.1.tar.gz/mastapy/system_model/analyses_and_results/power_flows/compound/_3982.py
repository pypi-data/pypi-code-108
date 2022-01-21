'''_3982.py

PlanetaryGearSetCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3850
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3947
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'PlanetaryGearSetCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetCompoundPowerFlow',)


class PlanetaryGearSetCompoundPowerFlow(_3947.CylindricalGearSetCompoundPowerFlow):
    '''PlanetaryGearSetCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3850.PlanetaryGearSetPowerFlow]':
        '''List[PlanetaryGearSetPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3850.PlanetaryGearSetPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3850.PlanetaryGearSetPowerFlow]':
        '''List[PlanetaryGearSetPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3850.PlanetaryGearSetPowerFlow))
        return value
