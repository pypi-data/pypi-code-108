'''_2662.py

MassDiscCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2514
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2710
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'MassDiscCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundSystemDeflection',)


class MassDiscCompoundSystemDeflection(_2710.VirtualComponentCompoundSystemDeflection):
    '''MassDiscCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2514.MassDiscSystemDeflection]':
        '''List[MassDiscSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2514.MassDiscSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundSystemDeflection]':
        '''List[MassDiscCompoundSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2514.MassDiscSystemDeflection]':
        '''List[MassDiscSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2514.MassDiscSystemDeflection))
        return value
