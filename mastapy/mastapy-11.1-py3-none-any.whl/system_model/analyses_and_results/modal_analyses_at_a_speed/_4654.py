'''_4654.py

RollingRingConnectionModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _2034
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6664
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4627
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'RollingRingConnectionModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionModalAnalysisAtASpeed',)


class RollingRingConnectionModalAnalysisAtASpeed(_4627.InterMountableComponentConnectionModalAnalysisAtASpeed):
    '''RollingRingConnectionModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2034.RollingRingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6664.RollingRingConnectionLoadCase':
        '''RollingRingConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6664.RollingRingConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[RollingRingConnectionModalAnalysisAtASpeed]':
        '''List[RollingRingConnectionModalAnalysisAtASpeed]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingConnectionModalAnalysisAtASpeed))
        return value
