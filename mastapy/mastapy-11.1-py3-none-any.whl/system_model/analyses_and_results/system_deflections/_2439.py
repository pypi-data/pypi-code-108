'''_2439.py

BevelDifferentialPlanetGearSystemDeflection
'''


from mastapy.system_model.part_model.gears import _2257
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3779
from mastapy.system_model.analyses_and_results.system_deflections import _2438
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'BevelDifferentialPlanetGearSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGearSystemDeflection',)


class BevelDifferentialPlanetGearSystemDeflection(_2438.BevelDifferentialGearSystemDeflection):
    '''BevelDifferentialPlanetGearSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGearSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2257.BevelDifferentialPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def power_flow_results(self) -> '_3779.BevelDifferentialPlanetGearPowerFlow':
        '''BevelDifferentialPlanetGearPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3779.BevelDifferentialPlanetGearPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
