'''_4272.py

SpecialisedAssemblyCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4143
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4174
from mastapy._internal.python_net import python_net_import

_SPECIALISED_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'SpecialisedAssemblyCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecialisedAssemblyCompoundParametricStudyTool',)


class SpecialisedAssemblyCompoundParametricStudyTool(_4174.AbstractAssemblyCompoundParametricStudyTool):
    '''SpecialisedAssemblyCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SPECIALISED_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecialisedAssemblyCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4143.SpecialisedAssemblyParametricStudyTool]':
        '''List[SpecialisedAssemblyParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4143.SpecialisedAssemblyParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4143.SpecialisedAssemblyParametricStudyTool]':
        '''List[SpecialisedAssemblyParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4143.SpecialisedAssemblyParametricStudyTool))
        return value
