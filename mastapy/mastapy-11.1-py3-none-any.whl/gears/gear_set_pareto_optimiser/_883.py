'''_883.py

ParetoConicalRatingOptimisationStrategyDatabase
'''


from mastapy.math_utility.optimisation import _1351
from mastapy._internal.python_net import python_net_import

_PARETO_CONICAL_RATING_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoConicalRatingOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoConicalRatingOptimisationStrategyDatabase',)


class ParetoConicalRatingOptimisationStrategyDatabase(_1351.ParetoOptimisationStrategyDatabase):
    '''ParetoConicalRatingOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_CONICAL_RATING_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoConicalRatingOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
