'''_669.py

FinishStockPoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FINISH_STOCK_POINT = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'FinishStockPoint')


__docformat__ = 'restructuredtext en'
__all__ = ('FinishStockPoint',)


class FinishStockPoint(_0.APIBase):
    '''FinishStockPoint

    This is a mastapy class.
    '''

    TYPE = _FINISH_STOCK_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FinishStockPoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Radius

    @property
    def index(self) -> 'str':
        '''str: 'Index' is the original name of this property.'''

        return self.wrapped.Index

    @index.setter
    def index(self, value: 'str'):
        self.wrapped.Index = str(value) if value else ''

    @property
    def finish_stock_arc_length(self) -> 'float':
        '''float: 'FinishStockArcLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FinishStockArcLength

    @property
    def finish_stock_tangent_to_the_base_circle(self) -> 'float':
        '''float: 'FinishStockTangentToTheBaseCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FinishStockTangentToTheBaseCircle
