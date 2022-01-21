'''_572.py

CylindricalGearManufacturingConfig
'''


from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.gears.manufacturing.cylindrical import _584, _583, _571
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy._internal.python_net import python_net_import
from mastapy.gears.manufacturing.cylindrical.cutters import (
    _691, _685, _686, _687,
    _688, _690, _692, _693,
    _696
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical import _1000, _969, _996
from mastapy.gears.manufacturing.cylindrical.cutter_simulation import (
    _671, _668, _676, _665,
    _674
)
from mastapy.gears.manufacturing.cylindrical.process_simulation import _599, _600, _601
from mastapy.gears.analysis import _1165

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_MANUFACTURING_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalGearManufacturingConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearManufacturingConfig',)


class CylindricalGearManufacturingConfig(_1165.GearImplementationDetail):
    '''CylindricalGearManufacturingConfig

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MANUFACTURING_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearManufacturingConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def roughing_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods: 'RoughingMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.RoughingMethod, value) if self.wrapped.RoughingMethod is not None else None

    @roughing_method.setter
    def roughing_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.RoughingMethod = value

    @property
    def finishing_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods: 'FinishingMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.FinishingMethod, value) if self.wrapped.FinishingMethod is not None else None

    @finishing_method.setter
    def finishing_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.FinishingMethod = value

    @property
    def rough_cutter_database_selector(self) -> 'str':
        '''str: 'RoughCutterDatabaseSelector' is the original name of this property.'''

        return self.wrapped.RoughCutterDatabaseSelector.SelectedItemName

    @rough_cutter_database_selector.setter
    def rough_cutter_database_selector(self, value: 'str'):
        self.wrapped.RoughCutterDatabaseSelector.SetSelectedItem(str(value) if value else '')

    @property
    def finish_cutter_database_selector(self) -> 'str':
        '''str: 'FinishCutterDatabaseSelector' is the original name of this property.'''

        return self.wrapped.FinishCutterDatabaseSelector.SelectedItemName

    @finish_cutter_database_selector.setter
    def finish_cutter_database_selector(self, value: 'str'):
        self.wrapped.FinishCutterDatabaseSelector.SetSelectedItem(str(value) if value else '')

    @property
    def minimum_finish_cutter_gear_root_clearance_factor(self) -> 'float':
        '''float: 'MinimumFinishCutterGearRootClearanceFactor' is the original name of this property.'''

        return self.wrapped.MinimumFinishCutterGearRootClearanceFactor

    @minimum_finish_cutter_gear_root_clearance_factor.setter
    def minimum_finish_cutter_gear_root_clearance_factor(self, value: 'float'):
        self.wrapped.MinimumFinishCutterGearRootClearanceFactor = float(value) if value else 0.0

    @property
    def number_of_points_for_reporting_main_profile_finish_stock(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'NumberOfPointsForReportingMainProfileFinishStock' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.NumberOfPointsForReportingMainProfileFinishStock) if self.wrapped.NumberOfPointsForReportingMainProfileFinishStock is not None else None

    @number_of_points_for_reporting_main_profile_finish_stock.setter
    def number_of_points_for_reporting_main_profile_finish_stock(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.NumberOfPointsForReportingMainProfileFinishStock = value

    @property
    def rough_cutter(self) -> '_691.CylindricalGearRealCutterDesign':
        '''CylindricalGearRealCutterDesign: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _691.CylindricalGearRealCutterDesign.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearRealCutterDesign. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_form_grinding_wheel(self) -> '_685.CylindricalGearFormGrindingWheel':
        '''CylindricalGearFormGrindingWheel: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _685.CylindricalGearFormGrindingWheel.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearFormGrindingWheel. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_grinding_worm(self) -> '_686.CylindricalGearGrindingWorm':
        '''CylindricalGearGrindingWorm: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _686.CylindricalGearGrindingWorm.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearGrindingWorm. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_hob_design(self) -> '_687.CylindricalGearHobDesign':
        '''CylindricalGearHobDesign: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _687.CylindricalGearHobDesign.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearHobDesign. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_plunge_shaver(self) -> '_688.CylindricalGearPlungeShaver':
        '''CylindricalGearPlungeShaver: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _688.CylindricalGearPlungeShaver.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearPlungeShaver. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_rack_design(self) -> '_690.CylindricalGearRackDesign':
        '''CylindricalGearRackDesign: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _690.CylindricalGearRackDesign.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearRackDesign. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_shaper(self) -> '_692.CylindricalGearShaper':
        '''CylindricalGearShaper: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _692.CylindricalGearShaper.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearShaper. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_cylindrical_gear_shaver(self) -> '_693.CylindricalGearShaver':
        '''CylindricalGearShaver: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _693.CylindricalGearShaver.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to CylindricalGearShaver. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def rough_cutter_of_type_involute_cutter_design(self) -> '_696.InvoluteCutterDesign':
        '''InvoluteCutterDesign: 'RoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _696.InvoluteCutterDesign.TYPE not in self.wrapped.RoughCutter.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter to InvoluteCutterDesign. Expected: {}.'.format(self.wrapped.RoughCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutter.__class__)(self.wrapped.RoughCutter) if self.wrapped.RoughCutter is not None else None

    @property
    def finish_cutter(self) -> '_691.CylindricalGearRealCutterDesign':
        '''CylindricalGearRealCutterDesign: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _691.CylindricalGearRealCutterDesign.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearRealCutterDesign. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_form_grinding_wheel(self) -> '_685.CylindricalGearFormGrindingWheel':
        '''CylindricalGearFormGrindingWheel: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _685.CylindricalGearFormGrindingWheel.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearFormGrindingWheel. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_grinding_worm(self) -> '_686.CylindricalGearGrindingWorm':
        '''CylindricalGearGrindingWorm: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _686.CylindricalGearGrindingWorm.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearGrindingWorm. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_hob_design(self) -> '_687.CylindricalGearHobDesign':
        '''CylindricalGearHobDesign: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _687.CylindricalGearHobDesign.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearHobDesign. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_plunge_shaver(self) -> '_688.CylindricalGearPlungeShaver':
        '''CylindricalGearPlungeShaver: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _688.CylindricalGearPlungeShaver.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearPlungeShaver. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_rack_design(self) -> '_690.CylindricalGearRackDesign':
        '''CylindricalGearRackDesign: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _690.CylindricalGearRackDesign.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearRackDesign. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_shaper(self) -> '_692.CylindricalGearShaper':
        '''CylindricalGearShaper: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _692.CylindricalGearShaper.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearShaper. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_cylindrical_gear_shaver(self) -> '_693.CylindricalGearShaver':
        '''CylindricalGearShaver: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _693.CylindricalGearShaver.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to CylindricalGearShaver. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_cutter_of_type_involute_cutter_design(self) -> '_696.InvoluteCutterDesign':
        '''InvoluteCutterDesign: 'FinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _696.InvoluteCutterDesign.TYPE not in self.wrapped.FinishCutter.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter to InvoluteCutterDesign. Expected: {}.'.format(self.wrapped.FinishCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutter.__class__)(self.wrapped.FinishCutter) if self.wrapped.FinishCutter is not None else None

    @property
    def finish_stock_specification(self) -> '_1000.FinishStockSpecification':
        '''FinishStockSpecification: 'FinishStockSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1000.FinishStockSpecification)(self.wrapped.FinishStockSpecification) if self.wrapped.FinishStockSpecification is not None else None

    @property
    def rough_cutter_simulation(self) -> '_671.GearCutterSimulation':
        '''GearCutterSimulation: 'RoughCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _671.GearCutterSimulation.TYPE not in self.wrapped.RoughCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter_simulation to GearCutterSimulation. Expected: {}.'.format(self.wrapped.RoughCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutterSimulation.__class__)(self.wrapped.RoughCutterSimulation) if self.wrapped.RoughCutterSimulation is not None else None

    @property
    def rough_cutter_simulation_of_type_finish_cutter_simulation(self) -> '_668.FinishCutterSimulation':
        '''FinishCutterSimulation: 'RoughCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _668.FinishCutterSimulation.TYPE not in self.wrapped.RoughCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter_simulation to FinishCutterSimulation. Expected: {}.'.format(self.wrapped.RoughCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutterSimulation.__class__)(self.wrapped.RoughCutterSimulation) if self.wrapped.RoughCutterSimulation is not None else None

    @property
    def rough_cutter_simulation_of_type_rough_cutter_simulation(self) -> '_676.RoughCutterSimulation':
        '''RoughCutterSimulation: 'RoughCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _676.RoughCutterSimulation.TYPE not in self.wrapped.RoughCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_cutter_simulation to RoughCutterSimulation. Expected: {}.'.format(self.wrapped.RoughCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughCutterSimulation.__class__)(self.wrapped.RoughCutterSimulation) if self.wrapped.RoughCutterSimulation is not None else None

    @property
    def rough_process_simulation(self) -> '_599.CutterProcessSimulation':
        '''CutterProcessSimulation: 'RoughProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _599.CutterProcessSimulation.TYPE not in self.wrapped.RoughProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_process_simulation to CutterProcessSimulation. Expected: {}.'.format(self.wrapped.RoughProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughProcessSimulation.__class__)(self.wrapped.RoughProcessSimulation) if self.wrapped.RoughProcessSimulation is not None else None

    @property
    def rough_process_simulation_of_type_form_wheel_grinding_process_simulation(self) -> '_600.FormWheelGrindingProcessSimulation':
        '''FormWheelGrindingProcessSimulation: 'RoughProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _600.FormWheelGrindingProcessSimulation.TYPE not in self.wrapped.RoughProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_process_simulation to FormWheelGrindingProcessSimulation. Expected: {}.'.format(self.wrapped.RoughProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughProcessSimulation.__class__)(self.wrapped.RoughProcessSimulation) if self.wrapped.RoughProcessSimulation is not None else None

    @property
    def rough_process_simulation_of_type_shaping_process_simulation(self) -> '_601.ShapingProcessSimulation':
        '''ShapingProcessSimulation: 'RoughProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _601.ShapingProcessSimulation.TYPE not in self.wrapped.RoughProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast rough_process_simulation to ShapingProcessSimulation. Expected: {}.'.format(self.wrapped.RoughProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughProcessSimulation.__class__)(self.wrapped.RoughProcessSimulation) if self.wrapped.RoughProcessSimulation is not None else None

    @property
    def finish_cutter_simulation(self) -> '_671.GearCutterSimulation':
        '''GearCutterSimulation: 'FinishCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _671.GearCutterSimulation.TYPE not in self.wrapped.FinishCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter_simulation to GearCutterSimulation. Expected: {}.'.format(self.wrapped.FinishCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutterSimulation.__class__)(self.wrapped.FinishCutterSimulation) if self.wrapped.FinishCutterSimulation is not None else None

    @property
    def finish_cutter_simulation_of_type_finish_cutter_simulation(self) -> '_668.FinishCutterSimulation':
        '''FinishCutterSimulation: 'FinishCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _668.FinishCutterSimulation.TYPE not in self.wrapped.FinishCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter_simulation to FinishCutterSimulation. Expected: {}.'.format(self.wrapped.FinishCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutterSimulation.__class__)(self.wrapped.FinishCutterSimulation) if self.wrapped.FinishCutterSimulation is not None else None

    @property
    def finish_cutter_simulation_of_type_rough_cutter_simulation(self) -> '_676.RoughCutterSimulation':
        '''RoughCutterSimulation: 'FinishCutterSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _676.RoughCutterSimulation.TYPE not in self.wrapped.FinishCutterSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_cutter_simulation to RoughCutterSimulation. Expected: {}.'.format(self.wrapped.FinishCutterSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishCutterSimulation.__class__)(self.wrapped.FinishCutterSimulation) if self.wrapped.FinishCutterSimulation is not None else None

    @property
    def finish_process_simulation(self) -> '_599.CutterProcessSimulation':
        '''CutterProcessSimulation: 'FinishProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _599.CutterProcessSimulation.TYPE not in self.wrapped.FinishProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_process_simulation to CutterProcessSimulation. Expected: {}.'.format(self.wrapped.FinishProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishProcessSimulation.__class__)(self.wrapped.FinishProcessSimulation) if self.wrapped.FinishProcessSimulation is not None else None

    @property
    def finish_process_simulation_of_type_form_wheel_grinding_process_simulation(self) -> '_600.FormWheelGrindingProcessSimulation':
        '''FormWheelGrindingProcessSimulation: 'FinishProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _600.FormWheelGrindingProcessSimulation.TYPE not in self.wrapped.FinishProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_process_simulation to FormWheelGrindingProcessSimulation. Expected: {}.'.format(self.wrapped.FinishProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishProcessSimulation.__class__)(self.wrapped.FinishProcessSimulation) if self.wrapped.FinishProcessSimulation is not None else None

    @property
    def finish_process_simulation_of_type_shaping_process_simulation(self) -> '_601.ShapingProcessSimulation':
        '''ShapingProcessSimulation: 'FinishProcessSimulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _601.ShapingProcessSimulation.TYPE not in self.wrapped.FinishProcessSimulation.__class__.__mro__:
            raise CastException('Failed to cast finish_process_simulation to ShapingProcessSimulation. Expected: {}.'.format(self.wrapped.FinishProcessSimulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FinishProcessSimulation.__class__)(self.wrapped.FinishProcessSimulation) if self.wrapped.FinishProcessSimulation is not None else None

    @property
    def design(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'Design' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.Design.__class__.__mro__:
            raise CastException('Failed to cast design to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.Design.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Design.__class__)(self.wrapped.Design) if self.wrapped.Design is not None else None

    @property
    def rough_gear_specification(self) -> '_665.CylindricalGearSpecification':
        '''CylindricalGearSpecification: 'RoughGearSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_665.CylindricalGearSpecification)(self.wrapped.RoughGearSpecification) if self.wrapped.RoughGearSpecification is not None else None

    @property
    def finished_gear_specification(self) -> '_665.CylindricalGearSpecification':
        '''CylindricalGearSpecification: 'FinishedGearSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_665.CylindricalGearSpecification)(self.wrapped.FinishedGearSpecification) if self.wrapped.FinishedGearSpecification is not None else None

    @property
    def gear_blank(self) -> '_571.CylindricalGearBlank':
        '''CylindricalGearBlank: 'GearBlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_571.CylindricalGearBlank)(self.wrapped.GearBlank) if self.wrapped.GearBlank is not None else None

    @property
    def rough_manufacturing_process_controls(self) -> '_674.ManufacturingProcessControls':
        '''ManufacturingProcessControls: 'RoughManufacturingProcessControls' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_674.ManufacturingProcessControls)(self.wrapped.RoughManufacturingProcessControls) if self.wrapped.RoughManufacturingProcessControls is not None else None

    @property
    def finish_manufacturing_process_controls(self) -> '_674.ManufacturingProcessControls':
        '''ManufacturingProcessControls: 'FinishManufacturingProcessControls' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_674.ManufacturingProcessControls)(self.wrapped.FinishManufacturingProcessControls) if self.wrapped.FinishManufacturingProcessControls is not None else None

    def create_new_rough_cutter_compatible_with_gear_in_design_mode(self):
        ''' 'CreateNewRoughCutterCompatibleWithGearInDesignMode' is the original name of this method.'''

        self.wrapped.CreateNewRoughCutterCompatibleWithGearInDesignMode()

    def create_new_finish_cutter_compatible_with_gear_in_design_mode(self):
        ''' 'CreateNewFinishCutterCompatibleWithGearInDesignMode' is the original name of this method.'''

        self.wrapped.CreateNewFinishCutterCompatibleWithGearInDesignMode()
