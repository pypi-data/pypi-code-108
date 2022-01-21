'''_6474.py

PlanetCarrierCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2210
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6345
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6466
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'PlanetCarrierCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierCompoundCriticalSpeedAnalysis',)


class PlanetCarrierCompoundCriticalSpeedAnalysis(_6466.MountableComponentCompoundCriticalSpeedAnalysis):
    '''PlanetCarrierCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2210.PlanetCarrier)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6345.PlanetCarrierCriticalSpeedAnalysis]':
        '''List[PlanetCarrierCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6345.PlanetCarrierCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6345.PlanetCarrierCriticalSpeedAnalysis]':
        '''List[PlanetCarrierCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6345.PlanetCarrierCriticalSpeedAnalysis))
        return value
