'''_896.py

ParetoStraightBevelGearSetOptimisationStrategyDatabase
'''


from mastapy.gears.gear_set_pareto_optimiser import _883
from mastapy._internal.python_net import python_net_import

_PARETO_STRAIGHT_BEVEL_GEAR_SET_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoStraightBevelGearSetOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoStraightBevelGearSetOptimisationStrategyDatabase',)


class ParetoStraightBevelGearSetOptimisationStrategyDatabase(_883.ParetoConicalRatingOptimisationStrategyDatabase):
    '''ParetoStraightBevelGearSetOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_STRAIGHT_BEVEL_GEAR_SET_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoStraightBevelGearSetOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
