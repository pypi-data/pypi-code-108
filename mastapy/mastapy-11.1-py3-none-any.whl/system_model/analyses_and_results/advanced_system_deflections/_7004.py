'''_7004.py

BevelDifferentialPlanetGearAdvancedSystemDeflection
'''


from mastapy.system_model.part_model.gears import _2257
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7001
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'BevelDifferentialPlanetGearAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGearAdvancedSystemDeflection',)


class BevelDifferentialPlanetGearAdvancedSystemDeflection(_7001.BevelDifferentialGearAdvancedSystemDeflection):
    '''BevelDifferentialPlanetGearAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGearAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2257.BevelDifferentialPlanetGear':
        '''BevelDifferentialPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2257.BevelDifferentialPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
