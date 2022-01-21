'''_6277.py

BoltCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model import _2184
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6546
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6283
from mastapy._internal.python_net import python_net_import

_BOLT_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'BoltCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltCriticalSpeedAnalysis',)


class BoltCriticalSpeedAnalysis(_6283.ComponentCriticalSpeedAnalysis):
    '''BoltCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _BOLT_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2184.Bolt':
        '''Bolt: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2184.Bolt)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6546.BoltLoadCase':
        '''BoltLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6546.BoltLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
