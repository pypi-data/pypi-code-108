'''_4240.py

KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4101
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4206
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool',)


class KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool(_4206.ConicalGearCompoundParametricStudyTool):
    '''KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4101.KlingelnbergCycloPalloidConicalGearParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidConicalGearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4101.KlingelnbergCycloPalloidConicalGearParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4101.KlingelnbergCycloPalloidConicalGearParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidConicalGearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4101.KlingelnbergCycloPalloidConicalGearParametricStudyTool))
        return value
