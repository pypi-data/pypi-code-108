'''_4200.py

ConceptCouplingCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2321
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4055
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4211
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ConceptCouplingCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingCompoundParametricStudyTool',)


class ConceptCouplingCompoundParametricStudyTool(_4211.CouplingCompoundParametricStudyTool):
    '''ConceptCouplingCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2321.ConceptCoupling':
        '''ConceptCoupling: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2321.ConceptCoupling)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2321.ConceptCoupling':
        '''ConceptCoupling: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2321.ConceptCoupling)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4055.ConceptCouplingParametricStudyTool]':
        '''List[ConceptCouplingParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4055.ConceptCouplingParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4055.ConceptCouplingParametricStudyTool]':
        '''List[ConceptCouplingParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4055.ConceptCouplingParametricStudyTool))
        return value
