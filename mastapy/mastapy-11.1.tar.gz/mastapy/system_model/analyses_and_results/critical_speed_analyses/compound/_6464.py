'''_6464.py

MassDiscCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6335
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6511
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'MassDiscCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundCriticalSpeedAnalysis',)


class MassDiscCompoundCriticalSpeedAnalysis(_6511.VirtualComponentCompoundCriticalSpeedAnalysis):
    '''MassDiscCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6335.MassDiscCriticalSpeedAnalysis]':
        '''List[MassDiscCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6335.MassDiscCriticalSpeedAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundCriticalSpeedAnalysis]':
        '''List[MassDiscCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6335.MassDiscCriticalSpeedAnalysis]':
        '''List[MassDiscCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6335.MassDiscCriticalSpeedAnalysis))
        return value
