'''_4966.py

PerModeResultsReport
'''


from mastapy.utility.enums import _1589
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.utility.report import _1529
from mastapy._internal.python_net import python_net_import

_PER_MODE_RESULTS_REPORT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'PerModeResultsReport')


__docformat__ = 'restructuredtext en'
__all__ = ('PerModeResultsReport',)


class PerModeResultsReport(_1529.CustomReportChart):
    '''PerModeResultsReport

    This is a mastapy class.
    '''

    TYPE = _PER_MODE_RESULTS_REPORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PerModeResultsReport.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def display_option(self) -> '_1589.TableAndChartOptions':
        '''TableAndChartOptions: 'DisplayOption' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DisplayOption)
        return constructor.new(_1589.TableAndChartOptions)(value) if value is not None else None

    @display_option.setter
    def display_option(self, value: '_1589.TableAndChartOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DisplayOption = value

    @property
    def show_all_modes(self) -> 'bool':
        '''bool: 'ShowAllModes' is the original name of this property.'''

        return self.wrapped.ShowAllModes

    @show_all_modes.setter
    def show_all_modes(self, value: 'bool'):
        self.wrapped.ShowAllModes = bool(value) if value else False

    @property
    def transpose_chart(self) -> 'bool':
        '''bool: 'TransposeChart' is the original name of this property.'''

        return self.wrapped.TransposeChart

    @transpose_chart.setter
    def transpose_chart(self, value: 'bool'):
        self.wrapped.TransposeChart = bool(value) if value else False

    @property
    def transpose_table(self) -> 'bool':
        '''bool: 'TransposeTable' is the original name of this property.'''

        return self.wrapped.TransposeTable

    @transpose_table.setter
    def transpose_table(self, value: 'bool'):
        self.wrapped.TransposeTable = bool(value) if value else False

    @property
    def include_connected_parts_for_connections(self) -> 'bool':
        '''bool: 'IncludeConnectedPartsForConnections' is the original name of this property.'''

        return self.wrapped.IncludeConnectedPartsForConnections

    @include_connected_parts_for_connections.setter
    def include_connected_parts_for_connections(self, value: 'bool'):
        self.wrapped.IncludeConnectedPartsForConnections = bool(value) if value else False

    @property
    def maximum_number_of_modes_to_show_on_a_single_table_or_chart(self) -> 'int':
        '''int: 'MaximumNumberOfModesToShowOnASingleTableOrChart' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfModesToShowOnASingleTableOrChart

    @maximum_number_of_modes_to_show_on_a_single_table_or_chart.setter
    def maximum_number_of_modes_to_show_on_a_single_table_or_chart(self, value: 'int'):
        self.wrapped.MaximumNumberOfModesToShowOnASingleTableOrChart = int(value) if value else 0
