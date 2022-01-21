'''_1140.py

AGMAGleasonConicalGearDesign
'''


from mastapy.gears.gear_designs.conical import (
    _1111, _1105, _1104, _1100,
    _1110, _1101
)
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import
from mastapy.gears.manufacturing.bevel.cutters import (
    _773, _774, _775, _776
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears import _280
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1083, _1087, _1092
from mastapy.gears.gear_designs.agma_gleason_conical import _1139
from mastapy.gears.materials import (
    _554, _543, _545, _547,
    _551, _557, _561, _563
)

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_AGMA_GLEASON_CONICAL_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.AGMAGleasonConical', 'AGMAGleasonConicalGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearDesign',)


class AGMAGleasonConicalGearDesign(_1101.ConicalGearDesign):
    '''AGMAGleasonConicalGearDesign

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def front_end_type(self) -> '_1111.FrontEndTypes':
        '''FrontEndTypes: 'FrontEndType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FrontEndType)
        return constructor.new(_1111.FrontEndTypes)(value) if value is not None else None

    @front_end_type.setter
    def front_end_type(self, value: '_1111.FrontEndTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FrontEndType = value

    @property
    def manufacture_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods: 'ManufactureMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ManufactureMethod, value) if self.wrapped.ManufactureMethod is not None else None

    @manufacture_method.setter
    def manufacture_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ManufactureMethod = value

    @property
    def machine_setting_calculation_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods: 'MachineSettingCalculationMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MachineSettingCalculationMethod, value) if self.wrapped.MachineSettingCalculationMethod is not None else None

    @machine_setting_calculation_method.setter
    def machine_setting_calculation_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MachineSettingCalculationMethod = value

    @property
    def material(self) -> 'str':
        '''str: 'Material' is the original name of this property.'''

        return self.wrapped.Material.SelectedItemName

    @material.setter
    def material(self, value: 'str'):
        self.wrapped.Material.SetSelectedItem(str(value) if value else '')

    @property
    def allowable_bending_stress(self) -> 'float':
        '''float: 'AllowableBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBendingStress

    @property
    def allowable_contact_stress(self) -> 'float':
        '''float: 'AllowableContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStress

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def cutter(self) -> '_1100.ConicalGearCutter':
        '''ConicalGearCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1100.ConicalGearCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to ConicalGearCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def cutter_of_type_pinion_finish_cutter(self) -> '_773.PinionFinishCutter':
        '''PinionFinishCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _773.PinionFinishCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to PinionFinishCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def cutter_of_type_pinion_rough_cutter(self) -> '_774.PinionRoughCutter':
        '''PinionRoughCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _774.PinionRoughCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to PinionRoughCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def cutter_of_type_wheel_finish_cutter(self) -> '_775.WheelFinishCutter':
        '''WheelFinishCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _775.WheelFinishCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to WheelFinishCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def cutter_of_type_wheel_rough_cutter(self) -> '_776.WheelRoughCutter':
        '''WheelRoughCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _776.WheelRoughCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to WheelRoughCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def cutter_of_type_dummy_conical_gear_cutter(self) -> '_1110.DummyConicalGearCutter':
        '''DummyConicalGearCutter: 'Cutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1110.DummyConicalGearCutter.TYPE not in self.wrapped.Cutter.__class__.__mro__:
            raise CastException('Failed to cast cutter to DummyConicalGearCutter. Expected: {}.'.format(self.wrapped.Cutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Cutter.__class__)(self.wrapped.Cutter) if self.wrapped.Cutter is not None else None

    @property
    def accuracy_grades(self) -> '_280.AccuracyGrades':
        '''AccuracyGrades: 'AccuracyGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _280.AccuracyGrades.TYPE not in self.wrapped.AccuracyGrades.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades to AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGrades.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGrades.__class__)(self.wrapped.AccuracyGrades) if self.wrapped.AccuracyGrades is not None else None

    @property
    def accuracy_grades_of_type_agma20151_accuracy_grades(self) -> '_1083.AGMA20151AccuracyGrades':
        '''AGMA20151AccuracyGrades: 'AccuracyGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1083.AGMA20151AccuracyGrades.TYPE not in self.wrapped.AccuracyGrades.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades to AGMA20151AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGrades.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGrades.__class__)(self.wrapped.AccuracyGrades) if self.wrapped.AccuracyGrades is not None else None

    @property
    def accuracy_grades_of_type_cylindrical_accuracy_grades(self) -> '_1087.CylindricalAccuracyGrades':
        '''CylindricalAccuracyGrades: 'AccuracyGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1087.CylindricalAccuracyGrades.TYPE not in self.wrapped.AccuracyGrades.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades to CylindricalAccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGrades.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGrades.__class__)(self.wrapped.AccuracyGrades) if self.wrapped.AccuracyGrades is not None else None

    @property
    def accuracy_grades_of_type_iso1328_accuracy_grades(self) -> '_1092.ISO1328AccuracyGrades':
        '''ISO1328AccuracyGrades: 'AccuracyGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1092.ISO1328AccuracyGrades.TYPE not in self.wrapped.AccuracyGrades.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades to ISO1328AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGrades.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGrades.__class__)(self.wrapped.AccuracyGrades) if self.wrapped.AccuracyGrades is not None else None

    @property
    def accuracy_grades_of_type_agma_gleason_conical_accuracy_grades(self) -> '_1139.AGMAGleasonConicalAccuracyGrades':
        '''AGMAGleasonConicalAccuracyGrades: 'AccuracyGrades' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1139.AGMAGleasonConicalAccuracyGrades.TYPE not in self.wrapped.AccuracyGrades.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades to AGMAGleasonConicalAccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGrades.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGrades.__class__)(self.wrapped.AccuracyGrades) if self.wrapped.AccuracyGrades is not None else None

    @property
    def bevel_gear_material(self) -> '_554.GearMaterial':
        '''GearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _554.GearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to GearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_agma_cylindrical_gear_material(self) -> '_543.AGMACylindricalGearMaterial':
        '''AGMACylindricalGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _543.AGMACylindricalGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to AGMACylindricalGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_bevel_gear_iso_material(self) -> '_545.BevelGearISOMaterial':
        '''BevelGearISOMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _545.BevelGearISOMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to BevelGearISOMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_bevel_gear_material(self) -> '_547.BevelGearMaterial':
        '''BevelGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _547.BevelGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to BevelGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_cylindrical_gear_material(self) -> '_551.CylindricalGearMaterial':
        '''CylindricalGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _551.CylindricalGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to CylindricalGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_iso_cylindrical_gear_material(self) -> '_557.ISOCylindricalGearMaterial':
        '''ISOCylindricalGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _557.ISOCylindricalGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to ISOCylindricalGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_klingelnberg_cyclo_palloid_conical_gear_material(self) -> '_561.KlingelnbergCycloPalloidConicalGearMaterial':
        '''KlingelnbergCycloPalloidConicalGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _561.KlingelnbergCycloPalloidConicalGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to KlingelnbergCycloPalloidConicalGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None

    @property
    def bevel_gear_material_of_type_plastic_cylindrical_gear_material(self) -> '_563.PlasticCylindricalGearMaterial':
        '''PlasticCylindricalGearMaterial: 'BevelGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _563.PlasticCylindricalGearMaterial.TYPE not in self.wrapped.BevelGearMaterial.__class__.__mro__:
            raise CastException('Failed to cast bevel_gear_material to PlasticCylindricalGearMaterial. Expected: {}.'.format(self.wrapped.BevelGearMaterial.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BevelGearMaterial.__class__)(self.wrapped.BevelGearMaterial) if self.wrapped.BevelGearMaterial is not None else None
