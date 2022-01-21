'''_3751.py

UnbalancedMassCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3622
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3752
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'UnbalancedMassCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassCompoundStabilityAnalysis',)


class UnbalancedMassCompoundStabilityAnalysis(_3752.VirtualComponentCompoundStabilityAnalysis):
    '''UnbalancedMassCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3622.UnbalancedMassStabilityAnalysis]':
        '''List[UnbalancedMassStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3622.UnbalancedMassStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3622.UnbalancedMassStabilityAnalysis]':
        '''List[UnbalancedMassStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3622.UnbalancedMassStabilityAnalysis))
        return value
