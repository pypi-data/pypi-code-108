'''_4276.py

SpringDamperCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2340
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4149
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4211
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'SpringDamperCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperCompoundParametricStudyTool',)


class SpringDamperCompoundParametricStudyTool(_4211.CouplingCompoundParametricStudyTool):
    '''SpringDamperCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2340.SpringDamper)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2340.SpringDamper)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4149.SpringDamperParametricStudyTool]':
        '''List[SpringDamperParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4149.SpringDamperParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4149.SpringDamperParametricStudyTool]':
        '''List[SpringDamperParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4149.SpringDamperParametricStudyTool))
        return value
