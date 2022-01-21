'''_887.py

ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase
'''


from mastapy.gears.gear_set_pareto_optimiser import _889
from mastapy._internal.python_net import python_net_import

_PARETO_FACE_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase',)


class ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase(_889.ParetoFaceRatingOptimisationStrategyDatabase):
    '''ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_FACE_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
