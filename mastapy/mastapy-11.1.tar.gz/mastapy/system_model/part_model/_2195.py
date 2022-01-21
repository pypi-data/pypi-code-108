'''_2195.py

FlexiblePinAssembly
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import
from mastapy.system_model.part_model.gears import _2265, _2267
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model import _2217

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_FLEXIBLE_PIN_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'FlexiblePinAssembly')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAssembly',)


class FlexiblePinAssembly(_2217.SpecialisedAssembly):
    '''FlexiblePinAssembly

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ASSEMBLY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAssembly.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_position_tolerance(self) -> 'float':
        '''float: 'PinPositionTolerance' is the original name of this property.'''

        return self.wrapped.PinPositionTolerance

    @pin_position_tolerance.setter
    def pin_position_tolerance(self, value: 'float'):
        self.wrapped.PinPositionTolerance = float(value) if value else 0.0

    @property
    def pitch_iso_quality_grade(self) -> 'list_with_selected_item.ListWithSelectedItem_int':
        '''list_with_selected_item.ListWithSelectedItem_int: 'PitchISOQualityGrade' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_int)(self.wrapped.PitchISOQualityGrade) if self.wrapped.PitchISOQualityGrade is not None else None

    @pitch_iso_quality_grade.setter
    def pitch_iso_quality_grade(self, value: 'list_with_selected_item.ListWithSelectedItem_int.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_int.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_int.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0)
        self.wrapped.PitchISOQualityGrade = value

    @property
    def unsupported_pin_length(self) -> 'float':
        '''float: 'UnsupportedPinLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UnsupportedPinLength

    @property
    def total_pin_length(self) -> 'float':
        '''float: 'TotalPinLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalPinLength

    @property
    def pin_diameter(self) -> 'float':
        '''float: 'PinDiameter' is the original name of this property.'''

        return self.wrapped.PinDiameter

    @pin_diameter.setter
    def pin_diameter(self, value: 'float'):
        self.wrapped.PinDiameter = float(value) if value else 0.0

    @property
    def spindle_outer_diameter(self) -> 'float':
        '''float: 'SpindleOuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpindleOuterDiameter

    @property
    def planet_gear_bore_diameter(self) -> 'float':
        '''float: 'PlanetGearBoreDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PlanetGearBoreDiameter

    @property
    def maximum_pin_diameter_from_planet_bore(self) -> 'float':
        '''float: 'MaximumPinDiameterFromPlanetBore' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPinDiameterFromPlanetBore

    @property
    def length_to_diameter_ratio(self) -> 'float':
        '''float: 'LengthToDiameterRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthToDiameterRatio

    @property
    def material(self) -> 'str':
        '''str: 'Material' is the original name of this property.'''

        return self.wrapped.Material.SelectedItemName

    @material.setter
    def material(self, value: 'str'):
        self.wrapped.Material.SetSelectedItem(str(value) if value else '')

    @property
    def minimum_fatigue_safety_factor(self) -> 'float':
        '''float: 'MinimumFatigueSafetyFactor' is the original name of this property.'''

        return self.wrapped.MinimumFatigueSafetyFactor

    @minimum_fatigue_safety_factor.setter
    def minimum_fatigue_safety_factor(self, value: 'float'):
        self.wrapped.MinimumFatigueSafetyFactor = float(value) if value else 0.0

    @property
    def planet_gear(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'PlanetGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.PlanetGear.__class__.__mro__:
            raise CastException('Failed to cast planet_gear to CylindricalGear. Expected: {}.'.format(self.wrapped.PlanetGear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PlanetGear.__class__)(self.wrapped.PlanetGear) if self.wrapped.PlanetGear is not None else None
