'''_3708.py

OilSealCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3577
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3666
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'OilSealCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealCompoundStabilityAnalysis',)


class OilSealCompoundStabilityAnalysis(_3666.ConnectorCompoundStabilityAnalysis):
    '''OilSealCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3577.OilSealStabilityAnalysis]':
        '''List[OilSealStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3577.OilSealStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3577.OilSealStabilityAnalysis]':
        '''List[OilSealStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3577.OilSealStabilityAnalysis))
        return value
