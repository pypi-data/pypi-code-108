'''_6500.py

StraightBevelPlanetGearCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6371
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6494
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_PLANET_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'StraightBevelPlanetGearCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelPlanetGearCompoundCriticalSpeedAnalysis',)


class StraightBevelPlanetGearCompoundCriticalSpeedAnalysis(_6494.StraightBevelDiffGearCompoundCriticalSpeedAnalysis):
    '''StraightBevelPlanetGearCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_PLANET_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelPlanetGearCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_6371.StraightBevelPlanetGearCriticalSpeedAnalysis]':
        '''List[StraightBevelPlanetGearCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6371.StraightBevelPlanetGearCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6371.StraightBevelPlanetGearCriticalSpeedAnalysis]':
        '''List[StraightBevelPlanetGearCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6371.StraightBevelPlanetGearCriticalSpeedAnalysis))
        return value
