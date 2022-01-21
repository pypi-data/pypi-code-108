'''_4602.py

CVTBeltConnectionModalAnalysisAtASpeed
'''


from mastapy.system_model.connections_and_sockets import _2015
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4571
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'CVTBeltConnectionModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionModalAnalysisAtASpeed',)


class CVTBeltConnectionModalAnalysisAtASpeed(_4571.BeltConnectionModalAnalysisAtASpeed):
    '''CVTBeltConnectionModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2015.CVTBeltConnection':
        '''CVTBeltConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2015.CVTBeltConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
