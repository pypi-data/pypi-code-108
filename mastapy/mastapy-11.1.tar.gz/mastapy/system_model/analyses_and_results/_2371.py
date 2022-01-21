'''_2371.py

DynamicModelForSteadyStateSynchronousResponseAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_FOR_STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'DynamicModelForSteadyStateSynchronousResponseAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelForSteadyStateSynchronousResponseAnalysis',)


class DynamicModelForSteadyStateSynchronousResponseAnalysis(_2360.SingleAnalysis):
    '''DynamicModelForSteadyStateSynchronousResponseAnalysis

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_FOR_STEADY_STATE_SYNCHRONOUS_RESPONSE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelForSteadyStateSynchronousResponseAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
