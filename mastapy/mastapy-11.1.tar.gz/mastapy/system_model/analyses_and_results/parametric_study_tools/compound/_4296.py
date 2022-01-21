'''_4296.py

VirtualComponentCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4167
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4251
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'VirtualComponentCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundParametricStudyTool',)


class VirtualComponentCompoundParametricStudyTool(_4251.MountableComponentCompoundParametricStudyTool):
    '''VirtualComponentCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4167.VirtualComponentParametricStudyTool]':
        '''List[VirtualComponentParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4167.VirtualComponentParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4167.VirtualComponentParametricStudyTool]':
        '''List[VirtualComponentParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4167.VirtualComponentParametricStudyTool))
        return value
