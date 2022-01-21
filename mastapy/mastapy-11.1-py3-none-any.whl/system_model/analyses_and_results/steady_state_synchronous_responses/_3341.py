'''_3341.py

SpringDamperSteadyStateSynchronousResponse
'''


from mastapy.system_model.part_model.couplings import _2340
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6677
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3275
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'SpringDamperSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperSteadyStateSynchronousResponse',)


class SpringDamperSteadyStateSynchronousResponse(_3275.CouplingSteadyStateSynchronousResponse):
    '''SpringDamperSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2340.SpringDamper)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6677.SpringDamperLoadCase':
        '''SpringDamperLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6677.SpringDamperLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
