'''_2590.py

AGMAGleasonConicalGearCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2431
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2618
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'AGMAGleasonConicalGearCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundSystemDeflection',)


class AGMAGleasonConicalGearCompoundSystemDeflection(_2618.ConicalGearCompoundSystemDeflection):
    '''AGMAGleasonConicalGearCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2431.AGMAGleasonConicalGearSystemDeflection]':
        '''List[AGMAGleasonConicalGearSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2431.AGMAGleasonConicalGearSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2431.AGMAGleasonConicalGearSystemDeflection]':
        '''List[AGMAGleasonConicalGearSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2431.AGMAGleasonConicalGearSystemDeflection))
        return value
