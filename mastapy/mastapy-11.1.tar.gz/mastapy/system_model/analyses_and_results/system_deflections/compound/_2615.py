'''_2615.py

ConceptGearCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2261
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2457
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2645
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ConceptGearCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearCompoundSystemDeflection',)


class ConceptGearCompoundSystemDeflection(_2645.GearCompoundSystemDeflection):
    '''ConceptGearCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2261.ConceptGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2457.ConceptGearSystemDeflection]':
        '''List[ConceptGearSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2457.ConceptGearSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2457.ConceptGearSystemDeflection]':
        '''List[ConceptGearSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2457.ConceptGearSystemDeflection))
        return value
