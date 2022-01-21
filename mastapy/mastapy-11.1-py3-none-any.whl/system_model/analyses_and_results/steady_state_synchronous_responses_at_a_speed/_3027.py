'''_3027.py

CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import _3026
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesAtASpeed', 'CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed',)


class CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed(_3026.CylindricalGearSteadyStateSynchronousResponseAtASpeed):
    '''CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
