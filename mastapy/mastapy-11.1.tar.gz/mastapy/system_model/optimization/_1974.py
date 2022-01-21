'''_1974.py

CylindricalGearOptimisationStrategy
'''


from mastapy.system_model.optimization import _1980, _1975
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_OPTIMISATION_STRATEGY = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'CylindricalGearOptimisationStrategy')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearOptimisationStrategy',)


class CylindricalGearOptimisationStrategy(_1980.OptimizationStrategy['_1975.CylindricalGearOptimizationStep']):
    '''CylindricalGearOptimisationStrategy

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_OPTIMISATION_STRATEGY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearOptimisationStrategy.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
