'''_31.py

ShaftProfilePointCopy
'''


from mastapy.shafts import _30
from mastapy._internal.python_net import python_net_import

_SHAFT_PROFILE_POINT_COPY = python_net_import('SMT.MastaAPI.Shafts', 'ShaftProfilePointCopy')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftProfilePointCopy',)


class ShaftProfilePointCopy(_30.ShaftProfilePoint):
    '''ShaftProfilePointCopy

    This is a mastapy class.
    '''

    TYPE = _SHAFT_PROFILE_POINT_COPY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftProfilePointCopy.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
