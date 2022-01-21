'''_6484.py

ShaftCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6355
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6390
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ShaftCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundCriticalSpeedAnalysis',)


class ShaftCompoundCriticalSpeedAnalysis(_6390.AbstractShaftCompoundCriticalSpeedAnalysis):
    '''ShaftCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6355.ShaftCriticalSpeedAnalysis]':
        '''List[ShaftCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6355.ShaftCriticalSpeedAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundCriticalSpeedAnalysis]':
        '''List[ShaftCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6355.ShaftCriticalSpeedAnalysis]':
        '''List[ShaftCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6355.ShaftCriticalSpeedAnalysis))
        return value
