'''_711.py

ConventionalShavingDynamics
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _725
from mastapy._internal.python_net import python_net_import

_CONVENTIONAL_SHAVING_DYNAMICS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'ConventionalShavingDynamics')


__docformat__ = 'restructuredtext en'
__all__ = ('ConventionalShavingDynamics',)


class ConventionalShavingDynamics(_725.ShavingDynamics):
    '''ConventionalShavingDynamics

    This is a mastapy class.
    '''

    TYPE = _CONVENTIONAL_SHAVING_DYNAMICS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConventionalShavingDynamics.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
