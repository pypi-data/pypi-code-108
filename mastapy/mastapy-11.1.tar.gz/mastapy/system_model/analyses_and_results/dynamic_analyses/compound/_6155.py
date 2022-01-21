'''_6155.py

ConicalGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6025
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6181
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'ConicalGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundDynamicAnalysis',)


class ConicalGearCompoundDynamicAnalysis(_6181.GearCompoundDynamicAnalysis):
    '''ConicalGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundDynamicAnalysis]':
        '''List[ConicalGearCompoundDynamicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6025.ConicalGearDynamicAnalysis]':
        '''List[ConicalGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6025.ConicalGearDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6025.ConicalGearDynamicAnalysis]':
        '''List[ConicalGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6025.ConicalGearDynamicAnalysis))
        return value
