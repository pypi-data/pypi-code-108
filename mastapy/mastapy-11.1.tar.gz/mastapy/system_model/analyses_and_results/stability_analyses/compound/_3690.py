'''_3690.py

GearSetCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3558
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3728
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'GearSetCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundStabilityAnalysis',)


class GearSetCompoundStabilityAnalysis(_3728.SpecialisedAssemblyCompoundStabilityAnalysis):
    '''GearSetCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_3558.GearSetStabilityAnalysis]':
        '''List[GearSetStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3558.GearSetStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3558.GearSetStabilityAnalysis]':
        '''List[GearSetStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3558.GearSetStabilityAnalysis))
        return value
