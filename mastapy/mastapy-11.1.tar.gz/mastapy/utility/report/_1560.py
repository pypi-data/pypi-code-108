'''_1560.py

UserTextRow
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.utility.report import _1558, _1551
from mastapy._internal.python_net import python_net_import

_USER_TEXT_ROW = python_net_import('SMT.MastaAPI.Utility.Report', 'UserTextRow')


__docformat__ = 'restructuredtext en'
__all__ = ('UserTextRow',)


class UserTextRow(_1551.CustomRow):
    '''UserTextRow

    This is a mastapy class.
    '''

    TYPE = _USER_TEXT_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UserTextRow.TYPE'):
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
    def additional_text(self) -> 'str':
        '''str: 'AdditionalText' is the original name of this property.'''

        return self.wrapped.AdditionalText

    @additional_text.setter
    def additional_text(self, value: 'str'):
        self.wrapped.AdditionalText = str(value) if value else ''

    @property
    def is_heading(self) -> 'bool':
        '''bool: 'IsHeading' is the original name of this property.'''

        return self.wrapped.IsHeading

    @is_heading.setter
    def is_heading(self, value: 'bool'):
        self.wrapped.IsHeading = bool(value) if value else False

    @property
    def heading_size(self) -> '_1558.HeadingSize':
        '''HeadingSize: 'HeadingSize' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.HeadingSize)
        return constructor.new(_1558.HeadingSize)(value) if value is not None else None

    @heading_size.setter
    def heading_size(self, value: '_1558.HeadingSize'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.HeadingSize = value

    @property
    def show_additional_text(self) -> 'bool':
        '''bool: 'ShowAdditionalText' is the original name of this property.'''

        return self.wrapped.ShowAdditionalText

    @show_additional_text.setter
    def show_additional_text(self, value: 'bool'):
        self.wrapped.ShowAdditionalText = bool(value) if value else False
