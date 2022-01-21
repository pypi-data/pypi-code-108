'''_3071.py

RootAssemblySteadyStateSynchronousResponseAtASpeed
'''


from mastapy.system_model.part_model import _2215
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _3082, _2984
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed', 'RootAssemblySteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblySteadyStateSynchronousResponseAtASpeed',)


class RootAssemblySteadyStateSynchronousResponseAtASpeed(_2984.AssemblySteadyStateSynchronousResponseAtASpeed):
    '''RootAssemblySteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblySteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def steady_state_synchronous_response_at_a_speed_inputs(self) -> '_3082.SteadyStateSynchronousResponseAtASpeed':
        '''SteadyStateSynchronousResponseAtASpeed: 'SteadyStateSynchronousResponseAtASpeedInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3082.SteadyStateSynchronousResponseAtASpeed)(self.wrapped.SteadyStateSynchronousResponseAtASpeedInputs) if self.wrapped.SteadyStateSynchronousResponseAtASpeedInputs is not None else None
