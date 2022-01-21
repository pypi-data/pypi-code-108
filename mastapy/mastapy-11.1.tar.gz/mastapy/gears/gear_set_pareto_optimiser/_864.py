'''_864.py

ChartInfoBase
'''


from typing import List, Generic, TypeVar

from PIL.Image import Image

from mastapy.math_utility.optimisation import _1350
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.utility.reporting_property_framework import _1517
from mastapy.gears.gear_set_pareto_optimiser import (
    _866, _865, _868, _872,
    _873, _876, _879, _898,
    _899, _862, _874
)
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy.gears.analysis import _1161
from mastapy._internal.python_net import python_net_import

_CHART_INFO_BASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ChartInfoBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ChartInfoBase',)


TAnalysis = TypeVar('TAnalysis', bound='_1161.AbstractGearSetAnalysis')
TCandidate = TypeVar('TCandidate')


class ChartInfoBase(_0.APIBase, Generic[TAnalysis, TCandidate]):
    '''ChartInfoBase

    This is a mastapy class.

    Generic Types:
        TAnalysis
        TCandidate
    '''

    TYPE = _CHART_INFO_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ChartInfoBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def select_chart_type(self) -> '_1350.ParetoOptimisationStrategyChartInformation.ScatterOrBarChart':
        '''ParetoOptimisationStrategyChartInformation.ScatterOrBarChart: 'SelectChartType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SelectChartType)
        return constructor.new(_1350.ParetoOptimisationStrategyChartInformation.ScatterOrBarChart)(value) if value is not None else None

    @select_chart_type.setter
    def select_chart_type(self, value: '_1350.ParetoOptimisationStrategyChartInformation.ScatterOrBarChart'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SelectChartType = value

    @property
    def chart_type(self) -> '_1517.CustomChartType':
        '''CustomChartType: 'ChartType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ChartType)
        return constructor.new(_1517.CustomChartType)(value) if value is not None else None

    @property
    def selected_candidate_design(self) -> 'int':
        '''int: 'SelectedCandidateDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SelectedCandidateDesign

    @property
    def result_chart_scatter(self) -> 'Image':
        '''Image: 'ResultChartScatter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ResultChartScatter)
        return value

    @property
    def result_chart_bar_and_line(self) -> 'Image':
        '''Image: 'ResultChartBarAndLine' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ResultChartBarAndLine)
        return value

    @property
    def chart_name(self) -> 'str':
        '''str: 'ChartName' is the original name of this property.'''

        return self.wrapped.ChartName

    @chart_name.setter
    def chart_name(self, value: 'str'):
        self.wrapped.ChartName = str(value) if value else ''

    @property
    def optimiser(self) -> '_866.DesignSpaceSearchBase[TAnalysis, TCandidate]':
        '''DesignSpaceSearchBase[TAnalysis, TCandidate]: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _866.DesignSpaceSearchBase[TAnalysis, TCandidate].TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to DesignSpaceSearchBase[TAnalysis, TCandidate]. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_cylindrical_gear_set_pareto_optimiser(self) -> '_865.CylindricalGearSetParetoOptimiser':
        '''CylindricalGearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _865.CylindricalGearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to CylindricalGearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_face_gear_set_pareto_optimiser(self) -> '_868.FaceGearSetParetoOptimiser':
        '''FaceGearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _868.FaceGearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to FaceGearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_gear_set_pareto_optimiser(self) -> '_872.GearSetParetoOptimiser':
        '''GearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _872.GearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to GearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_hypoid_gear_set_pareto_optimiser(self) -> '_873.HypoidGearSetParetoOptimiser':
        '''HypoidGearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _873.HypoidGearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to HypoidGearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_micro_geometry_design_space_search(self) -> '_876.MicroGeometryDesignSpaceSearch':
        '''MicroGeometryDesignSpaceSearch: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _876.MicroGeometryDesignSpaceSearch.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to MicroGeometryDesignSpaceSearch. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_micro_geometry_gear_set_design_space_search(self) -> '_879.MicroGeometryGearSetDesignSpaceSearch':
        '''MicroGeometryGearSetDesignSpaceSearch: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _879.MicroGeometryGearSetDesignSpaceSearch.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to MicroGeometryGearSetDesignSpaceSearch. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_spiral_bevel_gear_set_pareto_optimiser(self) -> '_898.SpiralBevelGearSetParetoOptimiser':
        '''SpiralBevelGearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _898.SpiralBevelGearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to SpiralBevelGearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def optimiser_of_type_straight_bevel_gear_set_pareto_optimiser(self) -> '_899.StraightBevelGearSetParetoOptimiser':
        '''StraightBevelGearSetParetoOptimiser: 'Optimiser' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _899.StraightBevelGearSetParetoOptimiser.TYPE not in self.wrapped.Optimiser.__class__.__mro__:
            raise CastException('Failed to cast optimiser to StraightBevelGearSetParetoOptimiser. Expected: {}.'.format(self.wrapped.Optimiser.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Optimiser.__class__)(self.wrapped.Optimiser) if self.wrapped.Optimiser is not None else None

    @property
    def bars(self) -> 'List[_862.BarForPareto[TAnalysis, TCandidate]]':
        '''List[BarForPareto[TAnalysis, TCandidate]]: 'Bars' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Bars, constructor.new(_862.BarForPareto)[TAnalysis, TCandidate])
        return value

    @property
    def input_sliders(self) -> 'List[_874.InputSliderForPareto[TAnalysis, TCandidate]]':
        '''List[InputSliderForPareto[TAnalysis, TCandidate]]: 'InputSliders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InputSliders, constructor.new(_874.InputSliderForPareto)[TAnalysis, TCandidate])
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def remove_chart(self):
        ''' 'RemoveChart' is the original name of this method.'''

        self.wrapped.RemoveChart()

    def add_bar(self):
        ''' 'AddBar' is the original name of this method.'''

        self.wrapped.AddBar()

    def add_selected_design(self):
        ''' 'AddSelectedDesign' is the original name of this method.'''

        self.wrapped.AddSelectedDesign()

    def add_selected_designs(self):
        ''' 'AddSelectedDesigns' is the original name of this method.'''

        self.wrapped.AddSelectedDesigns()

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
