'''_1327.py

RoundedOrder
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ROUNDED_ORDER = python_net_import('SMT.MastaAPI.MathUtility', 'RoundedOrder')


__docformat__ = 'restructuredtext en'
__all__ = ('RoundedOrder',)


class RoundedOrder(_0.APIBase):
    '''RoundedOrder

    This is a mastapy class.
    '''

    TYPE = _ROUNDED_ORDER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RoundedOrder.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
