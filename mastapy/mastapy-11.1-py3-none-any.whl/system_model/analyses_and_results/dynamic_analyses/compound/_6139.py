'''_6139.py

BevelGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6009
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6127
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'BevelGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundDynamicAnalysis',)


class BevelGearCompoundDynamicAnalysis(_6127.AGMAGleasonConicalGearCompoundDynamicAnalysis):
    '''BevelGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6009.BevelGearDynamicAnalysis]':
        '''List[BevelGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6009.BevelGearDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6009.BevelGearDynamicAnalysis]':
        '''List[BevelGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6009.BevelGearDynamicAnalysis))
        return value
