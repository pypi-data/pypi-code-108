'''_2814.py

ShaftSteadyStateSynchronousResponseOnAShaft
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6668
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2720
from mastapy._internal.python_net import python_net_import

_SHAFT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'ShaftSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftSteadyStateSynchronousResponseOnAShaft',)


class ShaftSteadyStateSynchronousResponseOnAShaft(_2720.AbstractShaftSteadyStateSynchronousResponseOnAShaft):
    '''ShaftSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _SHAFT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6668.ShaftLoadCase':
        '''ShaftLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6668.ShaftLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[ShaftSteadyStateSynchronousResponseOnAShaft]':
        '''List[ShaftSteadyStateSynchronousResponseOnAShaft]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftSteadyStateSynchronousResponseOnAShaft))
        return value
