'''_3425.py

FEPartCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3293
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3371
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'FEPartCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundSteadyStateSynchronousResponse',)


class FEPartCompoundSteadyStateSynchronousResponse(_3371.AbstractShaftOrHousingCompoundSteadyStateSynchronousResponse):
    '''FEPartCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3293.FEPartSteadyStateSynchronousResponse]':
        '''List[FEPartSteadyStateSynchronousResponse]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3293.FEPartSteadyStateSynchronousResponse))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundSteadyStateSynchronousResponse]':
        '''List[FEPartCompoundSteadyStateSynchronousResponse]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundSteadyStateSynchronousResponse))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3293.FEPartSteadyStateSynchronousResponse]':
        '''List[FEPartSteadyStateSynchronousResponse]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3293.FEPartSteadyStateSynchronousResponse))
        return value
