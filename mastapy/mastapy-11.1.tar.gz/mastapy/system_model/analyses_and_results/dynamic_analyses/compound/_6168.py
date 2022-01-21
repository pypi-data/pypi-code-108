'''_6168.py

CycloidalDiscCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6038
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6124
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CycloidalDiscCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCompoundDynamicAnalysis',)


class CycloidalDiscCompoundDynamicAnalysis(_6124.AbstractShaftCompoundDynamicAnalysis):
    '''CycloidalDiscCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2309.CycloidalDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6038.CycloidalDiscDynamicAnalysis]':
        '''List[CycloidalDiscDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6038.CycloidalDiscDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6038.CycloidalDiscDynamicAnalysis]':
        '''List[CycloidalDiscDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6038.CycloidalDiscDynamicAnalysis))
        return value
