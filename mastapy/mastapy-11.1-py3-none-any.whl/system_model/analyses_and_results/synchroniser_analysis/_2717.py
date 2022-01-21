'''_2717.py

SynchroniserShift
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.analyses_and_results.load_case_groups import _5388
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.part_model.couplings import _2344, _2346
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SHIFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SynchroniserAnalysis', 'SynchroniserShift')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserShift',)


class SynchroniserShift(_0.APIBase):
    '''SynchroniserShift

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SHIFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserShift.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sleeve_impulse(self) -> 'float':
        '''float: 'SleeveImpulse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SleeveImpulse

    @property
    def sleeve_axial_force(self) -> 'float':
        '''float: 'SleeveAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SleeveAxialForce

    @property
    def synchronisation_torque(self) -> 'float':
        '''float: 'SynchronisationTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SynchronisationTorque

    @property
    def indexing_torque(self) -> 'float':
        '''float: 'IndexingTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IndexingTorque

    @property
    def frictional_work(self) -> 'float':
        '''float: 'FrictionalWork' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalWork

    @property
    def slipping_velocity(self) -> 'float':
        '''float: 'SlippingVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlippingVelocity

    @property
    def frictional_energy_per_area_for_shift_time(self) -> 'float':
        '''float: 'FrictionalEnergyPerAreaForShiftTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalEnergyPerAreaForShiftTime

    @property
    def mean_frictional_power_for_shift_time(self) -> 'float':
        '''float: 'MeanFrictionalPowerForShiftTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanFrictionalPowerForShiftTime

    @property
    def mean_frictional_power_per_area_for_shift_time(self) -> 'float':
        '''float: 'MeanFrictionalPowerPerAreaForShiftTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanFrictionalPowerPerAreaForShiftTime

    @property
    def hand_ball_impulse(self) -> 'float':
        '''float: 'HandBallImpulse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HandBallImpulse

    @property
    def final_synchronised_speed(self) -> 'float':
        '''float: 'FinalSynchronisedSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FinalSynchronisedSpeed

    @property
    def downstream_component(self) -> 'str':
        '''str: 'DownstreamComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DownstreamComponent

    @property
    def upstream_component(self) -> 'str':
        '''str: 'UpstreamComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpstreamComponent

    @property
    def initial_upstream_component_speed(self) -> 'float':
        '''float: 'InitialUpstreamComponentSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InitialUpstreamComponentSpeed

    @property
    def initial_downstream_component_speed(self) -> 'float':
        '''float: 'InitialDownstreamComponentSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InitialDownstreamComponentSpeed

    @property
    def clutch_inertia(self) -> 'float':
        '''float: 'ClutchInertia' is the original name of this property.'''

        return self.wrapped.ClutchInertia

    @clutch_inertia.setter
    def clutch_inertia(self, value: 'float'):
        self.wrapped.ClutchInertia = float(value) if value else 0.0

    @property
    def engine_power_load_name(self) -> 'str':
        '''str: 'EnginePowerLoadName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnginePowerLoadName

    @property
    def upstream_inertia(self) -> 'float':
        '''float: 'UpstreamInertia' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpstreamInertia

    @property
    def initial_design_state(self) -> 'list_with_selected_item.ListWithSelectedItem_DesignState':
        '''list_with_selected_item.ListWithSelectedItem_DesignState: 'InitialDesignState' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_DesignState)(self.wrapped.InitialDesignState) if self.wrapped.InitialDesignState is not None else None

    @initial_design_state.setter
    def initial_design_state(self, value: 'list_with_selected_item.ListWithSelectedItem_DesignState.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_DesignState.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_DesignState.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.InitialDesignState = value

    @property
    def final_design_state(self) -> 'list_with_selected_item.ListWithSelectedItem_DesignState':
        '''list_with_selected_item.ListWithSelectedItem_DesignState: 'FinalDesignState' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_DesignState)(self.wrapped.FinalDesignState) if self.wrapped.FinalDesignState is not None else None

    @final_design_state.setter
    def final_design_state(self, value: 'list_with_selected_item.ListWithSelectedItem_DesignState.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_DesignState.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_DesignState.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.FinalDesignState = value

    @property
    def initial_engine_speed(self) -> 'float':
        '''float: 'InitialEngineSpeed' is the original name of this property.'''

        return self.wrapped.InitialEngineSpeed

    @initial_engine_speed.setter
    def initial_engine_speed(self, value: 'float'):
        self.wrapped.InitialEngineSpeed = float(value) if value else 0.0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def shift_mechanism_ratio(self) -> 'float':
        '''float: 'ShiftMechanismRatio' is the original name of this property.'''

        return self.wrapped.ShiftMechanismRatio

    @shift_mechanism_ratio.setter
    def shift_mechanism_ratio(self, value: 'float'):
        self.wrapped.ShiftMechanismRatio = float(value) if value else 0.0

    @property
    def shift_mechanism_efficiency(self) -> 'float':
        '''float: 'ShiftMechanismEfficiency' is the original name of this property.'''

        return self.wrapped.ShiftMechanismEfficiency

    @shift_mechanism_efficiency.setter
    def shift_mechanism_efficiency(self, value: 'float'):
        self.wrapped.ShiftMechanismEfficiency = float(value) if value else 0.0

    @property
    def shift_time(self) -> 'float':
        '''float: 'ShiftTime' is the original name of this property.'''

        return self.wrapped.ShiftTime

    @shift_time.setter
    def shift_time(self, value: 'float'):
        self.wrapped.ShiftTime = float(value) if value else 0.0

    @property
    def hand_ball_force(self) -> 'float':
        '''float: 'HandBallForce' is the original name of this property.'''

        return self.wrapped.HandBallForce

    @hand_ball_force.setter
    def hand_ball_force(self, value: 'float'):
        self.wrapped.HandBallForce = float(value) if value else 0.0

    @property
    def total_normal_force_on_cones(self) -> 'float':
        '''float: 'TotalNormalForceOnCones' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalNormalForceOnCones

    @property
    def cone_normal_pressure_when_all_cones_take_equal_force(self) -> 'float':
        '''float: 'ConeNormalPressureWhenAllConesTakeEqualForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConeNormalPressureWhenAllConesTakeEqualForce

    @property
    def maximum_cone_normal_pressure(self) -> 'float':
        '''float: 'MaximumConeNormalPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumConeNormalPressure

    @property
    def time_specified(self) -> 'bool':
        '''bool: 'TimeSpecified' is the original name of this property.'''

        return self.wrapped.TimeSpecified

    @time_specified.setter
    def time_specified(self, value: 'bool'):
        self.wrapped.TimeSpecified = bool(value) if value else False

    @property
    def cone_torque_index_torque(self) -> 'float':
        '''float: 'ConeTorqueIndexTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConeTorqueIndexTorque

    @property
    def cone(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'Cone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.Cone) if self.wrapped.Cone is not None else None

    @property
    def sleeve(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'Sleeve' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2346.SynchroniserSleeve)(self.wrapped.Sleeve) if self.wrapped.Sleeve is not None else None

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
