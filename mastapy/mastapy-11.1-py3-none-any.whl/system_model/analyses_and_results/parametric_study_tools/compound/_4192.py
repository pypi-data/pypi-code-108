'''_4192.py

BevelGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4045
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4180
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'BevelGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetCompoundParametricStudyTool',)


class BevelGearSetCompoundParametricStudyTool(_4180.AGMAGleasonConicalGearSetCompoundParametricStudyTool):
    '''BevelGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4045.BevelGearSetParametricStudyTool]':
        '''List[BevelGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4045.BevelGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4045.BevelGearSetParametricStudyTool]':
        '''List[BevelGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4045.BevelGearSetParametricStudyTool))
        return value
