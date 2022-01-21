'''_1334.py

Vector6D
'''


from mastapy.math_utility import _1324
from mastapy._internal.python_net import python_net_import

_VECTOR_6D = python_net_import('SMT.MastaAPI.MathUtility', 'Vector6D')


__docformat__ = 'restructuredtext en'
__all__ = ('Vector6D',)


class Vector6D(_1324.RealVector):
    '''Vector6D

    This is a mastapy class.
    '''

    TYPE = _VECTOR_6D

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Vector6D.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
