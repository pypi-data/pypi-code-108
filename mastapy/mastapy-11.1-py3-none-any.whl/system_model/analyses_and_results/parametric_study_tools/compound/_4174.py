'''_4174.py

AbstractAssemblyCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4027
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4253
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AbstractAssemblyCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAssemblyCompoundParametricStudyTool',)


class AbstractAssemblyCompoundParametricStudyTool(_4253.PartCompoundParametricStudyTool):
    '''AbstractAssemblyCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAssemblyCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4027.AbstractAssemblyParametricStudyTool]':
        '''List[AbstractAssemblyParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4027.AbstractAssemblyParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4027.AbstractAssemblyParametricStudyTool]':
        '''List[AbstractAssemblyParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4027.AbstractAssemblyParametricStudyTool))
        return value
