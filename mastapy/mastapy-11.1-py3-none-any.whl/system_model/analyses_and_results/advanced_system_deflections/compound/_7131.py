'''_7131.py

BearingCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2182
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6998
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7159
from mastapy._internal.python_net import python_net_import

_BEARING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'BearingCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingCompoundAdvancedSystemDeflection',)


class BearingCompoundAdvancedSystemDeflection(_7159.ConnectorCompoundAdvancedSystemDeflection):
    '''BearingCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEARING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2182.Bearing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6998.BearingAdvancedSystemDeflection]':
        '''List[BearingAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6998.BearingAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[BearingCompoundAdvancedSystemDeflection]':
        '''List[BearingCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(BearingCompoundAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6998.BearingAdvancedSystemDeflection]':
        '''List[BearingAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6998.BearingAdvancedSystemDeflection))
        return value
