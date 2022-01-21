'''_3288.py

DynamicModelForSteadyStateSynchronousResponse
'''


from mastapy.system_model.analyses_and_results.dynamic_analyses import _2366
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_FOR_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'DynamicModelForSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelForSteadyStateSynchronousResponse',)


class DynamicModelForSteadyStateSynchronousResponse(_2366.DynamicAnalysis):
    '''DynamicModelForSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_FOR_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelForSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
