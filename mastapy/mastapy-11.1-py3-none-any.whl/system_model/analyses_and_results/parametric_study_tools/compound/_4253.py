'''_4253.py

PartCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4124
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7263
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'PartCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundParametricStudyTool',)


class PartCompoundParametricStudyTool(_7263.PartCompoundAnalysis):
    '''PartCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4124.PartParametricStudyTool]':
        '''List[PartParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4124.PartParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4124.PartParametricStudyTool]':
        '''List[PartParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4124.PartParametricStudyTool))
        return value
