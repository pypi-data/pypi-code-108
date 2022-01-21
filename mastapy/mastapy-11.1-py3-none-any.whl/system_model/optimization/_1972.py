'''_1972.py

ConicalGearOptimizationStep
'''


from mastapy.system_model.optimization import _1979
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_OPTIMIZATION_STEP = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'ConicalGearOptimizationStep')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearOptimizationStep',)


class ConicalGearOptimizationStep(_1979.OptimizationStep):
    '''ConicalGearOptimizationStep

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_OPTIMIZATION_STEP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearOptimizationStep.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
