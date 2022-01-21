'''_7165.py

CVTPulleyCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7033
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7211
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'CVTPulleyCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundAdvancedSystemDeflection',)


class CVTPulleyCompoundAdvancedSystemDeflection(_7211.PulleyCompoundAdvancedSystemDeflection):
    '''CVTPulleyCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_7033.CVTPulleyAdvancedSystemDeflection]':
        '''List[CVTPulleyAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7033.CVTPulleyAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7033.CVTPulleyAdvancedSystemDeflection]':
        '''List[CVTPulleyAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7033.CVTPulleyAdvancedSystemDeflection))
        return value
