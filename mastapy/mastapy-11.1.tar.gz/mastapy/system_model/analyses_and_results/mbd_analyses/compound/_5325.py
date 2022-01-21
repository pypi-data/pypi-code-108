'''_5325.py

KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2279
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5323, _5324, _5322
from mastapy.system_model.analyses_and_results.mbd_analyses import _5181
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis',)


class KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis(_5322.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis):
    '''KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears_compound_multibody_dynamics_analysis(self) -> 'List[_5323.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis]: 'KlingelnbergCycloPalloidHypoidGearsCompoundMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsCompoundMultibodyDynamicsAnalysis, constructor.new(_5323.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_compound_multibody_dynamics_analysis(self) -> 'List[_5324.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis]: 'KlingelnbergCycloPalloidHypoidMeshesCompoundMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesCompoundMultibodyDynamicsAnalysis, constructor.new(_5324.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5181.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5181.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_5181.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5181.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis))
        return value
