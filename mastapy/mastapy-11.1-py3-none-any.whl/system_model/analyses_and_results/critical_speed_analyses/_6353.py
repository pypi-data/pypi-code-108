'''_6353.py

RollingRingCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6665
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6297
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'RollingRingCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingCriticalSpeedAnalysis',)


class RollingRingCriticalSpeedAnalysis(_6297.CouplingHalfCriticalSpeedAnalysis):
    '''RollingRingCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6665.RollingRingLoadCase':
        '''RollingRingLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6665.RollingRingLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[RollingRingCriticalSpeedAnalysis]':
        '''List[RollingRingCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingCriticalSpeedAnalysis))
        return value
