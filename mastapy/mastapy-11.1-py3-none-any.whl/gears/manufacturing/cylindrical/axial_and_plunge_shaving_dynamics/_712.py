'''_712.py

ConventionalShavingDynamicsCalculationForDesignedGears
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _727, _711
from mastapy._internal.python_net import python_net_import

_CONVENTIONAL_SHAVING_DYNAMICS_CALCULATION_FOR_DESIGNED_GEARS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'ConventionalShavingDynamicsCalculationForDesignedGears')


__docformat__ = 'restructuredtext en'
__all__ = ('ConventionalShavingDynamicsCalculationForDesignedGears',)


class ConventionalShavingDynamicsCalculationForDesignedGears(_727.ShavingDynamicsCalculationForDesignedGears['_711.ConventionalShavingDynamics']):
    '''ConventionalShavingDynamicsCalculationForDesignedGears

    This is a mastapy class.
    '''

    TYPE = _CONVENTIONAL_SHAVING_DYNAMICS_CALCULATION_FOR_DESIGNED_GEARS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConventionalShavingDynamicsCalculationForDesignedGears.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
