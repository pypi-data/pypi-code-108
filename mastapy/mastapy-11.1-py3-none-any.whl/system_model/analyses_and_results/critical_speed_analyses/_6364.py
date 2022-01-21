'''_6364.py

SpringDamperHalfCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model.couplings import _2341
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6676
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6297
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'SpringDamperHalfCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfCriticalSpeedAnalysis',)


class SpringDamperHalfCriticalSpeedAnalysis(_6297.CouplingHalfCriticalSpeedAnalysis):
    '''SpringDamperHalfCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfCriticalSpeedAnalysis.TYPE'):
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
    def component_load_case(self) -> '_6676.SpringDamperHalfLoadCase':
        '''SpringDamperHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6676.SpringDamperHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
