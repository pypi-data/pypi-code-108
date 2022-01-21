'''_1525.py

CustomGraphic
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1533
from mastapy._internal.python_net import python_net_import

_CUSTOM_GRAPHIC = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomGraphic')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomGraphic',)


class CustomGraphic(_1533.CustomReportDefinitionItem):
    '''CustomGraphic

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_GRAPHIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomGraphic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def width(self) -> 'int':
        '''int: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'int'):
        self.wrapped.Width = int(value) if value else 0

    @property
    def height(self) -> 'int':
        '''int: 'Height' is the original name of this property.'''

        return self.wrapped.Height

    @height.setter
    def height(self, value: 'int'):
        self.wrapped.Height = int(value) if value else 0

    @property
    def transposed(self) -> 'bool':
        '''bool: 'Transposed' is the original name of this property.'''

        return self.wrapped.Transposed

    @transposed.setter
    def transposed(self, value: 'bool'):
        self.wrapped.Transposed = bool(value) if value else False

    @property
    def width_for_cad(self) -> 'float':
        '''float: 'WidthForCAD' is the original name of this property.'''

        return self.wrapped.WidthForCAD

    @width_for_cad.setter
    def width_for_cad(self, value: 'float'):
        self.wrapped.WidthForCAD = float(value) if value else 0.0

    @property
    def height_for_cad(self) -> 'float':
        '''float: 'HeightForCAD' is the original name of this property.'''

        return self.wrapped.HeightForCAD

    @height_for_cad.setter
    def height_for_cad(self, value: 'float'):
        self.wrapped.HeightForCAD = float(value) if value else 0.0
