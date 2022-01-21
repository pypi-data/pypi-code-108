'''_4175.py

AbstractShaftCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4029
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4176
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AbstractShaftCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftCompoundParametricStudyTool',)


class AbstractShaftCompoundParametricStudyTool(_4176.AbstractShaftOrHousingCompoundParametricStudyTool):
    '''AbstractShaftCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4029.AbstractShaftParametricStudyTool]':
        '''List[AbstractShaftParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4029.AbstractShaftParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4029.AbstractShaftParametricStudyTool]':
        '''List[AbstractShaftParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4029.AbstractShaftParametricStudyTool))
        return value
