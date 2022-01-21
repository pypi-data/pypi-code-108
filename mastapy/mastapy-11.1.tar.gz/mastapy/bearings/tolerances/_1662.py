'''_1662.py

InnerRingTolerance
'''


from mastapy.bearings.tolerances import _1673
from mastapy._internal.python_net import python_net_import

_INNER_RING_TOLERANCE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'InnerRingTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('InnerRingTolerance',)


class InnerRingTolerance(_1673.RingTolerance):
    '''InnerRingTolerance

    This is a mastapy class.
    '''

    TYPE = _INNER_RING_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InnerRingTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
