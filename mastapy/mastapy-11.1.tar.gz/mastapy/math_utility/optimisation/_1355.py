'''_1355.py

ReportingOptimizationInput
'''


from mastapy.math_utility.optimisation import _1343
from mastapy._internal.python_net import python_net_import

_REPORTING_OPTIMIZATION_INPUT = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'ReportingOptimizationInput')


__docformat__ = 'restructuredtext en'
__all__ = ('ReportingOptimizationInput',)


class ReportingOptimizationInput(_1343.OptimizationInput):
    '''ReportingOptimizationInput

    This is a mastapy class.
    '''

    TYPE = _REPORTING_OPTIMIZATION_INPUT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ReportingOptimizationInput.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
