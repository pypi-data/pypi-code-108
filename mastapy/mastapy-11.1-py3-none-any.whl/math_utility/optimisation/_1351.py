'''_1351.py

ParetoOptimisationStrategyDatabase
'''


from mastapy.math_utility.optimisation import _1338
from mastapy._internal.python_net import python_net_import

_PARETO_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'ParetoOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoOptimisationStrategyDatabase',)


class ParetoOptimisationStrategyDatabase(_1338.DesignSpaceSearchStrategyDatabase):
    '''ParetoOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
