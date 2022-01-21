'''_1292.py

ComplexMatrix
'''


from mastapy.math_utility import _1313
from mastapy._internal.python_net import python_net_import

_COMPLEX_MATRIX = python_net_import('SMT.MastaAPI.MathUtility', 'ComplexMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('ComplexMatrix',)


class ComplexMatrix(_1313.GenericMatrix['complex', 'ComplexMatrix']):
    '''ComplexMatrix

    This is a mastapy class.
    '''

    TYPE = _COMPLEX_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComplexMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
