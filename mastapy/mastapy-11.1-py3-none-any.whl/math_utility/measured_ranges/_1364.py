'''_1364.py

ShortLengthRange
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1287
from mastapy._internal.python_net import python_net_import

_SHORT_LENGTH_RANGE = python_net_import('SMT.MastaAPI.MathUtility.MeasuredRanges', 'ShortLengthRange')


__docformat__ = 'restructuredtext en'
__all__ = ('ShortLengthRange',)


class ShortLengthRange(_1287.Range):
    '''ShortLengthRange

    This is a mastapy class.
    '''

    TYPE = _SHORT_LENGTH_RANGE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShortLengthRange.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum(self) -> 'float':
        '''float: 'Minimum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Minimum

    @property
    def maximum(self) -> 'float':
        '''float: 'Maximum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Maximum
