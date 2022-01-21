'''_6404.py

BevelDifferentialSunGearCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6273
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6400
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_SUN_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'BevelDifferentialSunGearCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialSunGearCompoundCriticalSpeedAnalysis',)


class BevelDifferentialSunGearCompoundCriticalSpeedAnalysis(_6400.BevelDifferentialGearCompoundCriticalSpeedAnalysis):
    '''BevelDifferentialSunGearCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_SUN_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialSunGearCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_6273.BevelDifferentialSunGearCriticalSpeedAnalysis]':
        '''List[BevelDifferentialSunGearCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6273.BevelDifferentialSunGearCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6273.BevelDifferentialSunGearCriticalSpeedAnalysis]':
        '''List[BevelDifferentialSunGearCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6273.BevelDifferentialSunGearCriticalSpeedAnalysis))
        return value
