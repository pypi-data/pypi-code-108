'''_2703.py

SynchroniserPartCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2557
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2625
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'SynchroniserPartCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundSystemDeflection',)


class SynchroniserPartCompoundSystemDeflection(_2625.CouplingHalfCompoundSystemDeflection):
    '''SynchroniserPartCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2557.SynchroniserPartSystemDeflection]':
        '''List[SynchroniserPartSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2557.SynchroniserPartSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2557.SynchroniserPartSystemDeflection]':
        '''List[SynchroniserPartSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2557.SynchroniserPartSystemDeflection))
        return value
