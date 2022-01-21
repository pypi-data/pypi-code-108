'''_7239.py

SynchroniserSleeveCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2346
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7109
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7238
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SLEEVE_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'SynchroniserSleeveCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSleeveCompoundAdvancedSystemDeflection',)


class SynchroniserSleeveCompoundAdvancedSystemDeflection(_7238.SynchroniserPartCompoundAdvancedSystemDeflection):
    '''SynchroniserSleeveCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SLEEVE_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSleeveCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2346.SynchroniserSleeve)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7109.SynchroniserSleeveAdvancedSystemDeflection]':
        '''List[SynchroniserSleeveAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7109.SynchroniserSleeveAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7109.SynchroniserSleeveAdvancedSystemDeflection]':
        '''List[SynchroniserSleeveAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7109.SynchroniserSleeveAdvancedSystemDeflection))
        return value
