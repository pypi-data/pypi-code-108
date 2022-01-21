'''_7220.py

ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7090
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7126
from mastapy._internal.python_net import python_net_import

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection',)


class ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection(_7126.AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection):
    '''ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_7090.ShaftToMountableComponentConnectionAdvancedSystemDeflection]':
        '''List[ShaftToMountableComponentConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_7090.ShaftToMountableComponentConnectionAdvancedSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_7090.ShaftToMountableComponentConnectionAdvancedSystemDeflection]':
        '''List[ShaftToMountableComponentConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_7090.ShaftToMountableComponentConnectionAdvancedSystemDeflection))
        return value
