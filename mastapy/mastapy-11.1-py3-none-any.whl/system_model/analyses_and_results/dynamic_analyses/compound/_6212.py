'''_6212.py

RingPinsCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6083
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6200
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'RingPinsCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundDynamicAnalysis',)


class RingPinsCompoundDynamicAnalysis(_6200.MountableComponentCompoundDynamicAnalysis):
    '''RingPinsCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6083.RingPinsDynamicAnalysis]':
        '''List[RingPinsDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6083.RingPinsDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6083.RingPinsDynamicAnalysis]':
        '''List[RingPinsDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6083.RingPinsDynamicAnalysis))
        return value
