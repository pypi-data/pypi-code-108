'''_1548.py

CustomReportTab
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1540
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_TAB = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportTab')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportTab',)


class CustomReportTab(_1540.CustomReportItemContainerCollectionItem):
    '''CustomReportTab

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_TAB

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportTab.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hide_when_has_no_content(self) -> 'bool':
        '''bool: 'HideWhenHasNoContent' is the original name of this property.'''

        return self.wrapped.HideWhenHasNoContent

    @hide_when_has_no_content.setter
    def hide_when_has_no_content(self, value: 'bool'):
        self.wrapped.HideWhenHasNoContent = bool(value) if value else False

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''
