'''_1528.py

CustomReportCadDrawing
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.utility.cad_export import _1601
from mastapy.utility.report import _1544
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_CAD_DRAWING = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportCadDrawing')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportCadDrawing',)


class CustomReportCadDrawing(_1544.CustomReportNameableItem):
    '''CustomReportCadDrawing

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_CAD_DRAWING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportCadDrawing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_stock_drawing(self) -> 'bool':
        '''bool: 'UseStockDrawing' is the original name of this property.'''

        return self.wrapped.UseStockDrawing

    @use_stock_drawing.setter
    def use_stock_drawing(self, value: 'bool'):
        self.wrapped.UseStockDrawing = bool(value) if value else False

    @property
    def stock_drawing(self) -> '_1601.StockDrawings':
        '''StockDrawings: 'StockDrawing' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.StockDrawing)
        return constructor.new(_1601.StockDrawings)(value) if value is not None else None

    @stock_drawing.setter
    def stock_drawing(self, value: '_1601.StockDrawings'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.StockDrawing = value

    @property
    def scale(self) -> 'float':
        '''float: 'Scale' is the original name of this property.'''

        return self.wrapped.Scale

    @scale.setter
    def scale(self, value: 'float'):
        self.wrapped.Scale = float(value) if value else 0.0
