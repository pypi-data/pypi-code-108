'''_2272.py

GearSet
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item, overridable
from mastapy.gears.gear_designs import _907
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
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
from mastapy.system_model.part_model import _2217
from mastapy._internal.python_net import python_net_import

_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'GearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSet',)


class GearSet(_2217.SpecialisedAssembly):
    '''GearSet

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def active_design(self) -> 'list_with_selected_item.ListWithSelectedItem_GearSetDesign':
        '''list_with_selected_item.ListWithSelectedItem_GearSetDesign: 'ActiveDesign' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_GearSetDesign)(self.wrapped.ActiveDesign) if self.wrapped.ActiveDesign is not None else None

    @active_design.setter
    def active_design(self, value: 'list_with_selected_item.ListWithSelectedItem_GearSetDesign.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_GearSetDesign.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_GearSetDesign.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ActiveDesign = value

    @property
    def required_safety_factor_for_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RequiredSafetyFactorForContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RequiredSafetyFactorForContact) if self.wrapped.RequiredSafetyFactorForContact is not None else None

    @required_safety_factor_for_contact.setter
    def required_safety_factor_for_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RequiredSafetyFactorForContact = value

    @property
    def required_safety_factor_for_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RequiredSafetyFactorForBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RequiredSafetyFactorForBending) if self.wrapped.RequiredSafetyFactorForBending is not None else None

    @required_safety_factor_for_bending.setter
    def required_safety_factor_for_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RequiredSafetyFactorForBending = value

    @property
    def required_safety_factor_for_static_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RequiredSafetyFactorForStaticContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RequiredSafetyFactorForStaticContact) if self.wrapped.RequiredSafetyFactorForStaticContact is not None else None

    @required_safety_factor_for_static_contact.setter
    def required_safety_factor_for_static_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RequiredSafetyFactorForStaticContact = value

    @property
    def required_safety_factor_for_static_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RequiredSafetyFactorForStaticBending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RequiredSafetyFactorForStaticBending) if self.wrapped.RequiredSafetyFactorForStaticBending is not None else None

    @required_safety_factor_for_static_bending.setter
    def required_safety_factor_for_static_bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RequiredSafetyFactorForStaticBending = value

    @property
    def minimum_number_of_teeth_in_mesh(self) -> 'int':
        '''int: 'MinimumNumberOfTeethInMesh' is the original name of this property.'''

        return self.wrapped.MinimumNumberOfTeethInMesh

    @minimum_number_of_teeth_in_mesh.setter
    def minimum_number_of_teeth_in_mesh(self, value: 'int'):
        self.wrapped.MinimumNumberOfTeethInMesh = int(value) if value else 0

    @property
    def maximum_number_of_teeth_in_mesh(self) -> 'int':
        '''int: 'MaximumNumberOfTeethInMesh' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfTeethInMesh

    @maximum_number_of_teeth_in_mesh.setter
    def maximum_number_of_teeth_in_mesh(self, value: 'int'):
        self.wrapped.MaximumNumberOfTeethInMesh = int(value) if value else 0

    @property
    def maximum_mesh_ratio(self) -> 'float':
        '''float: 'MaximumMeshRatio' is the original name of this property.'''

        return self.wrapped.MaximumMeshRatio

    @maximum_mesh_ratio.setter
    def maximum_mesh_ratio(self, value: 'float'):
        self.wrapped.MaximumMeshRatio = float(value) if value else 0.0

    @property
    def active_gear_set_design(self) -> '_907.GearSetDesign':
        '''GearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _907.GearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to GearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_zerol_bevel_gear_set_design(self) -> '_911.ZerolBevelGearSetDesign':
        '''ZerolBevelGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _911.ZerolBevelGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to ZerolBevelGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_worm_gear_set_design(self) -> '_916.WormGearSetDesign':
        '''WormGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _916.WormGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to WormGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_straight_bevel_diff_gear_set_design(self) -> '_920.StraightBevelDiffGearSetDesign':
        '''StraightBevelDiffGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _920.StraightBevelDiffGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to StraightBevelDiffGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_straight_bevel_gear_set_design(self) -> '_924.StraightBevelGearSetDesign':
        '''StraightBevelGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _924.StraightBevelGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to StraightBevelGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_spiral_bevel_gear_set_design(self) -> '_928.SpiralBevelGearSetDesign':
        '''SpiralBevelGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _928.SpiralBevelGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to SpiralBevelGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_design(self) -> '_932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to KlingelnbergCycloPalloidSpiralBevelGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_design(self) -> '_936.KlingelnbergCycloPalloidHypoidGearSetDesign':
        '''KlingelnbergCycloPalloidHypoidGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _936.KlingelnbergCycloPalloidHypoidGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to KlingelnbergCycloPalloidHypoidGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_klingelnberg_conical_gear_set_design(self) -> '_940.KlingelnbergConicalGearSetDesign':
        '''KlingelnbergConicalGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _940.KlingelnbergConicalGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to KlingelnbergConicalGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_hypoid_gear_set_design(self) -> '_944.HypoidGearSetDesign':
        '''HypoidGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _944.HypoidGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to HypoidGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_face_gear_set_design(self) -> '_952.FaceGearSetDesign':
        '''FaceGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _952.FaceGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to FaceGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_cylindrical_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_cylindrical_planetary_gear_set_design(self) -> '_995.CylindricalPlanetaryGearSetDesign':
        '''CylindricalPlanetaryGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _995.CylindricalPlanetaryGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to CylindricalPlanetaryGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_conical_gear_set_design(self) -> '_1103.ConicalGearSetDesign':
        '''ConicalGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1103.ConicalGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to ConicalGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_concept_gear_set_design(self) -> '_1125.ConceptGearSetDesign':
        '''ConceptGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1125.ConceptGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to ConceptGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_bevel_gear_set_design(self) -> '_1129.BevelGearSetDesign':
        '''BevelGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1129.BevelGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to BevelGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def active_gear_set_design_of_type_agma_gleason_conical_gear_set_design(self) -> '_1142.AGMAGleasonConicalGearSetDesign':
        '''AGMAGleasonConicalGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1142.AGMAGleasonConicalGearSetDesign.TYPE not in self.wrapped.ActiveGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_set_design to AGMAGleasonConicalGearSetDesign. Expected: {}.'.format(self.wrapped.ActiveGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearSetDesign.__class__)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def gear_set_designs(self) -> 'List[_907.GearSetDesign]':
        '''List[GearSetDesign]: 'GearSetDesigns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSetDesigns, constructor.new(_907.GearSetDesign))
        return value

    def set_active_gear_set_design(self, gear_set_design: '_907.GearSetDesign'):
        ''' 'SetActiveGearSetDesign' is the original name of this method.

        Args:
            gear_set_design (mastapy.gears.gear_designs.GearSetDesign)
        '''

        self.wrapped.SetActiveGearSetDesign(gear_set_design.wrapped if gear_set_design else None)

    def add_gear_set_design(self, design: '_907.GearSetDesign'):
        ''' 'AddGearSetDesign' is the original name of this method.

        Args:
            design (mastapy.gears.gear_designs.GearSetDesign)
        '''

        self.wrapped.AddGearSetDesign(design.wrapped if design else None)
