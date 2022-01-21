'''_4612.py

CylindricalPlanetGearModalAnalysisAtASpeed
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4610
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'CylindricalPlanetGearModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearModalAnalysisAtASpeed',)


class CylindricalPlanetGearModalAnalysisAtASpeed(_4610.CylindricalGearModalAnalysisAtASpeed):
    '''CylindricalPlanetGearModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
