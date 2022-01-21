'''_1532.py

CustomReportColumns
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1538, _1531
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_COLUMNS = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportColumns')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportColumns',)


class CustomReportColumns(_1538.CustomReportItemContainerCollection['_1531.CustomReportColumn']):
    '''CustomReportColumns

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_COLUMNS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportColumns.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_columns(self) -> 'int':
        '''int: 'NumberOfColumns' is the original name of this property.'''

        return self.wrapped.NumberOfColumns

    @number_of_columns.setter
    def number_of_columns(self, value: 'int'):
        self.wrapped.NumberOfColumns = int(value) if value else 0

    @property
    def show_adjustable_column_divider(self) -> 'bool':
        '''bool: 'ShowAdjustableColumnDivider' is the original name of this property.'''

        return self.wrapped.ShowAdjustableColumnDivider

    @show_adjustable_column_divider.setter
    def show_adjustable_column_divider(self, value: 'bool'):
        self.wrapped.ShowAdjustableColumnDivider = bool(value) if value else False
