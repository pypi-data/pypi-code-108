'''_2737.py

BoltedJointSteadyStateSynchronousResponseOnAShaft
'''


from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6545
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2816
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'BoltedJointSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointSteadyStateSynchronousResponseOnAShaft',)


class BoltedJointSteadyStateSynchronousResponseOnAShaft(_2816.SpecialisedAssemblySteadyStateSynchronousResponseOnAShaft):
    '''BoltedJointSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2185.BoltedJoint)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6545.BoltedJointLoadCase':
        '''BoltedJointLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6545.BoltedJointLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
