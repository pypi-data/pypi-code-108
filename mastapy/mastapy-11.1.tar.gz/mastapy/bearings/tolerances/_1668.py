'''_1668.py

OuterRingTolerance
'''


from mastapy.bearings.tolerances import _1673
from mastapy._internal.python_net import python_net_import

_OUTER_RING_TOLERANCE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'OuterRingTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('OuterRingTolerance',)


class OuterRingTolerance(_1673.RingTolerance):
    '''OuterRingTolerance

    This is a mastapy class.
    '''

    TYPE = _OUTER_RING_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OuterRingTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
