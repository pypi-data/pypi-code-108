'''_224.py

FatigueSafetyFactorItemBase
'''


from mastapy.materials import _248
from mastapy._internal.python_net import python_net_import

_FATIGUE_SAFETY_FACTOR_ITEM_BASE = python_net_import('SMT.MastaAPI.Materials', 'FatigueSafetyFactorItemBase')


__docformat__ = 'restructuredtext en'
__all__ = ('FatigueSafetyFactorItemBase',)


class FatigueSafetyFactorItemBase(_248.SafetyFactorItem):
    '''FatigueSafetyFactorItemBase

    This is a mastapy class.
    '''

    TYPE = _FATIGUE_SAFETY_FACTOR_ITEM_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FatigueSafetyFactorItemBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
