'''_3734.py

SpringDamperHalfCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2341
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3602
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3669
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'SpringDamperHalfCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfCompoundStabilityAnalysis',)


class SpringDamperHalfCompoundStabilityAnalysis(_3669.CouplingHalfCompoundStabilityAnalysis):
    '''SpringDamperHalfCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2341.SpringDamperHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3602.SpringDamperHalfStabilityAnalysis]':
        '''List[SpringDamperHalfStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3602.SpringDamperHalfStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3602.SpringDamperHalfStabilityAnalysis]':
        '''List[SpringDamperHalfStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3602.SpringDamperHalfStabilityAnalysis))
        return value
