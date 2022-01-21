'''_1543.py

CustomReportMultiPropertyItemBase
'''


from mastapy.utility.report import _1544
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_MULTI_PROPERTY_ITEM_BASE = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportMultiPropertyItemBase')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportMultiPropertyItemBase',)


class CustomReportMultiPropertyItemBase(_1544.CustomReportNameableItem):
    '''CustomReportMultiPropertyItemBase

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_MULTI_PROPERTY_ITEM_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportMultiPropertyItemBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
