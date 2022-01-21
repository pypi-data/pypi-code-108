'''_2384.py

SteadyStateSynchronousResponseAtASpeedAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'SteadyStateSynchronousResponseAtASpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SteadyStateSynchronousResponseAtASpeedAnalysis',)


class SteadyStateSynchronousResponseAtASpeedAnalysis(_2360.SingleAnalysis):
    '''SteadyStateSynchronousResponseAtASpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SteadyStateSynchronousResponseAtASpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
