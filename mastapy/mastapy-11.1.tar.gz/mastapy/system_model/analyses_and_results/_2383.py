'''_2383.py

SteadyStateSynchronousResponseAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'SteadyStateSynchronousResponseAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SteadyStateSynchronousResponseAnalysis',)


class SteadyStateSynchronousResponseAnalysis(_2360.SingleAnalysis):
    '''SteadyStateSynchronousResponseAnalysis

    This is a mastapy class.
    '''

    TYPE = _STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SteadyStateSynchronousResponseAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
