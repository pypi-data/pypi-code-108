'''_2303.py

SuperchargerRotorSet
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.part_model.gears.supercharger_rotor_set import (
    _2305, _2298, _2300, _2295,
    _2297, _2296, _2299
)
from mastapy.utility_gui.charts import _1624
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_SUPERCHARGER_ROTOR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears.SuperchargerRotorSet', 'SuperchargerRotorSet')


__docformat__ = 'restructuredtext en'
__all__ = ('SuperchargerRotorSet',)


class SuperchargerRotorSet(_1597.NamedDatabaseItem):
    '''SuperchargerRotorSet

    This is a mastapy class.
    '''

    TYPE = _SUPERCHARGER_ROTOR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SuperchargerRotorSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def selected_file_name(self) -> 'str':
        '''str: 'SelectedFileName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SelectedFileName

    @property
    def y_variable_for_imported_data(self) -> '_2305.YVariableForImportedData':
        '''YVariableForImportedData: 'YVariableForImportedData' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.YVariableForImportedData)
        return constructor.new(_2305.YVariableForImportedData)(value) if value is not None else None

    @y_variable_for_imported_data.setter
    def y_variable_for_imported_data(self, value: '_2305.YVariableForImportedData'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.YVariableForImportedData = value

    @property
    def lateral_reaction_force(self) -> 'float':
        '''float: 'LateralReactionForce' is the original name of this property.'''

        return self.wrapped.LateralReactionForce

    @lateral_reaction_force.setter
    def lateral_reaction_force(self, value: 'float'):
        self.wrapped.LateralReactionForce = float(value) if value else 0.0

    @property
    def vertical_reaction_force(self) -> 'float':
        '''float: 'VerticalReactionForce' is the original name of this property.'''

        return self.wrapped.VerticalReactionForce

    @vertical_reaction_force.setter
    def vertical_reaction_force(self, value: 'float'):
        self.wrapped.VerticalReactionForce = float(value) if value else 0.0

    @property
    def axial_reaction_force(self) -> 'float':
        '''float: 'AxialReactionForce' is the original name of this property.'''

        return self.wrapped.AxialReactionForce

    @axial_reaction_force.setter
    def axial_reaction_force(self, value: 'float'):
        self.wrapped.AxialReactionForce = float(value) if value else 0.0

    @property
    def lateral_reaction_moment(self) -> 'float':
        '''float: 'LateralReactionMoment' is the original name of this property.'''

        return self.wrapped.LateralReactionMoment

    @lateral_reaction_moment.setter
    def lateral_reaction_moment(self, value: 'float'):
        self.wrapped.LateralReactionMoment = float(value) if value else 0.0

    @property
    def vertical_reaction_moment(self) -> 'float':
        '''float: 'VerticalReactionMoment' is the original name of this property.'''

        return self.wrapped.VerticalReactionMoment

    @vertical_reaction_moment.setter
    def vertical_reaction_moment(self, value: 'float'):
        self.wrapped.VerticalReactionMoment = float(value) if value else 0.0

    @property
    def dynamic_load_factor(self) -> 'float':
        '''float: 'DynamicLoadFactor' is the original name of this property.'''

        return self.wrapped.DynamicLoadFactor

    @dynamic_load_factor.setter
    def dynamic_load_factor(self, value: 'float'):
        self.wrapped.DynamicLoadFactor = float(value) if value else 0.0

    @property
    def supercharger_map_chart(self) -> '_1624.ThreeDChartDefinition':
        '''ThreeDChartDefinition: 'SuperchargerMapChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1624.ThreeDChartDefinition)(self.wrapped.SuperchargerMapChart) if self.wrapped.SuperchargerMapChart is not None else None

    @property
    def file(self) -> '_2298.RotorSetDataInputFileOptions':
        '''RotorSetDataInputFileOptions: 'File' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2298.RotorSetDataInputFileOptions)(self.wrapped.File) if self.wrapped.File is not None else None

    @property
    def rotor_speed(self) -> '_2300.RotorSpeedInputOptions':
        '''RotorSpeedInputOptions: 'RotorSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2300.RotorSpeedInputOptions)(self.wrapped.RotorSpeed) if self.wrapped.RotorSpeed is not None else None

    @property
    def boost_pressure(self) -> '_2295.BoostPressureInputOptions':
        '''BoostPressureInputOptions: 'BoostPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2295.BoostPressureInputOptions)(self.wrapped.BoostPressure) if self.wrapped.BoostPressure is not None else None

    @property
    def pressure_ratio(self) -> '_2297.PressureRatioInputOptions':
        '''PressureRatioInputOptions: 'PressureRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2297.PressureRatioInputOptions)(self.wrapped.PressureRatio) if self.wrapped.PressureRatio is not None else None

    @property
    def input_power(self) -> '_2296.InputPowerInputOptions':
        '''InputPowerInputOptions: 'InputPower' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2296.InputPowerInputOptions)(self.wrapped.InputPower) if self.wrapped.InputPower is not None else None

    @property
    def measured_points(self) -> 'List[_2299.RotorSetMeasuredPoint]':
        '''List[RotorSetMeasuredPoint]: 'MeasuredPoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeasuredPoints, constructor.new(_2299.RotorSetMeasuredPoint))
        return value

    def select_different_file(self):
        ''' 'SelectDifferentFile' is the original name of this method.'''

        self.wrapped.SelectDifferentFile()
