'''_1403.py

Unit
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_UNIT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'Unit')


__docformat__ = 'restructuredtext en'
__all__ = ('Unit',)


class Unit(_0.APIBase):
    '''Unit

    This is a mastapy class.
    '''

    TYPE = _UNIT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Unit.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def symbol(self) -> 'str':
        '''str: 'Symbol' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Symbol

    @property
    def html_symbol(self) -> 'str':
        '''str: 'HTMLSymbol' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HTMLSymbol

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Offset

    @property
    def scale(self) -> 'float':
        '''float: 'Scale' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Scale
