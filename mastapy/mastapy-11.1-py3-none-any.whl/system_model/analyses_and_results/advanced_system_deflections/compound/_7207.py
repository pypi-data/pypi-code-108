'''_7207.py

PlanetaryGearSetCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7077
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7172
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'PlanetaryGearSetCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetCompoundAdvancedSystemDeflection',)


class PlanetaryGearSetCompoundAdvancedSystemDeflection(_7172.CylindricalGearSetCompoundAdvancedSystemDeflection):
    '''PlanetaryGearSetCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_7077.PlanetaryGearSetAdvancedSystemDeflection]':
        '''List[PlanetaryGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_7077.PlanetaryGearSetAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_7077.PlanetaryGearSetAdvancedSystemDeflection]':
        '''List[PlanetaryGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_7077.PlanetaryGearSetAdvancedSystemDeflection))
        return value
