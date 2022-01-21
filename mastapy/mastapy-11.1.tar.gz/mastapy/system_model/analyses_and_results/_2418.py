'''_2418.py

CompoundSteadyStateSynchronousResponseAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundSteadyStateSynchronousResponseAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundSteadyStateSynchronousResponseAnalysis',)


class CompoundSteadyStateSynchronousResponseAnalysis(_2359.CompoundAnalysis):
    '''CompoundSteadyStateSynchronousResponseAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundSteadyStateSynchronousResponseAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
