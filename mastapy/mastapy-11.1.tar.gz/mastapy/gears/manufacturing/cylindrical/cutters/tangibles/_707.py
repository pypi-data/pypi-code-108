'''_707.py

NamedPoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_POINT = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters.Tangibles', 'NamedPoint')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedPoint',)


class NamedPoint(_0.APIBase):
    '''NamedPoint

    This is a mastapy class.
    '''

    TYPE = _NAMED_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedPoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x(self) -> 'float':
        '''float: 'X' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.X

    @property
    def y(self) -> 'float':
        '''float: 'Y' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Y
