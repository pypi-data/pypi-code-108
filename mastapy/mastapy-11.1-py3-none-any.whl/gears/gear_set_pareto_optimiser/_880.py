'''_880.py

MicroGeometryGearSetDesignSpaceSearchStrategyDatabase
'''


from mastapy.math_utility.optimisation import _1340
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_GEAR_SET_DESIGN_SPACE_SEARCH_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'MicroGeometryGearSetDesignSpaceSearchStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryGearSetDesignSpaceSearchStrategyDatabase',)


class MicroGeometryGearSetDesignSpaceSearchStrategyDatabase(_1340.MicroGeometryDesignSpaceSearchStrategyDatabase):
    '''MicroGeometryGearSetDesignSpaceSearchStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_GEAR_SET_DESIGN_SPACE_SEARCH_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryGearSetDesignSpaceSearchStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
