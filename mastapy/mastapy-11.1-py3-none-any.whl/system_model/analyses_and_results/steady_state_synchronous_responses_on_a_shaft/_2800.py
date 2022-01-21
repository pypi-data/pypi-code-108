'''_2800.py

PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft
'''


from mastapy.system_model.part_model.couplings import _2328
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6649
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import _2757
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft', 'PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft',)


class PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft(_2757.CouplingSteadyStateSynchronousResponseOnAShaft):
    '''PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2328.PartToPartShearCoupling)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6649.PartToPartShearCouplingLoadCase':
        '''PartToPartShearCouplingLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6649.PartToPartShearCouplingLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
