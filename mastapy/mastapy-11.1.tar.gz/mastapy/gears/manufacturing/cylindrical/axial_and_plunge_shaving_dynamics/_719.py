'''_719.py

PlungeShavingDynamicsCalculationForHobbedGears
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _728, _715
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'PlungeShavingDynamicsCalculationForHobbedGears')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShavingDynamicsCalculationForHobbedGears',)


class PlungeShavingDynamicsCalculationForHobbedGears(_728.ShavingDynamicsCalculationForHobbedGears['_715.PlungeShaverDynamics']):
    '''PlungeShavingDynamicsCalculationForHobbedGears

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShavingDynamicsCalculationForHobbedGears.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
