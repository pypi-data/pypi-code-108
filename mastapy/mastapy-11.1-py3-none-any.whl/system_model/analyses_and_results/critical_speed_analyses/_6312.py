'''_6312.py

ExternalCADModelCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model import _2193
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6598
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6283
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'ExternalCADModelCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelCriticalSpeedAnalysis',)


class ExternalCADModelCriticalSpeedAnalysis(_6283.ComponentCriticalSpeedAnalysis):
    '''ExternalCADModelCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6598.ExternalCADModelLoadCase':
        '''ExternalCADModelLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6598.ExternalCADModelLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
