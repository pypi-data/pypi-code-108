'''_4216.py

CVTPulleyCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4069
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4262
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'CVTPulleyCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyCompoundParametricStudyTool',)


class CVTPulleyCompoundParametricStudyTool(_4262.PulleyCompoundParametricStudyTool):
    '''CVTPulleyCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_4069.CVTPulleyParametricStudyTool]':
        '''List[CVTPulleyParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4069.CVTPulleyParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4069.CVTPulleyParametricStudyTool]':
        '''List[CVTPulleyParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4069.CVTPulleyParametricStudyTool))
        return value
