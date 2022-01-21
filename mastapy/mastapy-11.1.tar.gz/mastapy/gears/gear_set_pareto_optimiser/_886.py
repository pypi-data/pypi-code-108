'''_886.py

ParetoCylindricalRatingOptimisationStrategyDatabase
'''


from mastapy.math_utility.optimisation import _1351
from mastapy._internal.python_net import python_net_import

_PARETO_CYLINDRICAL_RATING_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoCylindricalRatingOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoCylindricalRatingOptimisationStrategyDatabase',)


class ParetoCylindricalRatingOptimisationStrategyDatabase(_1351.ParetoOptimisationStrategyDatabase):
    '''ParetoCylindricalRatingOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_CYLINDRICAL_RATING_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoCylindricalRatingOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
