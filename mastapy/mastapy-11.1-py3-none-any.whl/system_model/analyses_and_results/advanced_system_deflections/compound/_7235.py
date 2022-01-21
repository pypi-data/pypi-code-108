'''_7235.py

StraightBevelSunGearCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7105
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7228
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'StraightBevelSunGearCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelSunGearCompoundAdvancedSystemDeflection',)


class StraightBevelSunGearCompoundAdvancedSystemDeflection(_7228.StraightBevelDiffGearCompoundAdvancedSystemDeflection):
    '''StraightBevelSunGearCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelSunGearCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_7105.StraightBevelSunGearAdvancedSystemDeflection]':
        '''List[StraightBevelSunGearAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7105.StraightBevelSunGearAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7105.StraightBevelSunGearAdvancedSystemDeflection]':
        '''List[StraightBevelSunGearAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7105.StraightBevelSunGearAdvancedSystemDeflection))
        return value
