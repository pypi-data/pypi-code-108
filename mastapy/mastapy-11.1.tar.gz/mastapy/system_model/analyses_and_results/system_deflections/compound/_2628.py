'''_2628.py

CVTPulleyCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2468
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2675
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CVTPulleyCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundSystemDeflection',)


class CVTPulleyCompoundSystemDeflection(_2675.PulleyCompoundSystemDeflection):
    '''CVTPulleyCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_2468.CVTPulleySystemDeflection]':
        '''List[CVTPulleySystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2468.CVTPulleySystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2468.CVTPulleySystemDeflection]':
        '''List[CVTPulleySystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2468.CVTPulleySystemDeflection))
        return value
