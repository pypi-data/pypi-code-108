'''_3705.py

MassDiscCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3574
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3752
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'MassDiscCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundStabilityAnalysis',)


class MassDiscCompoundStabilityAnalysis(_3752.VirtualComponentCompoundStabilityAnalysis):
    '''MassDiscCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundStabilityAnalysis.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_3574.MassDiscStabilityAnalysis]':
        '''List[MassDiscStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3574.MassDiscStabilityAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundStabilityAnalysis]':
        '''List[MassDiscCompoundStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3574.MassDiscStabilityAnalysis]':
        '''List[MassDiscStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3574.MassDiscStabilityAnalysis))
        return value
