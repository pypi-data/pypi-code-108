'''_5023.py

CylindricalPlanetGearCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4871
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5020
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'CylindricalPlanetGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearCompoundModalAnalysis',)


class CylindricalPlanetGearCompoundModalAnalysis(_5020.CylindricalGearCompoundModalAnalysis):
    '''CylindricalPlanetGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_4871.CylindricalPlanetGearModalAnalysis]':
        '''List[CylindricalPlanetGearModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4871.CylindricalPlanetGearModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4871.CylindricalPlanetGearModalAnalysis]':
        '''List[CylindricalPlanetGearModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4871.CylindricalPlanetGearModalAnalysis))
        return value
