'''_3343.py

SteadyStateSynchronousResponseDrawStyle
'''


from mastapy.system_model.analyses_and_results.rotor_dynamics import _3759
from mastapy._internal.python_net import python_net_import

_STEADY_STATE_SYNCHRONOUS_RESPONSE_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'SteadyStateSynchronousResponseDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('SteadyStateSynchronousResponseDrawStyle',)


class SteadyStateSynchronousResponseDrawStyle(_3759.RotorDynamicsDrawStyle):
    '''SteadyStateSynchronousResponseDrawStyle

    This is a mastapy class.
    '''

    TYPE = _STEADY_STATE_SYNCHRONOUS_RESPONSE_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SteadyStateSynchronousResponseDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
