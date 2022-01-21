'''_7077.py

PlanetaryGearSetAdvancedSystemDeflection
'''


from mastapy.system_model.part_model.gears import _2282
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7040
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'PlanetaryGearSetAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetAdvancedSystemDeflection',)


class PlanetaryGearSetAdvancedSystemDeflection(_7040.CylindricalGearSetAdvancedSystemDeflection):
    '''PlanetaryGearSetAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2282.PlanetaryGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
