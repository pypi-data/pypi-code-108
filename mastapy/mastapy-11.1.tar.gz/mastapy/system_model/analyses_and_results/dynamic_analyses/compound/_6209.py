'''_6209.py

PointLoadCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6080
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6245
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'PointLoadCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadCompoundDynamicAnalysis',)


class PointLoadCompoundDynamicAnalysis(_6245.VirtualComponentCompoundDynamicAnalysis):
    '''PointLoadCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6080.PointLoadDynamicAnalysis]':
        '''List[PointLoadDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6080.PointLoadDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6080.PointLoadDynamicAnalysis]':
        '''List[PointLoadDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6080.PointLoadDynamicAnalysis))
        return value
