'''_6478.py

RingPinsCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6349
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6466
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'RingPinsCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundCriticalSpeedAnalysis',)


class RingPinsCompoundCriticalSpeedAnalysis(_6466.MountableComponentCompoundCriticalSpeedAnalysis):
    '''RingPinsCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundCriticalSpeedAnalysis.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_6349.RingPinsCriticalSpeedAnalysis]':
        '''List[RingPinsCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6349.RingPinsCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6349.RingPinsCriticalSpeedAnalysis]':
        '''List[RingPinsCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6349.RingPinsCriticalSpeedAnalysis))
        return value
