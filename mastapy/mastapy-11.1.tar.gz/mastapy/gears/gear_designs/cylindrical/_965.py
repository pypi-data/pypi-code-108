'''_965.py

CylindricalGearBasicRack
'''


from mastapy.gears.gear_designs.cylindrical import (
    _957, _1035, _979, _963
)
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_BASIC_RACK = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearBasicRack')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearBasicRack',)


class CylindricalGearBasicRack(_963.CylindricalGearAbstractRack):
    '''CylindricalGearBasicRack

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_BASIC_RACK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearBasicRack.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def basic_rack_profile(self) -> '_957.BasicRackProfiles':
        '''BasicRackProfiles: 'BasicRackProfile' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.BasicRackProfile)
        return constructor.new(_957.BasicRackProfiles)(value) if value is not None else None

    @basic_rack_profile.setter
    def basic_rack_profile(self, value: '_957.BasicRackProfiles'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.BasicRackProfile = value

    @property
    def tip_alteration_proportional_method_mesh(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'TipAlterationProportionalMethodMesh' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.TipAlterationProportionalMethodMesh) if self.wrapped.TipAlterationProportionalMethodMesh is not None else None

    @tip_alteration_proportional_method_mesh.setter
    def tip_alteration_proportional_method_mesh(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.TipAlterationProportionalMethodMesh = value

    @property
    def proportional_method_for_tip_clearance(self) -> '_1035.TipAlterationCoefficientMethod':
        '''TipAlterationCoefficientMethod: 'ProportionalMethodForTipClearance' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ProportionalMethodForTipClearance)
        return constructor.new(_1035.TipAlterationCoefficientMethod)(value) if value is not None else None

    @proportional_method_for_tip_clearance.setter
    def proportional_method_for_tip_clearance(self, value: '_1035.TipAlterationCoefficientMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ProportionalMethodForTipClearance = value

    @property
    def basic_rack_clearance_factor(self) -> 'float':
        '''float: 'BasicRackClearanceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackClearanceFactor

    @property
    def pinion_type_cutter_for_rating(self) -> '_979.CylindricalGearPinionTypeCutter':
        '''CylindricalGearPinionTypeCutter: 'PinionTypeCutterForRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_979.CylindricalGearPinionTypeCutter)(self.wrapped.PinionTypeCutterForRating) if self.wrapped.PinionTypeCutterForRating is not None else None
