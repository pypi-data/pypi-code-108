'''_4206.py

ConicalGearCompoundParametricStudyTool
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4060
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4232
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ConicalGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundParametricStudyTool',)


class ConicalGearCompoundParametricStudyTool(_4232.GearCompoundParametricStudyTool):
    '''ConicalGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundParametricStudyTool]':
        '''List[ConicalGearCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4060.ConicalGearParametricStudyTool]':
        '''List[ConicalGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4060.ConicalGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4060.ConicalGearParametricStudyTool]':
        '''List[ConicalGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4060.ConicalGearParametricStudyTool))
        return value
