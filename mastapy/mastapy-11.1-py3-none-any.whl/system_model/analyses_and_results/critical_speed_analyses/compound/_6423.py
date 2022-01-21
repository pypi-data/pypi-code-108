'''_6423.py

ConicalGearSetCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6449
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ConicalGearSetCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetCompoundCriticalSpeedAnalysis',)


class ConicalGearSetCompoundCriticalSpeedAnalysis(_6449.GearSetCompoundCriticalSpeedAnalysis):
    '''ConicalGearSetCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_6292.ConicalGearSetCriticalSpeedAnalysis]':
        '''List[ConicalGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6292.ConicalGearSetCriticalSpeedAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6292.ConicalGearSetCriticalSpeedAnalysis]':
        '''List[ConicalGearSetCriticalSpeedAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6292.ConicalGearSetCriticalSpeedAnalysis))
        return value
