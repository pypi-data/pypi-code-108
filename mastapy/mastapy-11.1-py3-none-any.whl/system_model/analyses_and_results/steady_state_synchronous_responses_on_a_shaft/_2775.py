'''_2775.py

FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft
'''


from mastapy.system_model.part_model import _2195
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6603
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2816
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft',)


class FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft(_2816.SpecialisedAssemblySteadyStateSynchronousResponseOnAShaft):
    '''FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ASSEMBLY_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2195.FlexiblePinAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6603.FlexiblePinAssemblyLoadCase':
        '''FlexiblePinAssemblyLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6603.FlexiblePinAssemblyLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
