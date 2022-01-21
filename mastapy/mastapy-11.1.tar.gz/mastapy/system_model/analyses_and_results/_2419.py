'''_2419.py

CompoundSteadyStateSynchronousResponseAtASpeedAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundSteadyStateSynchronousResponseAtASpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundSteadyStateSynchronousResponseAtASpeedAnalysis',)


class CompoundSteadyStateSynchronousResponseAtASpeedAnalysis(_2359.CompoundAnalysis):
    '''CompoundSteadyStateSynchronousResponseAtASpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundSteadyStateSynchronousResponseAtASpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
