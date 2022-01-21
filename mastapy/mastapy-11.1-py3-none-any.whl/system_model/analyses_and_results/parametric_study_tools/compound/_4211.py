'''_4211.py

CouplingCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4066
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4272
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'CouplingCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundParametricStudyTool',)


class CouplingCompoundParametricStudyTool(_4272.SpecialisedAssemblyCompoundParametricStudyTool):
    '''CouplingCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4066.CouplingParametricStudyTool]':
        '''List[CouplingParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4066.CouplingParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4066.CouplingParametricStudyTool]':
        '''List[CouplingParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4066.CouplingParametricStudyTool))
        return value
