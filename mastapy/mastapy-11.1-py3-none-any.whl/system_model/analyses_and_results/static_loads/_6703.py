'''_6703.py

WormGearSetLoadCase
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6701, _6702, _6610
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'WormGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetLoadCase',)


class WormGearSetLoadCase(_6610.GearSetLoadCase):
    '''WormGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetLoadCase.TYPE'):
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
    def gears(self) -> 'List[_6701.WormGearLoadCase]':
        '''List[WormGearLoadCase]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_6701.WormGearLoadCase))
        return value

    @property
    def worm_gears_load_case(self) -> 'List[_6701.WormGearLoadCase]':
        '''List[WormGearLoadCase]: 'WormGearsLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsLoadCase, constructor.new(_6701.WormGearLoadCase))
        return value

    @property
    def worm_meshes_load_case(self) -> 'List[_6702.WormGearMeshLoadCase]':
        '''List[WormGearMeshLoadCase]: 'WormMeshesLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesLoadCase, constructor.new(_6702.WormGearMeshLoadCase))
        return value
