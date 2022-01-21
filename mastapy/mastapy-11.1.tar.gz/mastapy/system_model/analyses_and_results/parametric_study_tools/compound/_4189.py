'''_4189.py

BevelDifferentialSunGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4042
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4185
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_SUN_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'BevelDifferentialSunGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialSunGearCompoundParametricStudyTool',)


class BevelDifferentialSunGearCompoundParametricStudyTool(_4185.BevelDifferentialGearCompoundParametricStudyTool):
    '''BevelDifferentialSunGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_SUN_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialSunGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_4042.BevelDifferentialSunGearParametricStudyTool]':
        '''List[BevelDifferentialSunGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4042.BevelDifferentialSunGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4042.BevelDifferentialSunGearParametricStudyTool]':
        '''List[BevelDifferentialSunGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4042.BevelDifferentialSunGearParametricStudyTool))
        return value
