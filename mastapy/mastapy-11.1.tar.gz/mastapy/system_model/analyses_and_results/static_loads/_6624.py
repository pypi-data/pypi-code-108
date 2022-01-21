'''_6624.py

HypoidGearSetLoadCase
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6622, _6623, _6530
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'HypoidGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetLoadCase',)


class HypoidGearSetLoadCase(_6530.AGMAGleasonConicalGearSetLoadCase):
    '''HypoidGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def gears(self) -> 'List[_6622.HypoidGearLoadCase]':
        '''List[HypoidGearLoadCase]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_6622.HypoidGearLoadCase))
        return value

    @property
    def hypoid_gears_load_case(self) -> 'List[_6622.HypoidGearLoadCase]':
        '''List[HypoidGearLoadCase]: 'HypoidGearsLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsLoadCase, constructor.new(_6622.HypoidGearLoadCase))
        return value

    @property
    def hypoid_meshes_load_case(self) -> 'List[_6623.HypoidGearMeshLoadCase]':
        '''List[HypoidGearMeshLoadCase]: 'HypoidMeshesLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesLoadCase, constructor.new(_6623.HypoidGearMeshLoadCase))
        return value
