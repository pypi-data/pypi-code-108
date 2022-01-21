'''_4227.py

FaceGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2268
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4088
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4232
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'FaceGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearCompoundParametricStudyTool',)


class FaceGearCompoundParametricStudyTool(_4232.GearCompoundParametricStudyTool):
    '''FaceGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2268.FaceGear':
        '''FaceGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2268.FaceGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4088.FaceGearParametricStudyTool]':
        '''List[FaceGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4088.FaceGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4088.FaceGearParametricStudyTool]':
        '''List[FaceGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4088.FaceGearParametricStudyTool))
        return value
