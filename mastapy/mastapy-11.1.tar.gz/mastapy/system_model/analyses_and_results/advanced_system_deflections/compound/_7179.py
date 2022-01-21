'''_7179.py

FEPartCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7048
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7125
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'FEPartCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundAdvancedSystemDeflection',)


class FEPartCompoundAdvancedSystemDeflection(_7125.AbstractShaftOrHousingCompoundAdvancedSystemDeflection):
    '''FEPartCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7048.FEPartAdvancedSystemDeflection]':
        '''List[FEPartAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7048.FEPartAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundAdvancedSystemDeflection]':
        '''List[FEPartCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7048.FEPartAdvancedSystemDeflection]':
        '''List[FEPartAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7048.FEPartAdvancedSystemDeflection))
        return value
