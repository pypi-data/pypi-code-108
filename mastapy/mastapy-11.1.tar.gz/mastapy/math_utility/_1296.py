'''_1296.py

ComplexVector6D
'''


from mastapy.math_utility import _1294
from mastapy._internal.python_net import python_net_import

_COMPLEX_VECTOR_6D = python_net_import('SMT.MastaAPI.MathUtility', 'ComplexVector6D')


__docformat__ = 'restructuredtext en'
__all__ = ('ComplexVector6D',)


class ComplexVector6D(_1294.ComplexVector):
    '''ComplexVector6D

    This is a mastapy class.
    '''

    TYPE = _COMPLEX_VECTOR_6D

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComplexVector6D.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
