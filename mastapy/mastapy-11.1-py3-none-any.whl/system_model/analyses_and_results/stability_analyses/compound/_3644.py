'''_3644.py

BevelDifferentialPlanetGearCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3512
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3641
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'BevelDifferentialPlanetGearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGearCompoundStabilityAnalysis',)


class BevelDifferentialPlanetGearCompoundStabilityAnalysis(_3641.BevelDifferentialGearCompoundStabilityAnalysis):
    '''BevelDifferentialPlanetGearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_3512.BevelDifferentialPlanetGearStabilityAnalysis]':
        '''List[BevelDifferentialPlanetGearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3512.BevelDifferentialPlanetGearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3512.BevelDifferentialPlanetGearStabilityAnalysis]':
        '''List[BevelDifferentialPlanetGearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3512.BevelDifferentialPlanetGearStabilityAnalysis))
        return value
