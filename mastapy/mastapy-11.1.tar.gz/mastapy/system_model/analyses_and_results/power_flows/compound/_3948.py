'''_3948.py

CylindricalPlanetGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3816
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3945
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'CylindricalPlanetGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearCompoundPowerFlow',)


class CylindricalPlanetGearCompoundPowerFlow(_3945.CylindricalGearCompoundPowerFlow):
    '''CylindricalPlanetGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_3816.CylindricalPlanetGearPowerFlow]':
        '''List[CylindricalPlanetGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3816.CylindricalPlanetGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3816.CylindricalPlanetGearPowerFlow]':
        '''List[CylindricalPlanetGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3816.CylindricalPlanetGearPowerFlow))
        return value
