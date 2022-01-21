'''_4251.py

MountableComponentCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4112
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4199
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'MountableComponentCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundParametricStudyTool',)


class MountableComponentCompoundParametricStudyTool(_4199.ComponentCompoundParametricStudyTool):
    '''MountableComponentCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4112.MountableComponentParametricStudyTool]':
        '''List[MountableComponentParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4112.MountableComponentParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4112.MountableComponentParametricStudyTool]':
        '''List[MountableComponentParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4112.MountableComponentParametricStudyTool))
        return value
