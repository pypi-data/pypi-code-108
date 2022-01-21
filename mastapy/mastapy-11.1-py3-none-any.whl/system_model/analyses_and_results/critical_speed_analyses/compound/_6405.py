'''_6405.py

BevelGearCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6274
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6393
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'BevelGearCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundCriticalSpeedAnalysis',)


class BevelGearCompoundCriticalSpeedAnalysis(_6393.AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis):
    '''BevelGearCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6274.BevelGearCriticalSpeedAnalysis]':
        '''List[BevelGearCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6274.BevelGearCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6274.BevelGearCriticalSpeedAnalysis]':
        '''List[BevelGearCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6274.BevelGearCriticalSpeedAnalysis))
        return value
