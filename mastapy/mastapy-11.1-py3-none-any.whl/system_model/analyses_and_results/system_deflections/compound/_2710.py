'''_2710.py

VirtualComponentCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2570
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2664
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'VirtualComponentCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundSystemDeflection',)


class VirtualComponentCompoundSystemDeflection(_2664.MountableComponentCompoundSystemDeflection):
    '''VirtualComponentCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2570.VirtualComponentSystemDeflection]':
        '''List[VirtualComponentSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2570.VirtualComponentSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2570.VirtualComponentSystemDeflection]':
        '''List[VirtualComponentSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2570.VirtualComponentSystemDeflection))
        return value
