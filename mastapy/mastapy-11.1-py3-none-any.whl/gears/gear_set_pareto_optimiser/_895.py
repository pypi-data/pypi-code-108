'''_895.py

ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase
'''


from mastapy.gears.gear_set_pareto_optimiser import _883
from mastapy._internal.python_net import python_net_import

_PARETO_STRAIGHT_BEVEL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase',)


class ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase(_883.ParetoConicalRatingOptimisationStrategyDatabase):
    '''ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_STRAIGHT_BEVEL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
