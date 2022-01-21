'''_1981.py

OptimizationStrategyBase
'''


from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_OPTIMIZATION_STRATEGY_BASE = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'OptimizationStrategyBase')


__docformat__ = 'restructuredtext en'
__all__ = ('OptimizationStrategyBase',)


class OptimizationStrategyBase(_1597.NamedDatabaseItem):
    '''OptimizationStrategyBase

    This is a mastapy class.
    '''

    TYPE = _OPTIMIZATION_STRATEGY_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptimizationStrategyBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
