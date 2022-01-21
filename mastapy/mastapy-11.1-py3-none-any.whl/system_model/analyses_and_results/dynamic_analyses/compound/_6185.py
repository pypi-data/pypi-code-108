'''_6185.py

HypoidGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2274
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6056
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6127
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'HypoidGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearCompoundDynamicAnalysis',)


class HypoidGearCompoundDynamicAnalysis(_6127.AGMAGleasonConicalGearCompoundDynamicAnalysis):
    '''HypoidGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2274.HypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6056.HypoidGearDynamicAnalysis]':
        '''List[HypoidGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6056.HypoidGearDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6056.HypoidGearDynamicAnalysis]':
        '''List[HypoidGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6056.HypoidGearDynamicAnalysis))
        return value
