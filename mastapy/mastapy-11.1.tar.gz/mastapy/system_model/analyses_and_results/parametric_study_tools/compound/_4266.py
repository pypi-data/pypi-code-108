'''_4266.py

RollingRingCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4138
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4213
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'RollingRingCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingCompoundParametricStudyTool',)


class RollingRingCompoundParametricStudyTool(_4213.CouplingHalfCompoundParametricStudyTool):
    '''RollingRingCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4138.RollingRingParametricStudyTool]':
        '''List[RollingRingParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4138.RollingRingParametricStudyTool))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingCompoundParametricStudyTool]':
        '''List[RollingRingCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingCompoundParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4138.RollingRingParametricStudyTool]':
        '''List[RollingRingParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4138.RollingRingParametricStudyTool))
        return value
