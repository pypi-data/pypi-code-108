'''_7218.py

ShaftCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7088
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7124
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ShaftCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundAdvancedSystemDeflection',)


class ShaftCompoundAdvancedSystemDeflection(_7124.AbstractShaftCompoundAdvancedSystemDeflection):
    '''ShaftCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7088.ShaftAdvancedSystemDeflection]':
        '''List[ShaftAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7088.ShaftAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundAdvancedSystemDeflection]':
        '''List[ShaftCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7088.ShaftAdvancedSystemDeflection]':
        '''List[ShaftAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7088.ShaftAdvancedSystemDeflection))
        return value
