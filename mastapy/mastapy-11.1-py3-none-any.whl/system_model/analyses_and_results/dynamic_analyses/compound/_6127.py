'''_6127.py

AGMAGleasonConicalGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _5997
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6155
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'AGMAGleasonConicalGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundDynamicAnalysis',)


class AGMAGleasonConicalGearCompoundDynamicAnalysis(_6155.ConicalGearCompoundDynamicAnalysis):
    '''AGMAGleasonConicalGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5997.AGMAGleasonConicalGearDynamicAnalysis]':
        '''List[AGMAGleasonConicalGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5997.AGMAGleasonConicalGearDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5997.AGMAGleasonConicalGearDynamicAnalysis]':
        '''List[AGMAGleasonConicalGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5997.AGMAGleasonConicalGearDynamicAnalysis))
        return value
