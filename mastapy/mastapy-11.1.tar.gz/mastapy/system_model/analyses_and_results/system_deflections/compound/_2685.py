'''_2685.py

ShaftToMountableComponentConnectionCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2540
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2589
from mastapy._internal.python_net import python_net_import

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ShaftToMountableComponentConnectionCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftToMountableComponentConnectionCompoundSystemDeflection',)


class ShaftToMountableComponentConnectionCompoundSystemDeflection(_2589.AbstractShaftToMountableComponentConnectionCompoundSystemDeflection):
    '''ShaftToMountableComponentConnectionCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftToMountableComponentConnectionCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2540.ShaftToMountableComponentConnectionSystemDeflection]':
        '''List[ShaftToMountableComponentConnectionSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2540.ShaftToMountableComponentConnectionSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2540.ShaftToMountableComponentConnectionSystemDeflection]':
        '''List[ShaftToMountableComponentConnectionSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2540.ShaftToMountableComponentConnectionSystemDeflection))
        return value
