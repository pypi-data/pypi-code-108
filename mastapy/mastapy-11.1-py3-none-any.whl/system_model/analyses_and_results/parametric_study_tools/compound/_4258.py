'''_4258.py

PlanetaryGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4129
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4223
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'PlanetaryGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetCompoundParametricStudyTool',)


class PlanetaryGearSetCompoundParametricStudyTool(_4223.CylindricalGearSetCompoundParametricStudyTool):
    '''PlanetaryGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4129.PlanetaryGearSetParametricStudyTool]':
        '''List[PlanetaryGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4129.PlanetaryGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4129.PlanetaryGearSetParametricStudyTool]':
        '''List[PlanetaryGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4129.PlanetaryGearSetParametricStudyTool))
        return value
