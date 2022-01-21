'''_3421.py

ExternalCADModelCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model import _2193
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3289
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3394
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'ExternalCADModelCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelCompoundSteadyStateSynchronousResponse',)


class ExternalCADModelCompoundSteadyStateSynchronousResponse(_3394.ComponentCompoundSteadyStateSynchronousResponse):
    '''ExternalCADModelCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3289.ExternalCADModelSteadyStateSynchronousResponse]':
        '''List[ExternalCADModelSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3289.ExternalCADModelSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3289.ExternalCADModelSteadyStateSynchronousResponse]':
        '''List[ExternalCADModelSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3289.ExternalCADModelSteadyStateSynchronousResponse))
        return value
