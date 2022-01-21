'''_2420.py

CompoundSteadyStateSynchronousResponseOnAShaftAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundSteadyStateSynchronousResponseOnAShaftAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundSteadyStateSynchronousResponseOnAShaftAnalysis',)


class CompoundSteadyStateSynchronousResponseOnAShaftAnalysis(_2359.CompoundAnalysis):
    '''CompoundSteadyStateSynchronousResponseOnAShaftAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundSteadyStateSynchronousResponseOnAShaftAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
