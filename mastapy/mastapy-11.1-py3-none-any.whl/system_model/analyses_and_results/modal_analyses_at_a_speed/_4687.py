'''_4687.py

WormGearSetModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4686, _4685, _4622
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed', 'WormGearSetModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetModalAnalysisAtASpeed',)


class WormGearSetModalAnalysisAtASpeed(_4622.GearSetModalAnalysisAtASpeed):
    '''WormGearSetModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6703.WormGearSetLoadCase':
        '''WormGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6703.WormGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def worm_gears_modal_analysis_at_a_speed(self) -> 'List[_4686.WormGearModalAnalysisAtASpeed]':
        '''List[WormGearModalAnalysisAtASpeed]: 'WormGearsModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsModalAnalysisAtASpeed, constructor.new(_4686.WormGearModalAnalysisAtASpeed))
        return value

    @property
    def worm_meshes_modal_analysis_at_a_speed(self) -> 'List[_4685.WormGearMeshModalAnalysisAtASpeed]':
        '''List[WormGearMeshModalAnalysisAtASpeed]: 'WormMeshesModalAnalysisAtASpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesModalAnalysisAtASpeed, constructor.new(_4685.WormGearMeshModalAnalysisAtASpeed))
        return value
