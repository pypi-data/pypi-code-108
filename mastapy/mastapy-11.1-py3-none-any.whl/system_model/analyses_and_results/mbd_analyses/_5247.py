'''_5247.py

ZerolBevelGearSetMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6706
from mastapy.system_model.analyses_and_results.mbd_analyses import _5246, _5245, _5122
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'ZerolBevelGearSetMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetMultibodyDynamicsAnalysis',)


class ZerolBevelGearSetMultibodyDynamicsAnalysis(_5122.BevelGearSetMultibodyDynamicsAnalysis):
    '''ZerolBevelGearSetMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6706.ZerolBevelGearSetLoadCase':
        '''ZerolBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6706.ZerolBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def gears(self) -> 'List[_5246.ZerolBevelGearMultibodyDynamicsAnalysis]':
        '''List[ZerolBevelGearMultibodyDynamicsAnalysis]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_5246.ZerolBevelGearMultibodyDynamicsAnalysis))
        return value

    @property
    def zerol_bevel_gears_multibody_dynamics_analysis(self) -> 'List[_5246.ZerolBevelGearMultibodyDynamicsAnalysis]':
        '''List[ZerolBevelGearMultibodyDynamicsAnalysis]: 'ZerolBevelGearsMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearsMultibodyDynamicsAnalysis, constructor.new(_5246.ZerolBevelGearMultibodyDynamicsAnalysis))
        return value

    @property
    def zerol_bevel_meshes_multibody_dynamics_analysis(self) -> 'List[_5245.ZerolBevelGearMeshMultibodyDynamicsAnalysis]':
        '''List[ZerolBevelGearMeshMultibodyDynamicsAnalysis]: 'ZerolBevelMeshesMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshesMultibodyDynamicsAnalysis, constructor.new(_5245.ZerolBevelGearMeshMultibodyDynamicsAnalysis))
        return value
