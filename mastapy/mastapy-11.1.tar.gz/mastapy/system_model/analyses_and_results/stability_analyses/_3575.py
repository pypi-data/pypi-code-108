'''_3575.py

MeasurementComponentStabilityAnalysis
'''


from mastapy.system_model.part_model import _2204
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6639
from mastapy.system_model.analyses_and_results.stability_analyses import _3623
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_COMPONENT_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'MeasurementComponentStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementComponentStabilityAnalysis',)


class MeasurementComponentStabilityAnalysis(_3623.VirtualComponentStabilityAnalysis):
    '''MeasurementComponentStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_COMPONENT_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementComponentStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2204.MeasurementComponent)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6639.MeasurementComponentLoadCase':
        '''MeasurementComponentLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6639.MeasurementComponentLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
