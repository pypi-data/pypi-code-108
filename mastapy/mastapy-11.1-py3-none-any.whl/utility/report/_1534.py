'''_1534.py

CustomReportHorizontalLine
'''


from mastapy.utility.report import _1536
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_HORIZONTAL_LINE = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportHorizontalLine')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportHorizontalLine',)


class CustomReportHorizontalLine(_1536.CustomReportItem):
    '''CustomReportHorizontalLine

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_HORIZONTAL_LINE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportHorizontalLine.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
