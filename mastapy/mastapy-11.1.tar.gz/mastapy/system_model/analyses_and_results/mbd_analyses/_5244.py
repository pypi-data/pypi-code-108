'''_5244.py

WormGearSetMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.mbd_analyses import _5243, _5242, _5166
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'WormGearSetMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetMultibodyDynamicsAnalysis',)


class WormGearSetMultibodyDynamicsAnalysis(_5166.GearSetMultibodyDynamicsAnalysis):
    '''WormGearSetMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetMultibodyDynamicsAnalysis.TYPE'):
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
    def gears(self) -> 'List[_5243.WormGearMultibodyDynamicsAnalysis]':
        '''List[WormGearMultibodyDynamicsAnalysis]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_5243.WormGearMultibodyDynamicsAnalysis))
        return value

    @property
    def worm_gears_multibody_dynamics_analysis(self) -> 'List[_5243.WormGearMultibodyDynamicsAnalysis]':
        '''List[WormGearMultibodyDynamicsAnalysis]: 'WormGearsMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsMultibodyDynamicsAnalysis, constructor.new(_5243.WormGearMultibodyDynamicsAnalysis))
        return value

    @property
    def worm_meshes_multibody_dynamics_analysis(self) -> 'List[_5242.WormGearMeshMultibodyDynamicsAnalysis]':
        '''List[WormGearMeshMultibodyDynamicsAnalysis]: 'WormMeshesMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesMultibodyDynamicsAnalysis, constructor.new(_5242.WormGearMeshMultibodyDynamicsAnalysis))
        return value
