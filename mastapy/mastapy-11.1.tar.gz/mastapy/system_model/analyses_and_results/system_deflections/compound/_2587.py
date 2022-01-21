'''_2587.py

AbstractShaftCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2427
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2588
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'AbstractShaftCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundSystemDeflection',)


class AbstractShaftCompoundSystemDeflection(_2588.AbstractShaftOrHousingCompoundSystemDeflection):
    '''AbstractShaftCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2427.AbstractShaftSystemDeflection]':
        '''List[AbstractShaftSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2427.AbstractShaftSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2427.AbstractShaftSystemDeflection]':
        '''List[AbstractShaftSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2427.AbstractShaftSystemDeflection))
        return value
