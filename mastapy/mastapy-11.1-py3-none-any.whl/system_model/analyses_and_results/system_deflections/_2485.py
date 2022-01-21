'''_2485.py

CylindricalPlanetGearSystemDeflection
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3816
from mastapy.system_model.analyses_and_results.system_deflections import _2482
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalPlanetGearSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearSystemDeflection',)


class CylindricalPlanetGearSystemDeflection(_2482.CylindricalGearSystemDeflectionWithLTCAResults):
    '''CylindricalPlanetGearSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def power_flow_results(self) -> '_3816.CylindricalPlanetGearPowerFlow':
        '''CylindricalPlanetGearPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3816.CylindricalPlanetGearPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
