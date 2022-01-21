'''_4195.py

ClutchCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2318
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4050
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4211
from mastapy._internal.python_net import python_net_import

_CLUTCH_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ClutchCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchCompoundParametricStudyTool',)


class ClutchCompoundParametricStudyTool(_4211.CouplingCompoundParametricStudyTool):
    '''ClutchCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2318.Clutch':
        '''Clutch: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2318.Clutch)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2318.Clutch':
        '''Clutch: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2318.Clutch)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4050.ClutchParametricStudyTool]':
        '''List[ClutchParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4050.ClutchParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4050.ClutchParametricStudyTool]':
        '''List[ClutchParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4050.ClutchParametricStudyTool))
        return value
