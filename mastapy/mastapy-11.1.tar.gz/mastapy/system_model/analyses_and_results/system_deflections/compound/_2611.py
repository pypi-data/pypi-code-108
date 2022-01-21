'''_2611.py

ComponentCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2450
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2666
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ComponentCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundSystemDeflection',)


class ComponentCompoundSystemDeflection(_2666.PartCompoundSystemDeflection):
    '''ComponentCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2450.ComponentSystemDeflection]':
        '''List[ComponentSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2450.ComponentSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2450.ComponentSystemDeflection]':
        '''List[ComponentSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2450.ComponentSystemDeflection))
        return value
