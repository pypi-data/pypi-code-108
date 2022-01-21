'''_4224.py

CylindricalPlanetGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4077
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4221
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'CylindricalPlanetGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearCompoundParametricStudyTool',)


class CylindricalPlanetGearCompoundParametricStudyTool(_4221.CylindricalGearCompoundParametricStudyTool):
    '''CylindricalPlanetGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_4077.CylindricalPlanetGearParametricStudyTool]':
        '''List[CylindricalPlanetGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4077.CylindricalPlanetGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4077.CylindricalPlanetGearParametricStudyTool]':
        '''List[CylindricalPlanetGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4077.CylindricalPlanetGearParametricStudyTool))
        return value
