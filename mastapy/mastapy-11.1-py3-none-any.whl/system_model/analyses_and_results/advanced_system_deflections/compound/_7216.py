'''_7216.py

RollingRingConnectionCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _2034
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7086
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7188
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'RollingRingConnectionCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionCompoundAdvancedSystemDeflection',)


class RollingRingConnectionCompoundAdvancedSystemDeflection(_7188.InterMountableComponentConnectionCompoundAdvancedSystemDeflection):
    '''RollingRingConnectionCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2034.RollingRingConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2034.RollingRingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_7086.RollingRingConnectionAdvancedSystemDeflection]':
        '''List[RollingRingConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_7086.RollingRingConnectionAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingConnectionCompoundAdvancedSystemDeflection]':
        '''List[RollingRingConnectionCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingConnectionCompoundAdvancedSystemDeflection))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_7086.RollingRingConnectionAdvancedSystemDeflection]':
        '''List[RollingRingConnectionAdvancedSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_7086.RollingRingConnectionAdvancedSystemDeflection))
        return value
