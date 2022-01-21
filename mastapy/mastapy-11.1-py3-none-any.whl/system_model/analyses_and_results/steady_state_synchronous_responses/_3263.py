'''_3263.py

ConceptCouplingHalfSteadyStateSynchronousResponse
'''


from mastapy.system_model.part_model.couplings import _2322
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6553
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3274
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_HALF_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses', 'ConceptCouplingHalfSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingHalfSteadyStateSynchronousResponse',)


class ConceptCouplingHalfSteadyStateSynchronousResponse(_3274.CouplingHalfSteadyStateSynchronousResponse):
    '''ConceptCouplingHalfSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_HALF_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingHalfSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2322.ConceptCouplingHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6553.ConceptCouplingHalfLoadCase':
        '''ConceptCouplingHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6553.ConceptCouplingHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
