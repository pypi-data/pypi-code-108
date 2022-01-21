'''_7126.py

AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6990
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7158
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection',)


class AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection(_7158.ConnectionCompoundAdvancedSystemDeflection):
    '''AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6990.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]':
        '''List[AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6990.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6990.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]':
        '''List[AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6990.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection))
        return value
