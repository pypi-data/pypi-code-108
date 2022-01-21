'''_1371.py

ConvergenceLogger
'''


from mastapy.math_utility.convergence import _1372
from mastapy._internal.python_net import python_net_import

_CONVERGENCE_LOGGER = python_net_import('SMT.MastaAPI.MathUtility.Convergence', 'ConvergenceLogger')


__docformat__ = 'restructuredtext en'
__all__ = ('ConvergenceLogger',)


class ConvergenceLogger(_1372.DataLogger):
    '''ConvergenceLogger

    This is a mastapy class.
    '''

    TYPE = _CONVERGENCE_LOGGER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConvergenceLogger.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
