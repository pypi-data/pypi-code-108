'''_1527.py

CustomReport
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.utility.report import (
    _1522, _1521, _1520, _1554,
    _1537
)
from mastapy._internal.implicit import enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReport')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReport',)


class CustomReport(_1537.CustomReportItemContainer):
    '''CustomReport

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReport.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_default_border(self) -> 'bool':
        '''bool: 'UseDefaultBorder' is the original name of this property.'''

        return self.wrapped.UseDefaultBorder

    @use_default_border.setter
    def use_default_border(self, value: 'bool'):
        self.wrapped.UseDefaultBorder = bool(value) if value else False

    @property
    def font_height_for_cad_tables(self) -> 'float':
        '''float: 'FontHeightForCADTables' is the original name of this property.'''

        return self.wrapped.FontHeightForCADTables

    @font_height_for_cad_tables.setter
    def font_height_for_cad_tables(self, value: 'float'):
        self.wrapped.FontHeightForCADTables = float(value) if value else 0.0

    @property
    def text_margin_for_cad_tables(self) -> 'float':
        '''float: 'TextMarginForCADTables' is the original name of this property.'''

        return self.wrapped.TextMarginForCADTables

    @text_margin_for_cad_tables.setter
    def text_margin_for_cad_tables(self, value: 'float'):
        self.wrapped.TextMarginForCADTables = float(value) if value else 0.0

    @property
    def cad_table_border_style(self) -> '_1522.CadTableBorderType':
        '''CadTableBorderType: 'CADTableBorderStyle' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CADTableBorderStyle)
        return constructor.new(_1522.CadTableBorderType)(value) if value is not None else None

    @cad_table_border_style.setter
    def cad_table_border_style(self, value: '_1522.CadTableBorderType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CADTableBorderStyle = value

    @property
    def hide_cad_table_borders(self) -> 'bool':
        '''bool: 'HideCADTableBorders' is the original name of this property.'''

        return self.wrapped.HideCADTableBorders

    @hide_cad_table_borders.setter
    def hide_cad_table_borders(self, value: 'bool'):
        self.wrapped.HideCADTableBorders = bool(value) if value else False

    @property
    def page_size_for_cad_export(self) -> '_1521.CadPageSize':
        '''CadPageSize: 'PageSizeForCADExport' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PageSizeForCADExport)
        return constructor.new(_1521.CadPageSize)(value) if value is not None else None

    @page_size_for_cad_export.setter
    def page_size_for_cad_export(self, value: '_1521.CadPageSize'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PageSizeForCADExport = value

    @property
    def page_orientation_for_cad_export(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CadPageOrientation':
        '''enum_with_selected_value.EnumWithSelectedValue_CadPageOrientation: 'PageOrientationForCADExport' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CadPageOrientation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.PageOrientationForCADExport, value) if self.wrapped.PageOrientationForCADExport is not None else None

    @page_orientation_for_cad_export.setter
    def page_orientation_for_cad_export(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CadPageOrientation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CadPageOrientation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.PageOrientationForCADExport = value

    @property
    def page_height_for_cad_export(self) -> 'float':
        '''float: 'PageHeightForCADExport' is the original name of this property.'''

        return self.wrapped.PageHeightForCADExport

    @page_height_for_cad_export.setter
    def page_height_for_cad_export(self, value: 'float'):
        self.wrapped.PageHeightForCADExport = float(value) if value else 0.0

    @property
    def page_width_for_cad_export(self) -> 'float':
        '''float: 'PageWidthForCADExport' is the original name of this property.'''

        return self.wrapped.PageWidthForCADExport

    @page_width_for_cad_export.setter
    def page_width_for_cad_export(self, value: 'float'):
        self.wrapped.PageWidthForCADExport = float(value) if value else 0.0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def show_table_of_contents(self) -> 'bool':
        '''bool: 'ShowTableOfContents' is the original name of this property.'''

        return self.wrapped.ShowTableOfContents

    @show_table_of_contents.setter
    def show_table_of_contents(self, value: 'bool'):
        self.wrapped.ShowTableOfContents = bool(value) if value else False

    @property
    def include_report_check(self) -> '_1554.DefinitionBooleanCheckOptions':
        '''DefinitionBooleanCheckOptions: 'IncludeReportCheck' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.IncludeReportCheck)
        return constructor.new(_1554.DefinitionBooleanCheckOptions)(value) if value is not None else None

    @include_report_check.setter
    def include_report_check(self, value: '_1554.DefinitionBooleanCheckOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.IncludeReportCheck = value
