'''_7148.py

ComponentCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7015
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7202
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ComponentCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundAdvancedSystemDeflection',)


class ComponentCompoundAdvancedSystemDeflection(_7202.PartCompoundAdvancedSystemDeflection):
    '''ComponentCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_7015.ComponentAdvancedSystemDeflection]':
        '''List[ComponentAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7015.ComponentAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_7015.ComponentAdvancedSystemDeflection]':
        '''List[ComponentAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7015.ComponentAdvancedSystemDeflection))
        return value
