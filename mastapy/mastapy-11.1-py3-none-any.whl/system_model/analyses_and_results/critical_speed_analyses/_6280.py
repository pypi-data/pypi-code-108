'''_6280.py

ClutchCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model.couplings import _2318
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6549
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6296
from mastapy._internal.python_net import python_net_import

_CLUTCH_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'ClutchCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchCriticalSpeedAnalysis',)


class ClutchCriticalSpeedAnalysis(_6296.CouplingCriticalSpeedAnalysis):
    '''ClutchCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2318.Clutch':
        '''Clutch: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2318.Clutch)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6549.ClutchLoadCase':
        '''ClutchLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6549.ClutchLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
