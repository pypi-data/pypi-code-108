'''_1322.py

Quaternion
'''


from mastapy.math_utility import _1324
from mastapy._internal.python_net import python_net_import

_QUATERNION = python_net_import('SMT.MastaAPI.MathUtility', 'Quaternion')


__docformat__ = 'restructuredtext en'
__all__ = ('Quaternion',)


class Quaternion(_1324.RealVector):
    '''Quaternion

    This is a mastapy class.
    '''

    TYPE = _QUATERNION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Quaternion.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
