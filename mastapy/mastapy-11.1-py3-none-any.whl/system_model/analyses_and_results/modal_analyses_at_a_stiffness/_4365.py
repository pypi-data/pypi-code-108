'''_4365.py

GuideDxfModelModalAnalysisAtAStiffness
'''


from mastapy.system_model.part_model import _2196
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6611
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4328
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness', 'GuideDxfModelModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModelModalAnalysisAtAStiffness',)


class GuideDxfModelModalAnalysisAtAStiffness(_4328.ComponentModalAnalysisAtAStiffness):
    '''GuideDxfModelModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModelModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2196.GuideDxfModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6611.GuideDxfModelLoadCase':
        '''GuideDxfModelLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6611.GuideDxfModelLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
