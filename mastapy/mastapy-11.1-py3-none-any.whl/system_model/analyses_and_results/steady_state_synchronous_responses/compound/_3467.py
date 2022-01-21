'''_3467.py

SpecialisedAssemblyCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3335
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3369
from mastapy._internal.python_net import python_net_import

_SPECIALISED_ASSEMBLY_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'SpecialisedAssemblyCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecialisedAssemblyCompoundSteadyStateSynchronousResponse',)


class SpecialisedAssemblyCompoundSteadyStateSynchronousResponse(_3369.AbstractAssemblyCompoundSteadyStateSynchronousResponse):
    '''SpecialisedAssemblyCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _SPECIALISED_ASSEMBLY_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecialisedAssemblyCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3335.SpecialisedAssemblySteadyStateSynchronousResponse]':
        '''List[SpecialisedAssemblySteadyStateSynchronousResponse]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3335.SpecialisedAssemblySteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3335.SpecialisedAssemblySteadyStateSynchronousResponse]':
        '''List[SpecialisedAssemblySteadyStateSynchronousResponse]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3335.SpecialisedAssemblySteadyStateSynchronousResponse))
        return value
