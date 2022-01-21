'''_4241.py

KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4100
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4207
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool',)


class KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool(_4207.ConicalGearMeshCompoundParametricStudyTool):
    '''KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearMeshCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4100.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4100.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4100.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4100.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool))
        return value
