'''_4300.py

ZerolBevelGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2293
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4172
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4190
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ZerolBevelGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearCompoundParametricStudyTool',)


class ZerolBevelGearCompoundParametricStudyTool(_4190.BevelGearCompoundParametricStudyTool):
    '''ZerolBevelGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2293.ZerolBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4172.ZerolBevelGearParametricStudyTool]':
        '''List[ZerolBevelGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4172.ZerolBevelGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4172.ZerolBevelGearParametricStudyTool]':
        '''List[ZerolBevelGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4172.ZerolBevelGearParametricStudyTool))
        return value
