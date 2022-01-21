'''_7139.py

BevelGearCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7006
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7127
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'BevelGearCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundAdvancedSystemDeflection',)


class BevelGearCompoundAdvancedSystemDeflection(_7127.AGMAGleasonConicalGearCompoundAdvancedSystemDeflection):
    '''BevelGearCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_7006.BevelGearAdvancedSystemDeflection]':
        '''List[BevelGearAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7006.BevelGearAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_7006.BevelGearAdvancedSystemDeflection]':
        '''List[BevelGearAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7006.BevelGearAdvancedSystemDeflection))
        return value
