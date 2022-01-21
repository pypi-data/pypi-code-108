'''_4378.py

KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model.gears import _2281
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6637
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4377, _4376, _4372
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness', 'KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness',)


class KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness(_4372.KlingelnbergCycloPalloidConicalGearSetModalAnalysisAtAStiffness):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gears_modal_analysis_at_a_stiffness(self) -> 'List[_4377.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtAStiffness]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtAStiffness]: 'KlingelnbergCycloPalloidSpiralBevelGearsModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearsModalAnalysisAtAStiffness, constructor.new(_4377.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtAStiffness))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshes_modal_analysis_at_a_stiffness(self) -> 'List[_4376.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness]: 'KlingelnbergCycloPalloidSpiralBevelMeshesModalAnalysisAtAStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshesModalAnalysisAtAStiffness, constructor.new(_4376.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness))
        return value
