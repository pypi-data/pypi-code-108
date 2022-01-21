'''_1524.py

CustomChart
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1525
from mastapy._internal.python_net import python_net_import

_CUSTOM_CHART = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomChart')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomChart',)


class CustomChart(_1525.CustomGraphic):
    '''CustomChart

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_CHART

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomChart.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_header(self) -> 'bool':
        '''bool: 'ShowHeader' is the original name of this property.'''

        return self.wrapped.ShowHeader

    @show_header.setter
    def show_header(self, value: 'bool'):
        self.wrapped.ShowHeader = bool(value) if value else False

    @property
    def line_thickness_factor(self) -> 'int':
        '''int: 'LineThicknessFactor' is the original name of this property.'''

        return self.wrapped.LineThicknessFactor

    @line_thickness_factor.setter
    def line_thickness_factor(self, value: 'int'):
        self.wrapped.LineThicknessFactor = int(value) if value else 0

    @property
    def text_is_uppercase(self) -> 'bool':
        '''bool: 'TextIsUppercase' is the original name of this property.'''

        return self.wrapped.TextIsUppercase

    @text_is_uppercase.setter
    def text_is_uppercase(self, value: 'bool'):
        self.wrapped.TextIsUppercase = bool(value) if value else False
