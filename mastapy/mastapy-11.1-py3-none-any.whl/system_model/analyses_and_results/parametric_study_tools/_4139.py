'''_4139.py

RootAssemblyParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2215
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4119, _4121, _4034
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2638
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'RootAssemblyParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyParametricStudyTool',)


class RootAssemblyParametricStudyTool(_4034.AssemblyParametricStudyTool):
    '''RootAssemblyParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def parametric_study_tool_inputs(self) -> '_4119.ParametricStudyTool':
        '''ParametricStudyTool: 'ParametricStudyToolInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4119.ParametricStudyTool)(self.wrapped.ParametricStudyToolInputs) if self.wrapped.ParametricStudyToolInputs is not None else None

    @property
    def results_for_reporting(self) -> '_4121.ParametricStudyToolResultsForReporting':
        '''ParametricStudyToolResultsForReporting: 'ResultsForReporting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4121.ParametricStudyToolResultsForReporting)(self.wrapped.ResultsForReporting) if self.wrapped.ResultsForReporting is not None else None

    @property
    def root_assembly_duty_cycle_results(self) -> 'List[_2638.DutyCycleEfficiencyResults]':
        '''List[DutyCycleEfficiencyResults]: 'RootAssemblyDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RootAssemblyDutyCycleResults, constructor.new(_2638.DutyCycleEfficiencyResults))
        return value
