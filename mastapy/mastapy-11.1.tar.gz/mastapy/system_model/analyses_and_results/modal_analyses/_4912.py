'''_4912.py

PointLoadModalAnalysis
'''


from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6656
from mastapy.system_model.analyses_and_results.system_deflections import _2526
from mastapy.system_model.analyses_and_results.modal_analyses import _4949
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'PointLoadModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadModalAnalysis',)


class PointLoadModalAnalysis(_4949.VirtualComponentModalAnalysis):
    '''PointLoadModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadModalAnalysis.TYPE'):
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
    def component_load_case(self) -> '_6656.PointLoadLoadCase':
        '''PointLoadLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6656.PointLoadLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2526.PointLoadSystemDeflection':
        '''PointLoadSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2526.PointLoadSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
