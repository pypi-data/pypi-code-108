'''_3815.py

CylindricalGearSetPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2266, _2282
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6579, _6651
from mastapy.gears.rating.cylindrical import _428
from mastapy.system_model.analyses_and_results.power_flows import _3814, _3813, _3826
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'CylindricalGearSetPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetPowerFlow',)


class CylindricalGearSetPowerFlow(_3826.GearSetPowerFlow):
    '''CylindricalGearSetPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to CylindricalGearSet. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6579.CylindricalGearSetLoadCase':
        '''CylindricalGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6579.CylindricalGearSetLoadCase.TYPE not in self.wrapped.AssemblyLoadCase.__class__.__mro__:
            raise CastException('Failed to cast assembly_load_case to CylindricalGearSetLoadCase. Expected: {}.'.format(self.wrapped.AssemblyLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyLoadCase.__class__)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def rating(self) -> '_428.CylindricalGearSetRating':
        '''CylindricalGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_428.CylindricalGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_428.CylindricalGearSetRating':
        '''CylindricalGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_428.CylindricalGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def gears_power_flow(self) -> 'List[_3814.CylindricalGearPowerFlow]':
        '''List[CylindricalGearPowerFlow]: 'GearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearsPowerFlow, constructor.new(_3814.CylindricalGearPowerFlow))
        return value

    @property
    def cylindrical_gears_power_flow(self) -> 'List[_3814.CylindricalGearPowerFlow]':
        '''List[CylindricalGearPowerFlow]: 'CylindricalGearsPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearsPowerFlow, constructor.new(_3814.CylindricalGearPowerFlow))
        return value

    @property
    def meshes_power_flow(self) -> 'List[_3813.CylindricalGearMeshPowerFlow]':
        '''List[CylindricalGearMeshPowerFlow]: 'MeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshesPowerFlow, constructor.new(_3813.CylindricalGearMeshPowerFlow))
        return value

    @property
    def cylindrical_meshes_power_flow(self) -> 'List[_3813.CylindricalGearMeshPowerFlow]':
        '''List[CylindricalGearMeshPowerFlow]: 'CylindricalMeshesPowerFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshesPowerFlow, constructor.new(_3813.CylindricalGearMeshPowerFlow))
        return value

    @property
    def ratings_for_all_designs(self) -> 'List[_428.CylindricalGearSetRating]':
        '''List[CylindricalGearSetRating]: 'RatingsForAllDesigns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RatingsForAllDesigns, constructor.new(_428.CylindricalGearSetRating))
        return value
