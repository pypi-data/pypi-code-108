'''_4270.py

ShaftHubConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2338
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4140
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4210
from mastapy._internal.python_net import python_net_import

_SHAFT_HUB_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ShaftHubConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftHubConnectionCompoundParametricStudyTool',)


class ShaftHubConnectionCompoundParametricStudyTool(_4210.ConnectorCompoundParametricStudyTool):
    '''ShaftHubConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SHAFT_HUB_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftHubConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2338.ShaftHubConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4140.ShaftHubConnectionParametricStudyTool]':
        '''List[ShaftHubConnectionParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4140.ShaftHubConnectionParametricStudyTool))
        return value

    @property
    def planetaries(self) -> 'List[ShaftHubConnectionCompoundParametricStudyTool]':
        '''List[ShaftHubConnectionCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftHubConnectionCompoundParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4140.ShaftHubConnectionParametricStudyTool]':
        '''List[ShaftHubConnectionParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4140.ShaftHubConnectionParametricStudyTool))
        return value
