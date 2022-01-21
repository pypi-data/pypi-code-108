'''_713.py

ConventionalShavingDynamicsCalculationForHobbedGears
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _728, _711
from mastapy._internal.python_net import python_net_import

_CONVENTIONAL_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'ConventionalShavingDynamicsCalculationForHobbedGears')


__docformat__ = 'restructuredtext en'
__all__ = ('ConventionalShavingDynamicsCalculationForHobbedGears',)


class ConventionalShavingDynamicsCalculationForHobbedGears(_728.ShavingDynamicsCalculationForHobbedGears['_711.ConventionalShavingDynamics']):
    '''ConventionalShavingDynamicsCalculationForHobbedGears

    This is a mastapy class.
    '''

    TYPE = _CONVENTIONAL_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConventionalShavingDynamicsCalculationForHobbedGears.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
