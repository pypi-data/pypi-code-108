'''_1343.py

OptimizationInput
'''


from mastapy.math_utility.optimisation import _1344
from mastapy._internal.python_net import python_net_import

_OPTIMIZATION_INPUT = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'OptimizationInput')


__docformat__ = 'restructuredtext en'
__all__ = ('OptimizationInput',)


class OptimizationInput(_1344.OptimizationVariable):
    '''OptimizationInput

    This is a mastapy class.
    '''

    TYPE = _OPTIMIZATION_INPUT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptimizationInput.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
