'''_1323.py

RealMatrix
'''


from mastapy.math_utility import _1313
from mastapy._internal.python_net import python_net_import

_REAL_MATRIX = python_net_import('SMT.MastaAPI.MathUtility', 'RealMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('RealMatrix',)


class RealMatrix(_1313.GenericMatrix['float', 'RealMatrix']):
    '''RealMatrix

    This is a mastapy class.
    '''

    TYPE = _REAL_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RealMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
