'''_4190.py

BevelGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4044
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4178
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'BevelGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundParametricStudyTool',)


class BevelGearCompoundParametricStudyTool(_4178.AGMAGleasonConicalGearCompoundParametricStudyTool):
    '''BevelGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4044.BevelGearParametricStudyTool]':
        '''List[BevelGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4044.BevelGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4044.BevelGearParametricStudyTool]':
        '''List[BevelGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4044.BevelGearParametricStudyTool))
        return value
