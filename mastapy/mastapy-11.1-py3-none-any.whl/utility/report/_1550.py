'''_1550.py

CustomReportText
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.html import _272
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility.report import _1533
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_TEXT = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportText')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportText',)


class CustomReportText(_1533.CustomReportDefinitionItem):
    '''CustomReportText

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_TEXT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportText.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def text(self) -> 'str':
        '''str: 'Text' is the original name of this property.'''

        return self.wrapped.Text

    @text.setter
    def text(self, value: 'str'):
        self.wrapped.Text = str(value) if value else ''

    @property
    def is_heading(self) -> 'bool':
        '''bool: 'IsHeading' is the original name of this property.'''

        return self.wrapped.IsHeading

    @is_heading.setter
    def is_heading(self, value: 'bool'):
        self.wrapped.IsHeading = bool(value) if value else False

    @property
    def heading_type(self) -> '_272.HeadingType':
        '''HeadingType: 'HeadingType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.HeadingType)
        return constructor.new(_272.HeadingType)(value) if value is not None else None

    @heading_type.setter
    def heading_type(self, value: '_272.HeadingType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.HeadingType = value

    @property
    def bold(self) -> 'bool':
        '''bool: 'Bold' is the original name of this property.'''

        return self.wrapped.Bold

    @bold.setter
    def bold(self, value: 'bool'):
        self.wrapped.Bold = bool(value) if value else False

    @property
    def cad_text_size(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CADTextSize' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CADTextSize) if self.wrapped.CADTextSize is not None else None

    @cad_text_size.setter
    def cad_text_size(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CADTextSize = value

    @property
    def show_unit(self) -> 'bool':
        '''bool: 'ShowUnit' is the original name of this property.'''

        return self.wrapped.ShowUnit

    @show_unit.setter
    def show_unit(self, value: 'bool'):
        self.wrapped.ShowUnit = bool(value) if value else False

    @property
    def show_symbol(self) -> 'bool':
        '''bool: 'ShowSymbol' is the original name of this property.'''

        return self.wrapped.ShowSymbol

    @show_symbol.setter
    def show_symbol(self, value: 'bool'):
        self.wrapped.ShowSymbol = bool(value) if value else False
