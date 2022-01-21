'''_6431.py

CVTPulleyCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6302
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6477
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'CVTPulleyCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundCriticalSpeedAnalysis',)


class CVTPulleyCompoundCriticalSpeedAnalysis(_6477.PulleyCompoundCriticalSpeedAnalysis):
    '''CVTPulleyCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_6302.CVTPulleyCriticalSpeedAnalysis]':
        '''List[CVTPulleyCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6302.CVTPulleyCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6302.CVTPulleyCriticalSpeedAnalysis]':
        '''List[CVTPulleyCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6302.CVTPulleyCriticalSpeedAnalysis))
        return value
