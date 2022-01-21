'''_4604.py

CVTPulleyModalAnalysisAtASpeed
'''


from mastapy.system_model.part_model.couplings import _2327
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4650
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'CVTPulleyModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyModalAnalysisAtASpeed',)


class CVTPulleyModalAnalysisAtASpeed(_4650.PulleyModalAnalysisAtASpeed):
    '''CVTPulleyModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2327.CVTPulley)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
