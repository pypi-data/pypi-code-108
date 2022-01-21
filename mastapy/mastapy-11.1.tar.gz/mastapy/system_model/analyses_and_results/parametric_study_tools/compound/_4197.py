'''_4197.py

ClutchHalfCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4049
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4213
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ClutchHalfCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfCompoundParametricStudyTool',)


class ClutchHalfCompoundParametricStudyTool(_4213.CouplingHalfCompoundParametricStudyTool):
    '''ClutchHalfCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4049.ClutchHalfParametricStudyTool]':
        '''List[ClutchHalfParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4049.ClutchHalfParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4049.ClutchHalfParametricStudyTool]':
        '''List[ClutchHalfParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4049.ClutchHalfParametricStudyTool))
        return value
