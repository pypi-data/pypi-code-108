'''_6207.py

PlanetaryGearSetCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6078
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6172
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'PlanetaryGearSetCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetCompoundDynamicAnalysis',)


class PlanetaryGearSetCompoundDynamicAnalysis(_6172.CylindricalGearSetCompoundDynamicAnalysis):
    '''PlanetaryGearSetCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6078.PlanetaryGearSetDynamicAnalysis]':
        '''List[PlanetaryGearSetDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6078.PlanetaryGearSetDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6078.PlanetaryGearSetDynamicAnalysis]':
        '''List[PlanetaryGearSetDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6078.PlanetaryGearSetDynamicAnalysis))
        return value
