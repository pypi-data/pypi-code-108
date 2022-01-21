'''_4177.py

AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4030
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4209
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool',)


class AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool(_4209.ConnectionCompoundParametricStudyTool):
    '''AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4030.AbstractShaftToMountableComponentConnectionParametricStudyTool]':
        '''List[AbstractShaftToMountableComponentConnectionParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4030.AbstractShaftToMountableComponentConnectionParametricStudyTool))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4030.AbstractShaftToMountableComponentConnectionParametricStudyTool]':
        '''List[AbstractShaftToMountableComponentConnectionParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4030.AbstractShaftToMountableComponentConnectionParametricStudyTool))
        return value
