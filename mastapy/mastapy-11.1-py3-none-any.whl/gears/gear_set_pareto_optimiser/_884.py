'''_884.py

ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase
'''


from mastapy.gears.gear_set_pareto_optimiser import _886
from mastapy._internal.python_net import python_net_import

_PARETO_CYLINDRICAL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase',)


class ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase(_886.ParetoCylindricalRatingOptimisationStrategyDatabase):
    '''ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _PARETO_CYLINDRICAL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
