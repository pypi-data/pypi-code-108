'''_2600.py

BevelDifferentialPlanetGearCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2439
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2597
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'BevelDifferentialPlanetGearCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGearCompoundSystemDeflection',)


class BevelDifferentialPlanetGearCompoundSystemDeflection(_2597.BevelDifferentialGearCompoundSystemDeflection):
    '''BevelDifferentialPlanetGearCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGearCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_2439.BevelDifferentialPlanetGearSystemDeflection]':
        '''List[BevelDifferentialPlanetGearSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2439.BevelDifferentialPlanetGearSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2439.BevelDifferentialPlanetGearSystemDeflection]':
        '''List[BevelDifferentialPlanetGearSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2439.BevelDifferentialPlanetGearSystemDeflection))
        return value
