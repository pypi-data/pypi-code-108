'''_1307.py

Eigenmodes
'''


from typing import List

from mastapy.math_utility import _1306
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_EIGENMODES = python_net_import('SMT.MastaAPI.MathUtility', 'Eigenmodes')


__docformat__ = 'restructuredtext en'
__all__ = ('Eigenmodes',)


class Eigenmodes(_0.APIBase):
    '''Eigenmodes

    This is a mastapy class.
    '''

    TYPE = _EIGENMODES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Eigenmodes.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def items(self) -> 'List[_1306.Eigenmode]':
        '''List[Eigenmode]: 'Items' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Items, constructor.new(_1306.Eigenmode))
        return value
