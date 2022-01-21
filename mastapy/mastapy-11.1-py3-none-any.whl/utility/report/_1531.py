'''_1531.py

CustomReportColumn
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1540
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_COLUMN = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportColumn')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportColumn',)


class CustomReportColumn(_1540.CustomReportItemContainerCollectionItem):
    '''CustomReportColumn

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_COLUMN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportColumn.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def auto_width(self) -> 'bool':
        '''bool: 'AutoWidth' is the original name of this property.'''

        return self.wrapped.AutoWidth

    @auto_width.setter
    def auto_width(self, value: 'bool'):
        self.wrapped.AutoWidth = bool(value) if value else False
