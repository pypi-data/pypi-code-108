'''_7209.py

PointLoadCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7079
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7245
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'PointLoadCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadCompoundAdvancedSystemDeflection',)


class PointLoadCompoundAdvancedSystemDeflection(_7245.VirtualComponentCompoundAdvancedSystemDeflection):
    '''PointLoadCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7079.PointLoadAdvancedSystemDeflection]':
        '''List[PointLoadAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7079.PointLoadAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7079.PointLoadAdvancedSystemDeflection]':
        '''List[PointLoadAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7079.PointLoadAdvancedSystemDeflection))
        return value
