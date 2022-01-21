'''_2614.py

ConceptCouplingHalfCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2322
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2453
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2625
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_HALF_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ConceptCouplingHalfCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingHalfCompoundSystemDeflection',)


class ConceptCouplingHalfCompoundSystemDeflection(_2625.CouplingHalfCompoundSystemDeflection):
    '''ConceptCouplingHalfCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_HALF_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingHalfCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2322.ConceptCouplingHalf':
        '''ConceptCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2322.ConceptCouplingHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2453.ConceptCouplingHalfSystemDeflection]':
        '''List[ConceptCouplingHalfSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2453.ConceptCouplingHalfSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2453.ConceptCouplingHalfSystemDeflection]':
        '''List[ConceptCouplingHalfSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2453.ConceptCouplingHalfSystemDeflection))
        return value
