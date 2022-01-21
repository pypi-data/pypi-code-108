'''_3651.py

ClutchCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2318
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3521
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3667
from mastapy._internal.python_net import python_net_import

_CLUTCH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ClutchCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchCompoundStabilityAnalysis',)


class ClutchCompoundStabilityAnalysis(_3667.CouplingCompoundStabilityAnalysis):
    '''ClutchCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2318.Clutch':
        '''Clutch: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2318.Clutch)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2318.Clutch':
        '''Clutch: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2318.Clutch)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3521.ClutchStabilityAnalysis]':
        '''List[ClutchStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3521.ClutchStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3521.ClutchStabilityAnalysis]':
        '''List[ClutchStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3521.ClutchStabilityAnalysis))
        return value
