'''_1287.py

Range
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RANGE = python_net_import('SMT.MastaAPI.MathUtility', 'Range')


__docformat__ = 'restructuredtext en'
__all__ = ('Range',)


class Range(_0.APIBase):
    '''Range

    This is a mastapy class.
    '''

    TYPE = _RANGE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Range.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def min(self) -> 'float':
        '''float: 'Min' is the original name of this property.'''

        return self.wrapped.Min

    @min.setter
    def min(self, value: 'float'):
        self.wrapped.Min = float(value) if value else 0.0

    @property
    def max(self) -> 'float':
        '''float: 'Max' is the original name of this property.'''

        return self.wrapped.Max

    @max.setter
    def max(self, value: 'float'):
        self.wrapped.Max = float(value) if value else 0.0
