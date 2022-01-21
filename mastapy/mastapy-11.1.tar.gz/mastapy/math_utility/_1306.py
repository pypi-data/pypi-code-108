'''_1306.py

Eigenmode
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_EIGENMODE = python_net_import('SMT.MastaAPI.MathUtility', 'Eigenmode')


__docformat__ = 'restructuredtext en'
__all__ = ('Eigenmode',)


class Eigenmode(_0.APIBase):
    '''Eigenmode

    This is a mastapy class.
    '''

    TYPE = _EIGENMODE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Eigenmode.TYPE'):
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
    def frequency(self) -> 'float':
        '''float: 'Frequency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Frequency
