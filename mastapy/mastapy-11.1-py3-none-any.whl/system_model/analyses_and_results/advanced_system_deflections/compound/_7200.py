'''_7200.py

MountableComponentCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7070
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7148
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'MountableComponentCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundAdvancedSystemDeflection',)


class MountableComponentCompoundAdvancedSystemDeflection(_7148.ComponentCompoundAdvancedSystemDeflection):
    '''MountableComponentCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_7070.MountableComponentAdvancedSystemDeflection]':
        '''List[MountableComponentAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7070.MountableComponentAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_7070.MountableComponentAdvancedSystemDeflection]':
        '''List[MountableComponentAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7070.MountableComponentAdvancedSystemDeflection))
        return value
