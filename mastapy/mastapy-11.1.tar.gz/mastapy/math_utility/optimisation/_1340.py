'''_1340.py

MicroGeometryDesignSpaceSearchStrategyDatabase
'''


from mastapy.math_utility.optimisation import _1338
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_DESIGN_SPACE_SEARCH_STRATEGY_DATABASE = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'MicroGeometryDesignSpaceSearchStrategyDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryDesignSpaceSearchStrategyDatabase',)


class MicroGeometryDesignSpaceSearchStrategyDatabase(_1338.DesignSpaceSearchStrategyDatabase):
    '''MicroGeometryDesignSpaceSearchStrategyDatabase

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_DESIGN_SPACE_SEARCH_STRATEGY_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryDesignSpaceSearchStrategyDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
