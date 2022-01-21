'''_718.py

PlungeShavingDynamicsCalculationForDesignedGears
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _727, _715
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_DESIGNED_GEARS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'PlungeShavingDynamicsCalculationForDesignedGears')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShavingDynamicsCalculationForDesignedGears',)


class PlungeShavingDynamicsCalculationForDesignedGears(_727.ShavingDynamicsCalculationForDesignedGears['_715.PlungeShaverDynamics']):
    '''PlungeShavingDynamicsCalculationForDesignedGears

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_DESIGNED_GEARS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShavingDynamicsCalculationForDesignedGears.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
