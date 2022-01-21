'''_5154.py

CylindricalGearSetMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2266, _2282
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6579, _6651
from mastapy.system_model.analyses_and_results.mbd_analyses import _5153, _5152, _5166
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'CylindricalGearSetMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetMultibodyDynamicsAnalysis',)


class CylindricalGearSetMultibodyDynamicsAnalysis(_5166.GearSetMultibodyDynamicsAnalysis):
    '''CylindricalGearSetMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetMultibodyDynamicsAnalysis.TYPE'):
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
    def gears(self) -> 'List[_5153.CylindricalGearMultibodyDynamicsAnalysis]':
        '''List[CylindricalGearMultibodyDynamicsAnalysis]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_5153.CylindricalGearMultibodyDynamicsAnalysis))
        return value

    @property
    def cylindrical_gears_multibody_dynamics_analysis(self) -> 'List[_5153.CylindricalGearMultibodyDynamicsAnalysis]':
        '''List[CylindricalGearMultibodyDynamicsAnalysis]: 'CylindricalGearsMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearsMultibodyDynamicsAnalysis, constructor.new(_5153.CylindricalGearMultibodyDynamicsAnalysis))
        return value

    @property
    def cylindrical_meshes_multibody_dynamics_analysis(self) -> 'List[_5152.CylindricalGearMeshMultibodyDynamicsAnalysis]':
        '''List[CylindricalGearMeshMultibodyDynamicsAnalysis]: 'CylindricalMeshesMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshesMultibodyDynamicsAnalysis, constructor.new(_5152.CylindricalGearMeshMultibodyDynamicsAnalysis))
        return value
