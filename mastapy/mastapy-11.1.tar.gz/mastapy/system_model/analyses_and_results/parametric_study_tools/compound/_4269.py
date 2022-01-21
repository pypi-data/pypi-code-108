'''_4269.py

ShaftCompoundParametricStudyTool
'''


from typing import List

from mastapy.shafts import _19
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4141
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4175
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ShaftCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundParametricStudyTool',)


class ShaftCompoundParametricStudyTool(_4175.AbstractShaftCompoundParametricStudyTool):
    '''ShaftCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_duty_cycle_results(self) -> '_19.ShaftDamageResults':
        '''ShaftDamageResults: 'ShaftDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_19.ShaftDamageResults)(self.wrapped.ShaftDutyCycleResults) if self.wrapped.ShaftDutyCycleResults is not None else None

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4141.ShaftParametricStudyTool]':
        '''List[ShaftParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4141.ShaftParametricStudyTool))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundParametricStudyTool]':
        '''List[ShaftCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4141.ShaftParametricStudyTool]':
        '''List[ShaftParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4141.ShaftParametricStudyTool))
        return value
