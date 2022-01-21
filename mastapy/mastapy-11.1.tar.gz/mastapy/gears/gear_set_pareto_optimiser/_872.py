'''_872.py

GearSetParetoOptimiser
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs import _907
from mastapy.gears.gear_designs.zerol_bevel import _911
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.worm import _916
from mastapy.gears.gear_designs.straight_bevel_diff import _920
from mastapy.gears.gear_designs.straight_bevel import _924
from mastapy.gears.gear_designs.spiral_bevel import _928
from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _932
from mastapy.gears.gear_designs.klingelnberg_hypoid import _936
from mastapy.gears.gear_designs.klingelnberg_conical import _940
from mastapy.gears.gear_designs.hypoid import _944
from mastapy.gears.gear_designs.face import _952
from mastapy.gears.gear_designs.cylindrical import _984, _995
from mastapy.gears.gear_designs.conical import _1103
from mastapy.gears.gear_designs.concept import _1125
from mastapy.gears.gear_designs.bevel import _1129
from mastapy.gears.gear_designs.agma_gleason_conical import _1142
from mastapy.gears.gear_set_pareto_optimiser import _866, _871
from mastapy.gears.rating import _321
from mastapy._internal.python_net import python_net_import

_GEAR_SET_PARETO_OPTIMISER = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'GearSetParetoOptimiser')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetParetoOptimiser',)


class GearSetParetoOptimiser(_866.DesignSpaceSearchBase['_321.AbstractGearSetRating', '_871.GearSetOptimiserCandidate']):
    '''GearSetParetoOptimiser

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_PARETO_OPTIMISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetParetoOptimiser.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def remove_candidates_which_cannot_be_manufactured_with_cutters_from_database(self) -> 'bool':
        '''bool: 'RemoveCandidatesWhichCannotBeManufacturedWithCuttersFromDatabase' is the original name of this property.'''

        return self.wrapped.RemoveCandidatesWhichCannotBeManufacturedWithCuttersFromDatabase

    @remove_candidates_which_cannot_be_manufactured_with_cutters_from_database.setter
    def remove_candidates_which_cannot_be_manufactured_with_cutters_from_database(self, value: 'bool'):
        self.wrapped.RemoveCandidatesWhichCannotBeManufacturedWithCuttersFromDatabase = bool(value) if value else False

    @property
    def number_of_designs_with_gears_which_cannot_be_manufactured_from_cutters(self) -> 'int':
        '''int: 'NumberOfDesignsWithGearsWhichCannotBeManufacturedFromCutters' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfDesignsWithGearsWhichCannotBeManufacturedFromCutters

    @property
    def remove_candidates_with_warnings(self) -> 'bool':
        '''bool: 'RemoveCandidatesWithWarnings' is the original name of this property.'''

        return self.wrapped.RemoveCandidatesWithWarnings

    @remove_candidates_with_warnings.setter
    def remove_candidates_with_warnings(self, value: 'bool'):
        self.wrapped.RemoveCandidatesWithWarnings = bool(value) if value else False

    @property
    def selected_candidate_geometry(self) -> '_907.GearSetDesign':
        '''GearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _907.GearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to GearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_zerol_bevel_gear_set_design(self) -> '_911.ZerolBevelGearSetDesign':
        '''ZerolBevelGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _911.ZerolBevelGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to ZerolBevelGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_worm_gear_set_design(self) -> '_916.WormGearSetDesign':
        '''WormGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _916.WormGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to WormGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_straight_bevel_diff_gear_set_design(self) -> '_920.StraightBevelDiffGearSetDesign':
        '''StraightBevelDiffGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _920.StraightBevelDiffGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to StraightBevelDiffGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_straight_bevel_gear_set_design(self) -> '_924.StraightBevelGearSetDesign':
        '''StraightBevelGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _924.StraightBevelGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to StraightBevelGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_spiral_bevel_gear_set_design(self) -> '_928.SpiralBevelGearSetDesign':
        '''SpiralBevelGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _928.SpiralBevelGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to SpiralBevelGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_design(self) -> '_932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to KlingelnbergCycloPalloidSpiralBevelGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_design(self) -> '_936.KlingelnbergCycloPalloidHypoidGearSetDesign':
        '''KlingelnbergCycloPalloidHypoidGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _936.KlingelnbergCycloPalloidHypoidGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to KlingelnbergCycloPalloidHypoidGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_klingelnberg_conical_gear_set_design(self) -> '_940.KlingelnbergConicalGearSetDesign':
        '''KlingelnbergConicalGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _940.KlingelnbergConicalGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to KlingelnbergConicalGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_hypoid_gear_set_design(self) -> '_944.HypoidGearSetDesign':
        '''HypoidGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _944.HypoidGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to HypoidGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_face_gear_set_design(self) -> '_952.FaceGearSetDesign':
        '''FaceGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _952.FaceGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to FaceGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_cylindrical_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_cylindrical_planetary_gear_set_design(self) -> '_995.CylindricalPlanetaryGearSetDesign':
        '''CylindricalPlanetaryGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _995.CylindricalPlanetaryGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to CylindricalPlanetaryGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_conical_gear_set_design(self) -> '_1103.ConicalGearSetDesign':
        '''ConicalGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1103.ConicalGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to ConicalGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_concept_gear_set_design(self) -> '_1125.ConceptGearSetDesign':
        '''ConceptGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1125.ConceptGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to ConceptGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_bevel_gear_set_design(self) -> '_1129.BevelGearSetDesign':
        '''BevelGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1129.BevelGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to BevelGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def selected_candidate_geometry_of_type_agma_gleason_conical_gear_set_design(self) -> '_1142.AGMAGleasonConicalGearSetDesign':
        '''AGMAGleasonConicalGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1142.AGMAGleasonConicalGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to AGMAGleasonConicalGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def candidate_gear_sets(self) -> 'List[_907.GearSetDesign]':
        '''List[GearSetDesign]: 'CandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CandidateGearSets, constructor.new(_907.GearSetDesign))
        return value

    @property
    def all_candidate_gear_sets(self) -> 'List[_907.GearSetDesign]':
        '''List[GearSetDesign]: 'AllCandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllCandidateGearSets, constructor.new(_907.GearSetDesign))
        return value

    def reset_charts(self):
        ''' 'ResetCharts' is the original name of this method.'''

        self.wrapped.ResetCharts()

    def add_chart(self):
        ''' 'AddChart' is the original name of this method.'''

        self.wrapped.AddChart()
