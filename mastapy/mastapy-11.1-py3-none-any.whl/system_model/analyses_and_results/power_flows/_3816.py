'''_3816.py

CylindricalPlanetGearPowerFlow
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3814
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'CylindricalPlanetGearPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearPowerFlow',)


class CylindricalPlanetGearPowerFlow(_3814.CylindricalGearPowerFlow):
    '''CylindricalPlanetGearPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
