'''_7129.py

AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6996
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7157
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection',)


class AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection(_7157.ConicalGearSetCompoundAdvancedSystemDeflection):
    '''AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_6996.AGMAGleasonConicalGearSetAdvancedSystemDeflection]':
        '''List[AGMAGleasonConicalGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6996.AGMAGleasonConicalGearSetAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6996.AGMAGleasonConicalGearSetAdvancedSystemDeflection]':
        '''List[AGMAGleasonConicalGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6996.AGMAGleasonConicalGearSetAdvancedSystemDeflection))
        return value
