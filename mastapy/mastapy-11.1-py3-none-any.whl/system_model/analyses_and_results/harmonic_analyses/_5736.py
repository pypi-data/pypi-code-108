'''_5736.py

GearMeshExcitationDetail
'''


from mastapy.system_model.analyses_and_results.system_deflections import (
    _2494, _2429, _2436, _2441,
    _2455, _2459, _2474, _2475,
    _2476, _2489, _2498, _2503,
    _2506, _2509, _2542, _2548,
    _2551, _2571, _2574
)
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6690
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5688, _5663
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_EXCITATION_DETAIL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'GearMeshExcitationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshExcitationDetail',)


class GearMeshExcitationDetail(_5663.AbstractPeriodicExcitationDetail):
    '''GearMeshExcitationDetail

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_EXCITATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshExcitationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_mesh(self) -> '_2494.GearMeshSystemDeflection':
        '''GearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2494.GearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to GearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_agma_gleason_conical_gear_mesh_system_deflection(self) -> '_2429.AGMAGleasonConicalGearMeshSystemDeflection':
        '''AGMAGleasonConicalGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2429.AGMAGleasonConicalGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to AGMAGleasonConicalGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_bevel_differential_gear_mesh_system_deflection(self) -> '_2436.BevelDifferentialGearMeshSystemDeflection':
        '''BevelDifferentialGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2436.BevelDifferentialGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to BevelDifferentialGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_bevel_gear_mesh_system_deflection(self) -> '_2441.BevelGearMeshSystemDeflection':
        '''BevelGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2441.BevelGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to BevelGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_concept_gear_mesh_system_deflection(self) -> '_2455.ConceptGearMeshSystemDeflection':
        '''ConceptGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2455.ConceptGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to ConceptGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_conical_gear_mesh_system_deflection(self) -> '_2459.ConicalGearMeshSystemDeflection':
        '''ConicalGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2459.ConicalGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to ConicalGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_cylindrical_gear_mesh_system_deflection(self) -> '_2474.CylindricalGearMeshSystemDeflection':
        '''CylindricalGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2474.CylindricalGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to CylindricalGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_cylindrical_gear_mesh_system_deflection_timestep(self) -> '_2475.CylindricalGearMeshSystemDeflectionTimestep':
        '''CylindricalGearMeshSystemDeflectionTimestep: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2475.CylindricalGearMeshSystemDeflectionTimestep.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to CylindricalGearMeshSystemDeflectionTimestep. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_cylindrical_gear_mesh_system_deflection_with_ltca_results(self) -> '_2476.CylindricalGearMeshSystemDeflectionWithLTCAResults':
        '''CylindricalGearMeshSystemDeflectionWithLTCAResults: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2476.CylindricalGearMeshSystemDeflectionWithLTCAResults.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to CylindricalGearMeshSystemDeflectionWithLTCAResults. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_face_gear_mesh_system_deflection(self) -> '_2489.FaceGearMeshSystemDeflection':
        '''FaceGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2489.FaceGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to FaceGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_hypoid_gear_mesh_system_deflection(self) -> '_2498.HypoidGearMeshSystemDeflection':
        '''HypoidGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2498.HypoidGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to HypoidGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh_system_deflection(self) -> '_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidConicalGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to KlingelnbergCycloPalloidConicalGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh_system_deflection(self) -> '_2506.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2506.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_system_deflection(self) -> '_2509.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection':
        '''KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2509.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_spiral_bevel_gear_mesh_system_deflection(self) -> '_2542.SpiralBevelGearMeshSystemDeflection':
        '''SpiralBevelGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2542.SpiralBevelGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to SpiralBevelGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_straight_bevel_diff_gear_mesh_system_deflection(self) -> '_2548.StraightBevelDiffGearMeshSystemDeflection':
        '''StraightBevelDiffGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2548.StraightBevelDiffGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to StraightBevelDiffGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_straight_bevel_gear_mesh_system_deflection(self) -> '_2551.StraightBevelGearMeshSystemDeflection':
        '''StraightBevelGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2551.StraightBevelGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to StraightBevelGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_worm_gear_mesh_system_deflection(self) -> '_2571.WormGearMeshSystemDeflection':
        '''WormGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2571.WormGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to WormGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    @property
    def gear_mesh_of_type_zerol_bevel_gear_mesh_system_deflection(self) -> '_2574.ZerolBevelGearMeshSystemDeflection':
        '''ZerolBevelGearMeshSystemDeflection: 'GearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2574.ZerolBevelGearMeshSystemDeflection.TYPE not in self.wrapped.GearMesh.__class__.__mro__:
            raise CastException('Failed to cast gear_mesh to ZerolBevelGearMeshSystemDeflection. Expected: {}.'.format(self.wrapped.GearMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearMesh.__class__)(self.wrapped.GearMesh) if self.wrapped.GearMesh is not None else None

    def get_compliance_and_force_data(self, excitation_type: '_6690.TEExcitationType') -> '_5688.ComplianceAndForceData':
        ''' 'GetComplianceAndForceData' is the original name of this method.

        Args:
            excitation_type (mastapy.system_model.analyses_and_results.static_loads.TEExcitationType)

        Returns:
            mastapy.system_model.analyses_and_results.harmonic_analyses.ComplianceAndForceData
        '''

        excitation_type = conversion.mp_to_pn_enum(excitation_type)
        method_result = self.wrapped.GetComplianceAndForceData(excitation_type)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
