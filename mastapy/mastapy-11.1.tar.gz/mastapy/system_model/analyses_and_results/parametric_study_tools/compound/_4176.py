'''_4176.py

AbstractShaftOrHousingCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4028
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4199
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AbstractShaftOrHousingCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundParametricStudyTool',)


class AbstractShaftOrHousingCompoundParametricStudyTool(_4199.ComponentCompoundParametricStudyTool):
    '''AbstractShaftOrHousingCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4028.AbstractShaftOrHousingParametricStudyTool]':
        '''List[AbstractShaftOrHousingParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4028.AbstractShaftOrHousingParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4028.AbstractShaftOrHousingParametricStudyTool]':
        '''List[AbstractShaftOrHousingParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4028.AbstractShaftOrHousingParametricStudyTool))
        return value
