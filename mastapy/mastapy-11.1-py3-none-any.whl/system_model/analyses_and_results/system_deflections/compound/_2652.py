'''_2652.py

InterMountableComponentConnectionCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2502
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2621
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'InterMountableComponentConnectionCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundSystemDeflection',)


class InterMountableComponentConnectionCompoundSystemDeflection(_2621.ConnectionCompoundSystemDeflection):
    '''InterMountableComponentConnectionCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2502.InterMountableComponentConnectionSystemDeflection]':
        '''List[InterMountableComponentConnectionSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2502.InterMountableComponentConnectionSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2502.InterMountableComponentConnectionSystemDeflection]':
        '''List[InterMountableComponentConnectionSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2502.InterMountableComponentConnectionSystemDeflection))
        return value
