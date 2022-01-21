'''_1329.py

SquareMatrix
'''


from mastapy.math_utility import _1323
from mastapy._internal.python_net import python_net_import

_SQUARE_MATRIX = python_net_import('SMT.MastaAPI.MathUtility', 'SquareMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('SquareMatrix',)


class SquareMatrix(_1323.RealMatrix):
    '''SquareMatrix

    This is a mastapy class.
    '''

    TYPE = _SQUARE_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SquareMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
