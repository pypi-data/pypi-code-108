'''_2664.py

MountableComponentCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2517
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2611
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'MountableComponentCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundSystemDeflection',)


class MountableComponentCompoundSystemDeflection(_2611.ComponentCompoundSystemDeflection):
    '''MountableComponentCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2517.MountableComponentSystemDeflection]':
        '''List[MountableComponentSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2517.MountableComponentSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2517.MountableComponentSystemDeflection]':
        '''List[MountableComponentSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2517.MountableComponentSystemDeflection))
        return value
