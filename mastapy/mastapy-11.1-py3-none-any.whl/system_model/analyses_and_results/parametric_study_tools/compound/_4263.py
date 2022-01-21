'''_4263.py

RingPinsCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4134
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4251
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'RingPinsCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundParametricStudyTool',)


class RingPinsCompoundParametricStudyTool(_4251.MountableComponentCompoundParametricStudyTool):
    '''RingPinsCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4134.RingPinsParametricStudyTool]':
        '''List[RingPinsParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4134.RingPinsParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4134.RingPinsParametricStudyTool]':
        '''List[RingPinsParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4134.RingPinsParametricStudyTool))
        return value
