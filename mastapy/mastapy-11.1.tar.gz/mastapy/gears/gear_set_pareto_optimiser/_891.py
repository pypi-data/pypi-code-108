'''_891.py

ParetoHypoidGearSetOptimisationStrategyDatabase
'''


from mastapy.gears.gear_set_pareto_optimiser import _883
from mastapy._internal.python_net import python_net_import

_PARETO_HYPOID_GEAR_SET_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoHypoidGearSetOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoHypoidGearSetOptimisationStrategyDatabase',)


class ParetoHypoidGearSetOptimisationStrategyDatabase(_883.ParetoConicalRatingOptimisationStrategyDatabase):
    '''ParetoHypoidGearSetOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_HYPOID_GEAR_SET_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoHypoidGearSetOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
