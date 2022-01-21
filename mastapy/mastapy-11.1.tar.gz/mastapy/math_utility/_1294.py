'''_1294.py

ComplexVector
'''


from mastapy.math_utility import _1292
from mastapy._internal.python_net import python_net_import

_COMPLEX_VECTOR = python_net_import('SMT.MastaAPI.MathUtility', 'ComplexVector')


__docformat__ = 'restructuredtext en'
__all__ = ('ComplexVector',)


class ComplexVector(_1292.ComplexMatrix):
    '''ComplexVector

    This is a mastapy class.
    '''

    TYPE = _COMPLEX_VECTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComplexVector.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
