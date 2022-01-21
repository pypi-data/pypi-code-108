'''_4762.py

KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2279
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4760, _4761, _4759
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4633
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed',)


class KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed(_4759.KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysisAtASpeed):
    '''KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysisAtASpeed.TYPE'):
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
    def klingelnberg_cyclo_palloid_hypoid_gears_compound_modal_analysis_at_a_speed(self) -> 'List[_4760.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysisAtASpeed]: 'KlingelnbergCycloPalloidHypoidGearsCompoundModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsCompoundModalAnalysisAtASpeed, constructor.new(_4760.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysisAtASpeed))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_compound_modal_analysis_at_a_speed(self) -> 'List[_4761.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed]: 'KlingelnbergCycloPalloidHypoidMeshesCompoundModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesCompoundModalAnalysisAtASpeed, constructor.new(_4761.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4633.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed))
        return value
