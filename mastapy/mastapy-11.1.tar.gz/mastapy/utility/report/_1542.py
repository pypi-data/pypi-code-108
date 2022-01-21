'''_1542.py

CustomReportMultiPropertyItem
'''


from typing import Generic, TypeVar

from mastapy.utility.report import _1543, _1546
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_MULTI_PROPERTY_ITEM = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportMultiPropertyItem')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportMultiPropertyItem',)


TItem = TypeVar('TItem', bound='_1546.CustomReportPropertyItem')


class CustomReportMultiPropertyItem(_1543.CustomReportMultiPropertyItemBase, Generic[TItem]):
    '''CustomReportMultiPropertyItem

    This is a mastapy class.

    Generic Types:
        TItem
    '''

    TYPE = _CUSTOM_REPORT_MULTI_PROPERTY_ITEM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportMultiPropertyItem.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
