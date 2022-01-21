'''_4199.py

ComponentCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4052
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4253
from mastapy._internal.python_net import python_net_import

_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ComponentCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentCompoundParametricStudyTool',)


class ComponentCompoundParametricStudyTool(_4253.PartCompoundParametricStudyTool):
    '''ComponentCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4052.ComponentParametricStudyTool]':
        '''List[ComponentParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4052.ComponentParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4052.ComponentParametricStudyTool]':
        '''List[ComponentParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4052.ComponentParametricStudyTool))
        return value
