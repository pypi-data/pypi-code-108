'''_2499.py

HypoidGearSetSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6624
from mastapy.system_model.analyses_and_results.power_flows import _3830
from mastapy.gears.rating.hypoid import _406
from mastapy.system_model.analyses_and_results.system_deflections import _2500, _2498, _2430
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'HypoidGearSetSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetSystemDeflection',)


class HypoidGearSetSystemDeflection(_2430.AGMAGleasonConicalGearSetSystemDeflection):
    '''HypoidGearSetSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetSystemDeflection.TYPE'):
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
    def assembly_load_case(self) -> '_6624.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6624.HypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3830.HypoidGearSetPowerFlow':
        '''HypoidGearSetPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3830.HypoidGearSetPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def rating(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def hypoid_gears_system_deflection(self) -> 'List[_2500.HypoidGearSystemDeflection]':
        '''List[HypoidGearSystemDeflection]: 'HypoidGearsSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsSystemDeflection, constructor.new(_2500.HypoidGearSystemDeflection))
        return value

    @property
    def hypoid_meshes_system_deflection(self) -> 'List[_2498.HypoidGearMeshSystemDeflection]':
        '''List[HypoidGearMeshSystemDeflection]: 'HypoidMeshesSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesSystemDeflection, constructor.new(_2498.HypoidGearMeshSystemDeflection))
        return value
